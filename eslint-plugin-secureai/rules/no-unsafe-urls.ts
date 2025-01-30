import { Rule } from 'eslint';
import { Node, CallExpression } from 'estree';

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow unsafe URL construction and usage',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      unsafeUrl: 'Unsafe URL construction detected. Use URL sanitization.',
      directUrlUsage: 'Direct URL usage without validation is unsafe.',
    },
  },

  create(context) {
    return {
      // Check URL construction
      NewExpression(node) {
        if (node.callee.type === 'Identifier' && node.callee.name === 'URL') {
          const urlArg = node.arguments[0];
          if (urlArg.type === 'Literal' && typeof urlArg.value === 'string') {
            if (!urlArg.value.startsWith('https://')) {
              context.report({
                node,
                messageId: 'unsafeUrl',
              });
            }
          }
        }
      },

      // Check fetch calls
      CallExpression(node: Node) {
        const callExpr = node as CallExpression;
        if (
          callExpr.callee.type === 'Identifier' &&
          callExpr.callee.name === 'fetch'
        ) {
          const urlArg = callExpr.arguments[0];
          if (urlArg.type === 'Literal' && typeof urlArg.value === 'string') {
            if (!urlArg.value.startsWith('https://')) {
              context.report({
                node,
                messageId: 'unsafeUrl',
              });
            }
          } else if (urlArg.type === 'Identifier') {
            context.report({
              node,
              messageId: 'directUrlUsage',
            });
          }
        }
      },
    };
  },
};

export default rule;
