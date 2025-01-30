import { Rule } from 'eslint';
import { Node, Literal } from 'estree';

const SENSITIVE_PATTERNS = {
  apiKey: /api[_-]?key|api[_-]?secret/i,
  password: /password|passwd|pwd/i,
  token: /token|jwt|bearer/i,
  secret: /secret|private[_-]?key/i,
  credentials: /credentials|auth/i,
};

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Prevent sensitive information exposure in code',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      sensitiveInfo: 'Potential sensitive information detected: {{type}}',
      hardcodedValue: 'Hardcoded sensitive value detected',
    },
  },

  create(context) {
    const checkNode = (node: Node, value: string) => {
      for (const [type, pattern] of Object.entries(SENSITIVE_PATTERNS)) {
        if (pattern.test(value)) {
          context.report({
            node,
            messageId: 'sensitiveInfo',
            data: { type },
          });
        }
      }
    };

    return {
      // Check variable declarations
      VariableDeclarator(node) {
        if (node.id.type === 'Identifier') {
          checkNode(node, node.id.name);
        }
      },

      // Check string literals
      Literal(node: Node) {
        const literal = node as Literal;
        if (typeof literal.value === 'string') {
          // Check for potential hardcoded secrets
          if (
            literal.value.length > 16 &&
            /[A-Za-z0-9+/=]{16,}/.test(literal.value)
          ) {
            context.report({
              node,
              messageId: 'hardcodedValue',
            });
          }
        }
      },

      // Check object properties
      Property(node) {
        if (node.key.type === 'Identifier') {
          checkNode(node, node.key.name);
        }
      },
    };
  },
};

export default rule;
