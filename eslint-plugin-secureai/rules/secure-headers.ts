import { Rule } from 'eslint';
import { Node, CallExpression, ObjectExpression, Property } from 'estree';

const SECURITY_HEADERS = {
  required: {
    'Strict-Transport-Security': {
      value: 'max-age=31536000; includeSubDomains; preload',
      required: true,
    },
    'Content-Security-Policy': {
      value: "default-src 'self'; script-src 'self' 'nonce-{NONCE}'; style-src 'self' 'nonce-{NONCE}'; img-src 'self' data: https:; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none';",
      required: true,
    },
    'X-Content-Type-Options': {
      value: 'nosniff',
      required: true,
    },
    'X-Frame-Options': {
      value: 'DENY',
      required: true,
    },
    'X-XSS-Protection': {
      value: '1; mode=block',
      required: true,
    },
    'Referrer-Policy': {
      value: 'strict-origin-when-cross-origin',
      required: true,
    },
    'Permissions-Policy': {
      value: "camera=(), microphone=(), geolocation=(), payment=('self'), usb=(), vr=()",
      required: true,
    },
  },
  recommended: {
    'Cross-Origin-Embedder-Policy': 'require-corp',
    'Cross-Origin-Opener-Policy': 'same-origin',
    'Cross-Origin-Resource-Policy': 'same-origin',
    'Cache-Control': 'no-store, max-age=0',
    'Clear-Site-Data': '"cache", "cookies", "storage"',
    'NEL': '{"report_to": "default", "max_age": 31536000, "include_subdomains": true}',
    'Report-To': '{"group": "default", "max_age": 31536000, "endpoints": [{"url": "/api/security/reports"}]}',
  },
  pythonFrameworks: {
    fastapi: {
      middleware: 'SecurityMiddleware',
      config: 'SecurityConfig',
    },
    django: {
      middleware: 'SecurityMiddleware',
      settings: 'SECURITY_HEADERS',
    },
    flask: {
      extension: 'Talisman',
      config: 'security_headers',
    },
  },
};

const rule: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce secure HTTP headers',
      category: 'Security',
      recommended: true,
    },
    schema: [],
    messages: {
      missingRequiredHeader: 'Missing required security header: {{header}}',
      invalidHeaderValue: 'Invalid value for security header: {{header}}',
      missingCSPDirective: 'Content-Security-Policy missing critical directive: {{directive}}',
      weakHeaderValue: 'Security header value too permissive: {{header}}',
      missingMiddleware: 'Security middleware not properly configured',
      recommendedHeader: 'Consider adding recommended security header: {{header}}',
      nonceMissing: 'CSP should use nonces for script and style sources',
      reportingMissing: 'Security violation reporting not configured',
    },
  },

  create(context) {
    let hasSecurityMiddleware = false;
    let hasReportingEndpoint = false;

    const checkHeaderValue = (node: Property) => {
      if (node.key.type === 'Literal' || node.key.type === 'Identifier') {
        const headerName = node.key.type === 'Literal' ? node.key.value : node.key.name;

        if (SECURITY_HEADERS.required[headerName]) {
          if (node.value.type === 'Literal') {
            const headerValue = node.value.value as string;
            const requiredValue = SECURITY_HEADERS.required[headerName].value;

            if (!headerValue.includes(requiredValue)) {
              context.report({
                node,
                messageId: 'invalidHeaderValue',
                data: { header: headerName },
              });
            }

            // Special checks for CSP
            if (headerName === 'Content-Security-Policy') {
              if (!headerValue.includes('nonce-')) {
                context.report({
                  node,
                  messageId: 'nonceMissing',
                });
              }

              ['default-src', 'script-src', 'style-src'].forEach(directive => {
                if (!headerValue.includes(directive)) {
                  context.report({
                    node,
                    messageId: 'missingCSPDirective',
                    data: { directive },
                  });
                }
              });
            }
          }
        }
      }
    };

    const checkSecurityMiddleware = (node: ImportDeclaration) => {
      const importSource = context.getSourceCode().getText(node.source);
      Object.values(SECURITY_HEADERS.pythonFrameworks).forEach(framework => {
        if (importSource.includes(framework.middleware)) {
          hasSecurityMiddleware = true;
        }
      });
    };

    const checkReportingEndpoint = (node: Node) => {
      if (node.type === 'ObjectExpression') {
        node.properties.forEach(prop => {
          if (
            prop.type === 'Property' &&
            prop.key.type === 'Identifier' &&
            (prop.key.name === 'Report-To' || prop.key.name === 'NEL')
          ) {
            hasReportingEndpoint = true;
          }
        });
      }
    };

    return {
      // Check imports for security middleware
      ImportDeclaration(node) {
        checkSecurityMiddleware(node);
      },

      // Check header configurations
      Property(node) {
        checkHeaderValue(node);
      },

      // Check for reporting endpoints
      ObjectExpression(node) {
        checkReportingEndpoint(node);
      },

      // Program exit checks
      'Program:exit'() {
        if (!hasSecurityMiddleware) {
          context.report({
            node: null,
            messageId: 'missingMiddleware',
          });
        }

        if (!hasReportingEndpoint) {
          context.report({
            node: null,
            messageId: 'reportingMissing',
          });
        }

        // Check for recommended headers
        Object.entries(SECURITY_HEADERS.recommended).forEach(([header, value]) => {
          context.report({
            node: null,
            messageId: 'recommendedHeader',
            data: { header },
          });
        });
      },
    };
  },
};

export default rule;
