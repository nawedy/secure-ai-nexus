import { Rule } from 'eslint';
import { Node, CallExpression, Identifier } from 'estree';

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


  
} as const;

const UNSAFE_PATTERNS = {
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
};

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


      const safeAlternatives = UNSAFE_PATTERNS.safeAlternatives as Record<string, string>;

      // Check for unsafe deserialization functions
      for (const func of UNSAFE_PATTERNS.deserializationFuncs) {
          if (calleeText.includes(func)) {
            const alternative = safeAlternatives[func] || 'a safe alternative';
           context.report({
             node,
             messageId: 'unsafeDeserialization',
             data: {
               func,
               alternative:alternative
            },
          });
        }
      });

      // Check for type checking before deserialization
      let hasTypeCheck = false;
      context.getAncestors().forEach(ancestor => {
        if (ancestor.type === 'IfStatement') {
          const testText = context.getSourceCode().getText(ancestor.test);
          UNSAFE_PATTERNS.securityChecks.forEach(check => {
            if (testText.includes(check)) {
              hasTypeCheck = true;
            }
          });
        }
      });

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
        node.callee.type === 'MemberExpression' &&
        node.callee.property.type === 'Identifier' &&
        node.callee.property.name === 'loads'
      ) {
        const hasCustomDecoder = node.arguments.length > 1 &&
          node.arguments[1].type === 'Identifier';

        if (!hasCustomDecoder) {
          context.report({
            node,
            messageId: 'useCustomDecoder',
          });
        }
      }
    };

    return {
      CallExpression(node) {
        checkDeserializationCall(node);
        checkCustomDecoder(node);
      },

      // Check variable assignments for potential deserialization
      AssignmentExpression(node) {
        if (
          node.right.type === 'CallExpression' &&
          node.right.callee.type === 'Identifier'
        ) {
          const funcName = node.right.callee.name;
          if (funcName.toLowerCase().includes('load') || funcName.toLowerCase().includes('parse')) {
            context.report({
              node,
              messageId: 'untrustedInput',
            });
          }
        }
      },

      // Check imports for unsafe modules
      ImportDeclaration(node) {
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
