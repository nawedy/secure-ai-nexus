# SecureAI Project Migration Guide

## Overview

This guide provides instructions for migrating existing code to the new project structure. The reorganization aims to improve maintainability, scalability, and code organization while ensuring a smooth transition for developers.

## Migration Process

### 1. Preparation

Before starting the migration:

1. **Backup Your Work**
   ```bash
   # The reorganization script will create a backup automatically
   # But you can also create a manual backup
   cp -r /path/to/project /path/to/backup
   ```

2. **Install Required Tools**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Commit Current Changes**
   ```bash
   git add .
   git commit -m "Pre-reorganization commit"
   ```

### 2. Running the Reorganization

1. **Execute the Script**
   ```bash
   cd /path/to/project
   ./scripts/reorganize.sh
   ```

2. **Review Changes**
   - Check the reorganization log: `reorganization.log`
   - Review the new structure
   - Verify file locations
   - Test functionality

3. **Fix Any Issues**
   - Address validation errors
   - Update import statements
   - Fix broken references

### 3. Directory Structure Changes

#### Source Code (`src/`)

Old Structure:
```
src/
├── api/
├── app/
├── models/
├── tests/
└── utils/
```

New Structure:
```
src/
├── app/
│   ├── client/
│   ├── server/
│   └── shared/
├── core/
│   ├── models/
│   ├── services/
│   └── utils/
├── api/
│   ├── routes/
│   ├── controllers/
│   └── middleware/
├── security/
│   ├── auth/
│   ├── encryption/
│   └── validation/
└── ml/
    ├── training/
    ├── inference/
    └── evaluation/
```

#### Tests

Old Structure:
```
src/tests/
└── test_*.py
```

New Structure:
```
tests/
├── unit/
├── integration/
├── e2e/
├── performance/
└── security/
```

### 4. Import Statement Updates

1. **Old Import Style**
   ```python
   from src.utils import helper
   from src.models import User
   from tests.utils import test_helper
   ```

2. **New Import Style**
   ```python
   from core.utils import helper
   from core.models import User
   from tests.utils import test_helper
   ```

### 5. Common Migration Tasks

1. **Moving Source Files**
   - Frontend code → `src/app/client/`
   - Backend code → `src/app/server/`
   - Shared code → `src/app/shared/`
   - Models → `src/core/models/`
   - Services → `src/core/services/`
   - API routes → `src/api/routes/`

2. **Moving Test Files**
   - Unit tests → `tests/unit/`
   - Integration tests → `tests/integration/`
   - E2E tests → `tests/e2e/`
   - Performance tests → `tests/performance/`
   - Security tests → `tests/security/`

3. **Updating Documentation**
   - API docs → `docs/api/`
   - Architecture docs → `docs/architecture/`
   - User guides → `docs/guides/`
   - Reports → `docs/reports/`

### 6. Post-Migration Tasks

1. **Run Tests**
   ```bash
   pytest
   ```

2. **Update CI/CD**
   - Update build scripts
   - Update deployment configurations
   - Update test runners

3. **Update Documentation**
   - Update README.md
   - Update API documentation
   - Update development guides

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Project reorganization"
   ```

## Common Issues and Solutions

### 1. Import Errors

Problem: `ModuleNotFoundError: No module named 'src'`
Solution: Update import statements to use new directory structure

```python
# Old
from src.utils.helper import format_date

# New
from core.utils.helper import format_date
```

### 2. Test Discovery Issues

Problem: Tests not being discovered
Solution: Update `pytest.ini` configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### 3. Path Resolution

Problem: Relative path resolution issues
Solution: Use project root as base path

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / 'config' / 'settings.yaml'
```

### 4. Circular Imports

Problem: New structure reveals circular imports
Solution: Refactor using dependency injection or restructure modules

```python
# Before
from models.user import User
from services.auth import AuthService

# After
from core.models.base import BaseModel
from core.services.base import BaseService
```

## Best Practices

1. **File Organization**
   - Keep related files together
   - Use clear, descriptive names
   - Follow consistent naming conventions

2. **Import Structure**
   - Use absolute imports
   - Avoid circular dependencies
   - Group imports logically

3. **Testing**
   - Maintain test coverage
   - Update test paths
   - Add new tests for reorganized code

4. **Documentation**
   - Update all documentation references
   - Keep README.md current
   - Document new structure

## Rollback Procedure

If issues arise:

1. **Using Backup**
   ```bash
   # Restore from automatic backup
   cp -r backup_YYYYMMDD_HHMMSS/* .
   ```

2. **Using Git**
   ```bash
   # Revert to pre-reorganization state
   git reset --hard HEAD^
   ```

## Support

For migration issues:

1. Check the reorganization log
2. Review error messages
3. Consult the documentation
4. Submit a GitHub issue

## Timeline

1. **Phase 1: Preparation**
   - Backup data
   - Review changes
   - Plan migration

2. **Phase 2: Migration**
   - Run reorganization
   - Fix immediate issues
   - Update imports

3. **Phase 3: Validation**
   - Run tests
   - Check functionality
   - Verify structure

4. **Phase 4: Deployment**
   - Update CI/CD
   - Deploy changes
   - Monitor issues

## Checklist

- [ ] Create backup
- [ ] Run reorganization script
- [ ] Review changes
- [ ] Update imports
- [ ] Run tests
- [ ] Update documentation
- [ ] Update CI/CD
- [ ] Deploy changes
- [ ] Monitor for issues

## Contact

For additional support:
1. Review documentation
2. Check GitHub issues
3. Contact development team
