import { Rule } from 'eslint';
import { Node, CallExpression, Identifier, IfStatement, MemberExpression, AssignmentExpression, ImportDeclaration } from 'estree';

const UNSAFE_PATTERNS = {
  deserializationFuncs: [
    'pickle.loads',
    'yaml.load',
    'yaml.safe_load',
    'json.loads',
    'marshal.loads',
    'ast.literal_eval',
    'eval',
    'exec',
  ] as const,
  safeAlternatives: {
    'pickle.loads': 'dill.loads with whitelist',
    'yaml.load': 'yaml.safe_load',
    'json.loads': 'json.loads with custom decoder',
    'marshal.loads': 'json.loads',
    'ast.literal_eval': 'ast.literal_eval with type checking',
    'eval': 'ast.literal_eval',
    'exec': 'subprocess.run with restrictions',
  },
  securityChecks: [
    'isinstance',
    'type',
    'hasattr',
    'issubclass',
  ],
} as const;

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Prevent unsafe deserialization of untrusted data',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      unsafeDeserialization: 'Unsafe deserialization detected: {{func}}. Use {{alternative}} instead.',
      missingTypeCheck: 'Deserialization without type checking is unsafe',
      untrustedInput: 'Deserializing potentially untrusted input',
      useCustomDecoder: 'Use a custom decoder with strict type checking',
      requireWhitelist: 'Implement a whitelist for allowed types',
    },
  },

  create(context) {
    const checkDeserializationCall = (node: CallExpression) => {
      const calleeText = context.getSourceCode().getText(node.callee);

      // Check for unsafe deserialization functions
      for (const func of UNSAFE_PATTERNS.deserializationFuncs) {
        if (calleeText.includes(func)) {
          const alternative = UNSAFE_PATTERNS.safeAlternatives[func] || 'a safe alternative';
          context.report({
            node,
            messageId: 'unsafeDeserialization',
            data: {
              func,
              alternative
            },
          });
        }
      }

      // Check for type checking before deserialization
      let hasTypeCheck = false;
      const ancestors = context.getAncestors();

      for (const ancestor of ancestors) {
        if (ancestor.type === 'IfStatement') {
          const testText = context.getSourceCode().getText((ancestor as IfStatement).test);
          for (const check of UNSAFE_PATTERNS.securityChecks) {
            if (testText.includes(check)) {
              hasTypeCheck = true;
              break;
            }
          }
        }
      }

      if (!hasTypeCheck && calleeText.includes('loads')) {
        context.report({
          node,
          messageId: 'missingTypeCheck',
        });
      }
    };

    const checkCustomDecoder = (node: Node) => {
      if (
        node.type === 'CallExpression' &&
        node.callee.type === 'MemberExpression'
      ) {
        const memberExpression = node.callee as MemberExpression;
        if (memberExpression.property.type === 'Identifier' && memberExpression.property.name === 'loads') {
          const callExpression = node as CallExpression;
          const hasCustomDecoder = callExpression.arguments.length > 1 &&
            callExpression.arguments[1].type === 'Identifier';

          if (!hasCustomDecoder) {
            context.report({
              node,
              messageId: 'useCustomDecoder'
            });
          }
        }
      }
    };

    return {
      CallExpression(node) {
        checkDeserializationCall(node);
        checkCustomDecoder(node);
      },

      // Check variable assignments for potential deserialization
      AssignmentExpression(node: AssignmentExpression) {
        if (
          node.right.type === 'CallExpression' &&
          node.right.callee.type === 'Identifier'
        ) {
          const funcName = (node.right.callee as Identifier).name;
          if (funcName.toLowerCase().includes('load') || funcName.toLowerCase().includes('parse')) {
            context.report({
              node,
              messageId: 'untrustedInput',
            });
          }
        }
      },

      // Check imports for unsafe modules
      ImportDeclaration(node: ImportDeclaration) {
        const importSource = context.getSourceCode().getText(node.source);
        if (importSource.includes('pickle') || importSource.includes('marshal')) {
          context.report({
            node,
            messageId: 'requireWhitelist',
          });
        }
      },
    };
  },
};

export default rule;
