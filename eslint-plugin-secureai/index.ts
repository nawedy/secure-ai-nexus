import noUnsafeUrls from './rules/no-unsafe-urls';
import noSensitiveInfo from './rules/no-sensitive-info';
import enforceHttps from './rules/enforce-https';
import noWeakCrypto from './rules/no-weak-crypto';
import enforceAuthChecks from './rules/enforce-auth-checks';
import noUnsafeJwt from './rules/no-unsafe-jwt';
import enforceInputValidation from './rules/enforce-input-validation';
import noDataLeaks from './rules/no-data-leaks';

export default {
  rules: {
    'no-unsafe-urls': noUnsafeUrls,
    'no-sensitive-info': noSensitiveInfo,
    'enforce-https': enforceHttps,
    'no-weak-crypto': noWeakCrypto,
    'enforce-auth-checks': enforceAuthChecks,
    'no-unsafe-jwt': noUnsafeJwt,
    'enforce-input-validation': enforceInputValidation,
    'no-data-leaks': noDataLeaks,
  },
  configs: {
    recommended: {
      plugins: ['secureai'],
      rules: {
        'secureai/no-unsafe-urls': 'error',
        'secureai/no-sensitive-info': 'error',
        'secureai/enforce-https': 'error',
        'secureai/no-weak-crypto': 'error',
        'secureai/enforce-auth-checks': 'error',
        'secureai/no-unsafe-jwt': 'error',
        'secureai/enforce-input-validation': 'error',
        'secureai/no-data-leaks': 'error',
      },
    },
  },
};
