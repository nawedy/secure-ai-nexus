import { Rule } from 'eslint';
import { Node, CallExpression, MemberExpression } from 'estree';

const WEAK_CRYPTO_PATTERNS = {
  algorithms: {
    hash: ['MD5', 'SHA1'],
    cipher: ['DES', 'RC4', '3DES', 'Blowfish'],
    keySize: {
      RSA: 2048,
      EC: 256,
      AES: 128,
    },
  },
  insecureRandomness: ['Math.random', 'crypto.pseudoRandomBytes'],
};

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Prevent usage of weak cryptographic algorithms and practices',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      weakHash: 'Using weak hash algorithm: {{algo}}. Use SHA-256 or stronger.',
      weakCipher: 'Using weak cipher: {{algo}}. Use AES-256-GCM or similar.',
      weakKeySize: 'Key size {{size}} bits for {{algo}} is too weak. Minimum required: {{min}} bits.',
      insecureRandom: 'Using cryptographically insecure random number generator.',
    },
  },

  create(context) {
    const checkCryptoAlgorithm = (node: Node, value: string) => {
      // Check hash algorithms
      const weakHash = WEAK_CRYPTO_PATTERNS.algorithms.hash.find(algo =>
        value.toUpperCase().includes(algo)
      );
      if (weakHash) {
        context.report({
          node,
          messageId: 'weakHash',
          data: { algo: weakHash },
        });
      }

      // Check cipher algorithms
      const weakCipher = WEAK_CRYPTO_PATTERNS.algorithms.cipher.find(algo =>
        value.toUpperCase().includes(algo)
      );
      if (weakCipher) {
        context.report({
          node,
          messageId: 'weakCipher',
          data: { algo: weakCipher },
        });
      }
    };

    const checkKeySize = (node: Node, algorithm: string, size: number) => {
      const minSize = WEAK_CRYPTO_PATTERNS.algorithms.keySize[algorithm];
      if (minSize && size < minSize) {
        context.report({
          node,
          messageId: 'weakKeySize',
          data: {
            size,
            algo: algorithm,
            min: minSize,
          },
        });
      }
    };

    return {
      // Check crypto module usage
      CallExpression(node: Node) {
        const callExpr = node as CallExpression;

        // Check createHash calls
        if (
          callExpr.callee.type === 'MemberExpression' &&
          callExpr.callee.object.type === 'Identifier' &&
          callExpr.callee.object.name === 'crypto' &&
          callExpr.callee.property.type === 'Identifier' &&
          callExpr.callee.property.name === 'createHash'
        ) {
          const [algorithmArg] = callExpr.arguments;
          if (algorithmArg.type === 'Literal' && typeof algorithmArg.value === 'string') {
            checkCryptoAlgorithm(node, algorithmArg.value);
          }
        }

        // Check createCipheriv calls
        if (
          callExpr.callee.type === 'MemberExpression' &&
          callExpr.callee.object.type === 'Identifier' &&
          callExpr.callee.object.name === 'crypto' &&
          callExpr.callee.property.type === 'Identifier' &&
          callExpr.callee.property.name === 'createCipheriv'
        ) {
          const [algorithmArg] = callExpr.arguments;
          if (algorithmArg.type === 'Literal' && typeof algorithmArg.value === 'string') {
            checkCryptoAlgorithm(node, algorithmArg.value);
          }
        }

        // Check generateKeyPair calls
        if (
          callExpr.callee.type === 'MemberExpression' &&
          callExpr.callee.object.type === 'Identifier' &&
          callExpr.callee.object.name === 'crypto' &&
          callExpr.callee.property.type === 'Identifier' &&
          callExpr.callee.property.name === 'generateKeyPair'
        ) {
          const [algorithmArg, optionsArg] = callExpr.arguments;
          if (
            algorithmArg.type === 'Literal' &&
            typeof algorithmArg.value === 'string' &&
            optionsArg.type === 'ObjectExpression'
          ) {
            const modulusLength = optionsArg.properties.find(
              prop =>
                prop.type === 'Property' &&
                prop.key.type === 'Identifier' &&
                prop.key.name === 'modulusLength'
            );
            if (modulusLength && modulusLength.value.type === 'Literal') {
              checkKeySize(node, algorithmArg.value, modulusLength.value.value as number);
            }
          }
        }
      },

      // Check for insecure randomness
      MemberExpression(node: MemberExpression) {
        const fullPath = context.getSourceCode().getText(node);
        if (WEAK_CRYPTO_PATTERNS.insecureRandomness.includes(fullPath)) {
          context.report({
            node,
            messageId: 'insecureRandom',
          });
        }
      },
    };
  },
};

export default rule;
