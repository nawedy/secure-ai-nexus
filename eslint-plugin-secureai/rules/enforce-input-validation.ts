import { Rule } from 'eslint';
import { Node, CallExpression, ObjectExpression, Property } from 'estree';

const VALIDATION_PATTERNS = {
  pythonValidators: [
    'pydantic',
    'marshmallow',
    'cerberus',
    'voluptuous',
    'jsonschema',
    'dataclasses',
  ],
  requiredValidations: {
    string: ['max_length', 'min_length', 'pattern', 'strip', 'escape'],
    number: ['maximum', 'minimum', 'multiple_of', 'exclusive_maximum'],
    array: ['max_items', 'min_items', 'unique_items', 'contains'],
    object: ['required', 'properties', 'additional_properties'],
  },
  dangerousPatterns: {
    sql: /SELECT|INSERT|UPDATE|DELETE|DROP|UNION/i,
    nosql: /\$where|\$regex|\$ne|\$gt|\$lt/,
    path: /\.\.|\/\/|\\\\|~/,
    command: /exec|eval|system|popen|subprocess|shell/i,
  },
  sanitizationFunctions: {
    python: [
      'escape', 'quote', 'quote_plus', 'urlsafe_b64encode',
      'html.escape', 'shlex.quote', 'markupsafe.escape',
      'bleach.clean', 'validators.url', 'validators.email'
    ],
    common: [
      'sanitize', 'validate', 'escape', 'encode', 'filter',
      'clean', 'normalize', 'strip', 'purify'
    ],
  },
};

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce input validation and sanitization',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      missingValidation: 'Input parameter missing validation: {{param}}',
      missingPydantic: 'Use Pydantic models for request data validation',
      unsafePattern: 'Potentially unsafe pattern detected in input: {{pattern}}',
      missingSanitization: 'Input requires sanitization before use',
      directUserInput: 'Direct use of user input without validation',
      weakValidation: 'Validation too permissive for sensitive operation',
      pythonPreferred: 'Consider using Python validation libraries for stronger type checking',
    },
  },

  create(context) {
    const checkValidationPresence = (node: Node, paramName: string) => {
      let hasValidation = false;
      let hasPythonValidator = false;

      // Check for Python validation libraries
      context.getAncestors().forEach(ancestor => {
        if (ancestor.type === 'ImportDeclaration') {
          const importSource = context.getSourceCode().getText(ancestor.source);
          if (VALIDATION_PATTERNS.pythonValidators.some(v => importSource.includes(v))) {
            hasPythonValidator = true;
          }
        }
      });

      // Check for validation function calls
      context.getAncestors().forEach(ancestor => {
        if (ancestor.type === 'CallExpression') {
          const callExpr = ancestor as CallExpression;
          if (callExpr.callee.type === 'Identifier') {
            const functionName = callExpr.callee.name.toLowerCase();
            if (
              VALIDATION_PATTERNS.sanitizationFunctions.python.some(f =>
                functionName.includes(f.toLowerCase())
              ) ||
              VALIDATION_PATTERNS.sanitizationFunctions.common.some(f =>
                functionName.includes(f.toLowerCase())
              )
            ) {
              hasValidation = true;
            }
          }
        }
      });

      if (!hasValidation && !hasPythonValidator) {
        context.report({
          node,
          messageId: 'missingValidation',
          data: { param: paramName },
        });
      }

      if (!hasPythonValidator) {
        context.report({
          node,
          messageId: 'pythonPreferred',
        });
      }
    };

    const checkForDangerousPatterns = (node: Node, value: string) => {
      Object.entries(VALIDATION_PATTERNS.dangerousPatterns).forEach(([type, pattern]) => {
        if (pattern.test(value)) {
          context.report({
            node,
            messageId: 'unsafePattern',
            data: { pattern: type },
          });
        }
      });
    };

    const checkRequestHandler = (node: Node) => {
      let hasPydanticModel = false;
      let hasValidation = false;

      // Look for Pydantic model usage
      context.getAncestors().forEach(ancestor => {
        if (
          ancestor.type === 'ClassDeclaration' &&
          ancestor.superClass &&
          context.getSourceCode().getText(ancestor.superClass).includes('BaseModel')
        ) {
          hasPydanticModel = true;
        }
      });

      if (!hasPydanticModel) {
        context.report({
          node,
          messageId: 'missingPydantic',
        });
      }

      // Check for validation decorators
      const decorators = context.getSourceCode().getCommentsBefore(node);
      hasValidation = decorators.some(decorator =>
        decorator.value.includes('@validate') ||
        decorator.value.includes('@validated') ||
        decorator.value.includes('@requires_validation')
      );

      if (!hasValidation && !hasPydanticModel) {
        context.report({
          node,
          messageId: 'missingValidation',
          data: { param: 'request data' },
        });
      }
    };

    return {
      // Check function parameters
      FunctionDeclaration(node) {
        node.params.forEach(param => {
          checkValidationPresence(param, context.getSourceCode().getText(param));
        });
      },

      // Check request handlers
      FunctionDeclaration(node) {
        if (
          node.id &&
          (
            node.id.name.toLowerCase().includes('handler') ||
            node.id.name.toLowerCase().includes('endpoint') ||
            node.id.name.toLowerCase().includes('route')
          )
        ) {
          checkRequestHandler(node);
        }
      },

      // Check string literals for dangerous patterns
      Literal(node) {
        if (typeof node.value === 'string') {
          checkForDangerousPatterns(node, node.value);
        }
      },

      // Check variable assignments
      AssignmentExpression(node) {
        if (node.right.type === 'Identifier') {
          const varName = context.getSourceCode().getText(node.right);
          if (
            varName.toLowerCase().includes('input') ||
            varName.toLowerCase().includes('request') ||
            varName.toLowerCase().includes('param')
          ) {
            checkValidationPresence(node, varName);
          }
        }
      },
    };
  },
};

export default rule;
