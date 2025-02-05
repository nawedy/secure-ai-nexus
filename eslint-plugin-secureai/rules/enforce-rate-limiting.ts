import { Rule } from 'eslint';
import { Node, CallExpression, Identifier, ImportDeclaration, ObjectExpression, Property } from 'estree';

const RATE_LIMIT_PATTERNS = {
  pythonLibraries: {
    recommended: [
      'fastapi.middleware.ratelimit',
      'starlette.middleware.ratelimit',
      'flask_limiter',
      'django-ratelimit',
      'aiohttp_ratelimit',
      'redis-ratelimit',
    ],
    configurations: {
      'fastapi': {
        minDelay: '50',  // ms
        maxRequests: '100',
        perWindow: '60', // seconds
        burstSize: 5,
      },
      'flask': {
        defaultLimits: ['100 per minute', '5000 per hour'],
        storageUri: 'redis://localhost:6379/0',
      },
      'django': {
        cacheName: 'default',
        timeout: 60 * 15,  // 15 minutes
      },
    },
  },
  endpoints: {
    auth: {
      login: { maxAttempts: 5, window: 300 },    // 5 attempts per 5 minutes
      register: { maxAttempts: 3, window: 3600 }, // 3 attempts per hour
      reset: { maxAttempts: 2, window: 3600 },    // 2 attempts per hour
    },
    api: {
      standard: { maxRequests: 1000, window: 3600 },  // 1000 requests per hour
      premium: { maxRequests: 10000, window: 3600 },  // 10000 requests per hour
    },
  },
  securityHeaders: [
    'X-RateLimit-Limit',
    'X-RateLimit-Remaining',
    'X-RateLimit-Reset',
    'Retry-After',
  ],
};

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce rate limiting on endpoints and APIs',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      missingRateLimit: 'Endpoint missing rate limiting: {{endpoint}}',
      insufficientLimit: 'Rate limit too permissive: {{current}} requests, recommended: {{recommended}}',
      missingHeaders: 'Rate limit headers not properly implemented',
      unsafeStorage: 'Use distributed rate limit storage (e.g., Redis) for production',
      missingFallback: 'Implement fallback mechanism for rate limiter failure',
      noGlobalLimit: 'Global rate limiting not configured',
      insecureWindow: 'Rate limit window too large: {{window}} seconds',
    },
  },

  create(context) {
    let hasGlobalRateLimit = false;
    let hasDistributedStorage = false;
    let hasFallbackMechanism = false;

    const checkRateLimitConfig = (node: ObjectExpression) => {
      node.properties.forEach(prop => {
        if (prop.type === 'Property' && prop.key.type === 'Identifier') {
          // Check rate limit values
          if (prop.key.name === 'maxRequests' && prop.value.type === 'Literal') {
            if (typeof prop.value.value === 'number') {
              const maxRequests: number = prop.value.value;
              if (maxRequests > RATE_LIMIT_PATTERNS.endpoints.api.standard.maxRequests) {
                context.report({
                  node: prop,
                  messageId: 'insufficientLimit',
                  data: {
                    current: maxRequests,
                    recommended: RATE_LIMIT_PATTERNS.endpoints.api.standard.maxRequests,
                  },
                });
              }
            }
          }

          // Check window size
          if (prop.key.name === 'window' && prop.value.type === 'Literal') {
            if (typeof prop.value.value === 'number') {
              const windowValue = prop.value.value;
              if (windowValue > 3600) {
                context.report({
                  node: prop,
                  messageId: 'insecureWindow',
                  data: { window: windowValue },
                });
              }
            }
          }
        }
      });
    };

    const checkEndpointSecurity = (node: Node) => {
      const decorators = context.getSourceCode().getCommentsBefore(node);
      let hasRateLimit = false;

      decorators.forEach(decorator => {
        if (
          decorator.value.includes('@rate_limit') ||
          decorator.value.includes('@ratelimit') ||
          decorator.value.includes('@limiter')
        ) {
          hasRateLimit = true;
        }
      });

      if (!hasRateLimit) {
        context.report({
          node,
          messageId: 'missingRateLimit',
          data: {
            endpoint: context.getSourceCode().getText(node),
          },
        });
      }
    };

    const checkStorageBackend = (node: ImportDeclaration) => {
      const importSource = context.getSourceCode().getText(node.source);
      if (
        importSource.includes('redis') || importSource.includes('memcached')
      ) {
        hasDistributedStorage = true;
      }
    };

    return {
      // Check rate limit imports and configuration
      ImportDeclaration(node) {
        const importSource = context.getSourceCode().getText(node.source);
        RATE_LIMIT_PATTERNS.pythonLibraries.recommended.forEach((lib) => {
          if (importSource.includes(lib)) {
            hasGlobalRateLimit = true;
          }
        });
        checkStorageBackend(node);
      },

      // Check endpoint decorators
      FunctionDeclaration(node) {
        if (node.id && (
          node.id.name.toLowerCase().includes('handler') ||
          node.id.name.toLowerCase().includes('endpoint') ||
          node.id.name.toLowerCase().includes('route')
        )) {
          checkEndpointSecurity(node);
        }
      },

      // Check rate limit configuration
      ObjectExpression(node) {
        checkRateLimitConfig(node);
      },

      // Check for fallback mechanisms
      TryStatement(node) {
        if (context.getSourceCode().getText(node).includes('rate_limit')) {
          hasFallbackMechanism = true;
        }
      },

      // Program exit
      'Program:exit'() {
        if (!hasGlobalRateLimit) {
          context.report({
            node: null,
            messageId: 'noGlobalLimit',
          });
        }
        if (!hasDistributedStorage) {
          context.report({
            node: null,
            messageId: 'unsafeStorage',
          });
        }

        if (!hasFallbackMechanism) {
          context.report({
            node: null,
            messageId: 'missingFallback',
          });
        }
      },
    };
  },
};

export default rule;
