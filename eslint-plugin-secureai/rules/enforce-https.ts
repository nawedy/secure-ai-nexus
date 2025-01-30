import { Rule } from 'eslint';
import { Node, CallExpression } from 'estree';

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce HTTPS usage for all network requests',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      httpDetected: 'HTTP protocol detected. Use HTTPS instead.',
      insecureProtocol: 'Insecure protocol detected. Use HTTPS.',
    },
  },

  create(context) {
    const checkUrl = (node: Node, url: string) => {
      if (url.startsWith('http://')) {
        context.report({
          node,
          messageId: 'httpDetected',
        });
      } else if (!url.startsWith('https://')) {
        context.report({
          node,
          messageId: 'insecureProtocol',
        });
      }
    };

    return {
      // Check fetch calls
      CallExpression(node: Node) {
        const callExpr = node as CallExpression;
        if (
          callExpr.callee.type === 'Identifier' &&
          callExpr.callee.name === 'fetch'
        ) {
          const urlArg = callExpr.arguments[0];
          if (urlArg.type === 'Literal' && typeof urlArg.value === 'string') {
            checkUrl(node, urlArg.value);
          }
        }
      },

      // Check URL construction
      NewExpression(node) {
        if (node.callee.type === 'Identifier' && node.callee.name === 'URL') {
          const urlArg = node.arguments[0];
          if (urlArg.type === 'Literal' && typeof urlArg.value === 'string') {
            checkUrl(node, urlArg.value);
          }
        }
      },

      // Check string literals containing URLs
      Literal(node) {
        if (typeof node.value === 'string') {
          const urlRegex = /^(http|https|ws|wss):\/\//;
          if (urlRegex.test(node.value)) {
            checkUrl(node, node.value);
          }
        }
      },
    };
  },
};

export default rule;
