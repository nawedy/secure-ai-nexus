import { Rule } from 'eslint';
import { Node, CallExpression, ObjectExpression, Property, Identifier } from 'estree';

const DATA_SECURITY_PATTERNS = {
  sensitiveData: {
    personal: [
      'ssn', 'social_security', 'dob', 'birth_date', 'address',
      'phone', 'email', 'password', 'secret', 'token',
      'credit_card', 'card_number', 'cvv', 'pin',
    ],
    business: [
      'api_key', 'secret_key', 'private_key', 'auth_token',
      'client_secret', 'access_token', 'refresh_token',
    ],
    health: [
      'medical', 'health', 'diagnosis', 'prescription',
      'treatment', 'patient', 'doctor', 'hospital',
    ],
  },
  pythonSecurityTools: [
    'cryptography',
    'python-dotenv',
    'python-jose',
    'passlib',
    'bcrypt',
    'secrets',
    'maskpass',
  ],
  loggingPatterns: {
    dangerous: [
      'console.log', 'print', 'logger.debug',
      'logging.info', 'sys.stdout.write',
    ],
    safe: [
      'logging.error', 'logger.error', 'logging.critical',
      'logger.exception', 'traceback.format_exc',
    ],
  },
  secureStorageMethods: {
    python: [
      'keyring.set_password',
      'secretstorage.create_item',
      'cryptography.fernet',
      'os.environ.get',
    ],
    common: [
      'encrypt', 'hash', 'secure', 'protect',
      'mask', 'redact', 'sanitize',
    ],
  },
};

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Prevent data leaks and enforce secure data handling',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      sensitiveDataExposure: 'Potential exposure of sensitive data: {{field}}',
      unsafeLogging: 'Unsafe logging of potentially sensitive data',
      missingEncryption: 'Sensitive data should be encrypted before storage/transmission',
      insecureStorage: 'Use secure storage methods for sensitive data',
      pythonSecurityMissing: 'Consider using Python security tools: {{tools}}',
      dataInLogs: 'Avoid logging sensitive data',
      plainTextStorage: 'Storing sensitive data in plain text',
      missingMasking: 'Sensitive data should be masked before display/logging',
    },
  },

  create(context) {
    const checkForSensitiveData = (node: Node, value: string) => {
      Object.entries(DATA_SECURITY_PATTERNS.sensitiveData).forEach(([category, patterns]) => {
        patterns.forEach(pattern => {
          if (value.toLowerCase().includes(pattern.toLowerCase())) {
            context.report({
              node,
              messageId: 'sensitiveDataExposure',
              data: { field: pattern },
            });
          }
        });
      });
    };

    const checkSecureStorage = (node: CallExpression) => {
      let isSecure = false;
      let usesPythonSecurity = false;

      // Check for Python security tools
      context.getAncestors().forEach(ancestor => {
        if (ancestor.type === 'ImportDeclaration') {
          const importSource = context.getSourceCode().getText(ancestor.source);
          if (DATA_SECURITY_PATTERNS.pythonSecurityTools.some(tool =>
            importSource.includes(tool)
          )) {
            usesPythonSecurity = true;
          }
        }
      });

      // Check for secure storage methods
      if (node.callee.type === 'Identifier') {
        const methodName = node.callee.name.toLowerCase();
        isSecure = DATA_SECURITY_PATTERNS.secureStorageMethods.python.some(method =>
          methodName.includes(method.toLowerCase())
        ) || DATA_SECURITY_PATTERNS.secureStorageMethods.common.some(method =>
          methodName.includes(method.toLowerCase())
        );
      }

      if (!isSecure) {
        context.report({
          node,
          messageId: 'insecureStorage',
        });
      }

      if (!usesPythonSecurity) {
        context.report({
          node,
          messageId: 'pythonSecurityMissing',
          data: {
            tools: DATA_SECURITY_PATTERNS.pythonSecurityTools.join(', '),
          },
        });
      }
    };

    const checkLogging = (node: CallExpression) => {
      if (node.callee.type === 'Identifier' || node.callee.type === 'MemberExpression') {
        const callText = context.getSourceCode().getText(node.callee);

        // Check for dangerous logging patterns
        if (DATA_SECURITY_PATTERNS.loggingPatterns.dangerous.some(pattern =>
          callText.includes(pattern)
        )) {
          // Check if any argument contains sensitive data
          node.arguments.forEach(arg => {
            if (arg.type === 'Identifier') {
              checkForSensitiveData(arg, arg.name);
            } else if (arg.type === 'Literal' && typeof arg.value === 'string') {
              checkForSensitiveData(arg, arg.value);
            }
          });
        }
      }
    };

    return {
      // Check variable declarations
      VariableDeclarator(node) {
        if (node.id.type === 'Identifier') {
          checkForSensitiveData(node, node.id.name);
        }
      },

      // Check function parameters
      FunctionDeclaration(node) {
        node.params.forEach(param => {
          if (param.type === 'Identifier') {
            checkForSensitiveData(param, param.name);
          }
        });
      },

      // Check property assignments
      Property(node) {
        if (node.key.type === 'Identifier') {
          checkForSensitiveData(node, node.key.name);
        }
      },

      // Check function calls
      CallExpression(node) {
        checkLogging(node);
        checkSecureStorage(node);
      },

      // Check object properties access
      MemberExpression(node) {
        if (node.property.type === 'Identifier') {
          checkForSensitiveData(node.property, node.property.name);
        }
      },

      // Check string literals
      Literal(node) {
        if (typeof node.value === 'string') {
          checkForSensitiveData(node, node.value);
        }
      },
    };
  },
};

export default rule;
