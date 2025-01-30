import { Rule } from 'eslint';
import { Node, CallExpression, ObjectExpression, Property } from 'estree';

const JWT_SECURITY_PATTERNS = {
  weakAlgorithms: ['none', 'HS256', 'RS256'],
  recommendedAlgorithms: ['ES384', 'ES512', 'RS384', 'RS512', 'PS512', 'EdDSA'],
  unsafeOptions: {
    expiresIn: 86400, // 24 hours in seconds
    notBefore: 0,
    algorithm: 'HS256',
  },
  requiredClaims: ['exp', 'nbf', 'iat', 'iss', 'sub', 'aud'],
  sensitiveData: [
    'password',
    'secret',
    'token',
    'apiKey',
    'private',
    'credential',
    'ssn',
    'creditCard',
  ],
};

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce secure JWT handling practices',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      weakAlgorithm: 'Using weak JWT signing algorithm: {{algo}}. Use one of: {{recommended}}',
      missingExpiration: 'JWT must include expiration (exp claim)',
      longExpiration: 'JWT expiration time too long. Maximum recommended: 24 hours',
      missingClaim: 'Required JWT claim missing: {{claim}}',
      sensitiveData: 'Avoid storing sensitive data in JWT payload: {{field}}',
      unsafeVerification: 'Unsafe JWT verification options detected',
      noAlgorithm: 'JWT algorithm must be explicitly specified',
      insecureSecret: 'JWT secret/key should be at least 256 bits',
    },
  },

  create(context) {
    const checkJWTOptions = (node: ObjectExpression) => {
      let hasExpiration = false;
      let hasAlgorithm = false;

      node.properties.forEach((prop: Property) => {
        if (prop.type === 'Property' && prop.key.type === 'Identifier') {
          // Check algorithm
          if (prop.key.name === 'algorithm') {
            hasAlgorithm = true;
            if (prop.value.type === 'Literal' && typeof prop.value.value === 'string') {
              const algo = prop.value.value;
              if (JWT_SECURITY_PATTERNS.weakAlgorithms.includes(algo)) {
                context.report({
                  node: prop,
                  messageId: 'weakAlgorithm',
                  data: {
                    algo,
                    recommended: JWT_SECURITY_PATTERNS.recommendedAlgorithms.join(', '),
                  },
                });
              }
            }
          }

          // Check expiration
          if (prop.key.name === 'expiresIn' || prop.key.name === 'exp') {
            hasExpiration = true;
            if (prop.value.type === 'Literal' && typeof prop.value.value === 'number') {
              const expirationTime = prop.value.value;
              if (expirationTime > JWT_SECURITY_PATTERNS.unsafeOptions.expiresIn) {
                context.report({
                  node: prop,
                  messageId: 'longExpiration',
                });
              }
            }
          }

          // Check for sensitive data in payload
          if (JWT_SECURITY_PATTERNS.sensitiveData.some(field =>
            prop.key.name.toLowerCase().includes(field.toLowerCase())
          )) {
            context.report({
              node: prop,
              messageId: 'sensitiveData',
              data: { field: prop.key.name },
            });
          }
        }
      });

      // Report missing required options
      if (!hasExpiration) {
        context.report({
          node,
          messageId: 'missingExpiration',
        });
      }

      if (!hasAlgorithm) {
        context.report({
          node,
          messageId: 'noAlgorithm',
        });
      }
    };

    const checkJWTVerification = (node: CallExpression) => {
      // Check verify options
      const verifyOptions = node.arguments[2];
      if (verifyOptions && verifyOptions.type === 'ObjectExpression') {
        let hasAlgorithmsCheck = false;

        verifyOptions.properties.forEach((prop: Property) => {
          if (
            prop.type === 'Property' &&
            prop.key.type === 'Identifier' &&
            prop.key.name === 'algorithms'
          ) {
            hasAlgorithmsCheck = true;
            if (prop.value.type === 'ArrayExpression') {
              prop.value.elements.forEach(element => {
                if (
                  element.type === 'Literal' &&
                  typeof element.value === 'string' &&
                  JWT_SECURITY_PATTERNS.weakAlgorithms.includes(element.value)
                ) {
                  context.report({
                    node: element,
                    messageId: 'weakAlgorithm',
                    data: {
                      algo: element.value,
                      recommended: JWT_SECURITY_PATTERNS.recommendedAlgorithms.join(', '),
                    },
                  });
                }
              });
            }
          }
        });

        if (!hasAlgorithmsCheck) {
          context.report({
            node: verifyOptions,
            messageId: 'unsafeVerification',
          });
        }
      }
    };

    return {
      // Check JWT sign operations
      CallExpression(node: CallExpression) {
        if (
          node.callee.type === 'MemberExpression' &&
          node.callee.property.type === 'Identifier'
        ) {
          // Check jwt.sign calls
          if (
            node.callee.property.name === 'sign' &&
            node.arguments.length >= 2
          ) {
            const options = node.arguments[2];
            if (options && options.type === 'ObjectExpression') {
              checkJWTOptions(options);
            } else {
              context.report({
                node,
                messageId: 'noAlgorithm',
              });
            }
          }

          // Check jwt.verify calls
          if (
            node.callee.property.name === 'verify' &&
            node.arguments.length >= 2
          ) {
            checkJWTVerification(node);
          }
        }
      },
    };
  },
};

export default rule;
