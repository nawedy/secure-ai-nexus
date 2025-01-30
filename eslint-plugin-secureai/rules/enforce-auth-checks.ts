import { Rule } from 'eslint';
import { Node, CallExpression, FunctionDeclaration, ArrowFunctionExpression } from 'estree';

const AUTH_PATTERNS = {
  authFunctions: [
    'isAuthenticated',
    'checkAuth',
    'requireAuth',
    'verifyToken',
    'validateSession',
    'checkMFA',
    'verifyPermissions',
  ],
  authDecorators: [
    '@Authorized',
    '@RequireAuth',
    '@Protected',
    '@Authenticated',
    '@RequireMFA',
    '@SecurityCheck',
  ],
  authMiddleware: [
    'authMiddleware',
    'requireAuth',
    'authenticate',
    'verifySession',
    'checkPermissions',
    'validateToken',
  ],
  sensitiveOperations: [
    'user',
    'admin',
    'account',
    'profile',
    'password',
    'email',
    'payment',
    'billing',
    'settings',
  ],
};

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce authentication checks in routes and sensitive operations',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      missingAuthCheck: 'Route handler missing authentication check',
      missingAuthDecorator: 'Route handler missing authentication decorator',
      missingAuthMiddleware: 'Route missing authentication middleware',
      sensitiveOperation: 'Sensitive operation requires authentication check',
    },
  },

  create(context) {
    const hasAuthCheck = (node: Node): boolean => {
      let hasAuth = false;

      // Walk the AST to find auth checks
      context.getAncestors().forEach(ancestor => {
        if (ancestor.type === 'CallExpression') {
          const callExpr = ancestor as CallExpression;
          if (
            callExpr.callee.type === 'Identifier' &&
            AUTH_PATTERNS.authFunctions.includes(callExpr.callee.name)
          ) {
            hasAuth = true;
          }
        }
      });

      return hasAuth;
    };

    const hasAuthDecorator = (node: Node): boolean => {
      const decorators = context.getSourceCode().getCommentsBefore(node);
      return decorators.some(decorator =>
        AUTH_PATTERNS.authDecorators.some(pattern =>
          decorator.value.includes(pattern)
        )
      );
    };

    const hasAuthMiddleware = (node: Node): boolean => {
      if (node.type !== 'CallExpression') return false;

      const callExpr = node as CallExpression;
      if (callExpr.arguments.length === 0) return false;

      const middlewareArg = callExpr.arguments[0];
      if (middlewareArg.type !== 'ArrayExpression') return false;

      return middlewareArg.elements.some(element =>
        element.type === 'Identifier' &&
        AUTH_PATTERNS.authMiddleware.includes(element.name)
      );
    };

    const isSensitiveOperation = (node: Node): boolean => {
      const functionName = context.getSourceCode().getText(node).toLowerCase();
      return AUTH_PATTERNS.sensitiveOperations.some(op => functionName.includes(op));
    };

    return {
      // Check route handlers
      FunctionDeclaration(node: FunctionDeclaration) {
        if (node.id && (
          node.id.name.toLowerCase().includes('handler') ||
          node.id.name.toLowerCase().includes('controller') ||
          isSensitiveOperation(node)
        )) {
          if (!hasAuthCheck(node) && !hasAuthDecorator(node)) {
            context.report({
              node,
              messageId: isSensitiveOperation(node) ? 'sensitiveOperation' : 'missingAuthCheck',
            });
          }
        }
      },

      // Check arrow function route handlers
      ArrowFunctionExpression(node: ArrowFunctionExpression) {
        const parent = context.getAncestors().pop();
        if (
          parent &&
          parent.type === 'VariableDeclarator' &&
          parent.id.type === 'Identifier' &&
          (
            parent.id.name.toLowerCase().includes('handler') ||
            parent.id.name.toLowerCase().includes('controller') ||
            isSensitiveOperation(node)
          )
        ) {
          if (!hasAuthCheck(node) && !hasAuthDecorator(node)) {
            context.report({
              node,
              messageId: isSensitiveOperation(node) ? 'sensitiveOperation' : 'missingAuthCheck',
            });
          }
        }
      },

      // Check route definitions
      CallExpression(node: CallExpression) {
        if (
          node.callee.type === 'MemberExpression' &&
          node.callee.property.type === 'Identifier' &&
          ['get', 'post', 'put', 'delete', 'patch'].includes(node.callee.property.name.toLowerCase())
        ) {
          if (!hasAuthMiddleware(node)) {
            // Check if the route path indicates a sensitive operation
            const routePath = node.arguments[0];
            if (
              routePath.type === 'Literal' &&
              typeof routePath.value === 'string' &&
              AUTH_PATTERNS.sensitiveOperations.some(op => routePath.value.includes(op))
            ) {
              context.report({
                node,
                messageId: 'missingAuthMiddleware',
              });
            }
          }
        }
      },
    };
  },
};

export default rule;
