"""
Unit Tests for Project Reorganization Script
Tests the functionality of the project reorganization tools
"""

import pytest
import os
import shutil
from pathlib import Path
import tempfile
from datetime import datetime
import json
import yaml

from scripts.reorganize_project import ProjectReorganizer

class TestProjectReorganizer:
    """Test suite for ProjectReorganizer class"""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create basic project structure
            project_dir = Path(temp_dir)

            # Create source directories
            (project_dir / 'src').mkdir()
            (project_dir / 'src/app').mkdir()
            (project_dir / 'src/tests').mkdir()
            (project_dir / 'tests').mkdir()
            (project_dir / 'docs').mkdir()

            # Create test files
            test_files = {
                'src/app/test_file.py': 'def test_function(): pass',
                'src/tests/test_module.py': 'def test_case(): assert True',
                'tests/test_integration.py': 'def test_integration(): pass',
                'docs/readme.md': '# Test Documentation'
            }

            for file_path, content in test_files.items():
                file = project_dir / file_path
                file.parent.mkdir(exist_ok=True)
                file.write_text(content)

            yield project_dir

    @pytest.fixture
    def reorganizer(self, temp_project_dir):
        """Create ProjectReorganizer instance"""
        return ProjectReorganizer(str(temp_project_dir))

    def test_initialization(self, reorganizer, temp_project_dir):
        """Test reorganizer initialization"""
        assert reorganizer.root_dir == temp_project_dir
        assert isinstance(reorganizer.file_patterns, dict)
        assert isinstance(reorganizer.dir_mappings, dict)

    def test_create_backup(self, reorganizer):
        """Test backup creation"""
        reorganizer.create_backup()
        assert reorganizer.backup_dir.exists()
        assert (reorganizer.backup_dir / 'src').exists()
        assert (reorganizer.backup_dir / 'tests').exists()
        assert (reorganizer.backup_dir / 'docs').exists()

    def test_find_duplicates(self, reorganizer, temp_project_dir):
        """Test duplicate file detection"""
        # Create duplicate files
        file1 = temp_project_dir / 'src/file1.py'
        file2 = temp_project_dir / 'src/file2.py'
        content = 'print("test")'
        file1.write_text(content)
        file2.write_text(content)

        duplicates = reorganizer.find_duplicates()
        assert len(duplicates) == 1
        assert len(next(iter(duplicates.values()))) == 2

    def test_consolidate_tests(self, reorganizer, temp_project_dir):
        """Test test file consolidation"""
        reorganizer.consolidate_tests()

        # Check test files are moved correctly
        assert not (temp_project_dir / 'src/tests').exists()
        assert (temp_project_dir / 'tests/unit').exists()
        assert (temp_project_dir / 'tests/integration').exists()

    def test_reorganize_source_code(self, reorganizer, temp_project_dir):
        """Test source code reorganization"""
        # Create test files in various locations
        files = {
            'src/app/client/app.js': 'console.log("test")',
            'src/app/server/api.py': 'def api(): pass',
            'src/models/model.py': 'class Model: pass',
            'src/security/auth.py': 'def authenticate(): pass'
        }

        for file_path, content in files.items():
            file = temp_project_dir / file_path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content)

        reorganizer.reorganize_source_code()

        # Verify file locations
        assert (temp_project_dir / 'src/app/client/app.js').exists()
        assert (temp_project_dir / 'src/app/server/api.py').exists()
        assert (temp_project_dir / 'src/core/models/model.py').exists()
        assert (temp_project_dir / 'src/security/auth/auth.py').exists()

    def test_consolidate_documentation(self, reorganizer, temp_project_dir):
        """Test documentation consolidation"""
        # Create test documentation files
        docs = {
            'api.md': '# API Documentation',
            'architecture.md': '# Architecture',
            'guide.md': '# User Guide',
            'report.md': '# Status Report'
        }

        for file_name, content in docs.items():
            (temp_project_dir / file_name).write_text(content)

        reorganizer.consolidate_documentation()

        # Verify documentation organization
        assert (temp_project_dir / 'docs/api/api.md').exists()
        assert (temp_project_dir / 'docs/architecture/architecture.md').exists()
        assert (temp_project_dir / 'docs/guides/guide.md').exists()
        assert (temp_project_dir / 'docs/reports/report.md').exists()

    def test_cleanup(self, reorganizer, temp_project_dir):
        """Test cleanup functionality"""
        # Create files to be cleaned up
        cleanup_files = [
            '.DS_Store',
            '__pycache__/cache.pyc',
            'node_modules/package/index.js',
            '.coverage'
        ]

        for file_path in cleanup_files:
            file = temp_project_dir / file_path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch()

        reorganizer.cleanup()

        # Verify files are removed
        for file_path in cleanup_files:
            assert not (temp_project_dir / file_path).exists()

    def test_update_imports(self, reorganizer, temp_project_dir):
        """Test import statement updates"""
        # Create test Python files with imports
        test_files = {
            'src/module.py': 'from src.utils import helper\nimport src.config',
            'tests/test_module.py': 'from tests.utils import test_helper'
        }

        for file_path, content in test_files.items():
            file = temp_project_dir / file_path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content)

        reorganizer.update_imports()

        # Verify import statements are updated
        assert 'from utils import helper' in (temp_project_dir / 'src/module.py').read_text()
        assert 'import config' in (temp_project_dir / 'src/module.py').read_text()
        assert 'from utils import test_helper' in (temp_project_dir / 'tests/test_module.py').read_text()

    def test_validate_structure(self, reorganizer, temp_project_dir):
        """Test structure validation"""
        # Create valid project structure
        for dir_path in reorganizer.dir_mappings.keys():
            (temp_project_dir / dir_path).mkdir(parents=True, exist_ok=True)

        # Add some files
        test_files = {
            'src/app/client/app.js': 'console.log("test")',
            'src/app/server/api.py': 'def api(): pass',
            'src/security/auth/auth.py': 'def auth(): pass',
            'tests/unit/test_api.py': 'def test_api(): pass'
        }

        for file_path, content in test_files.items():
            file = temp_project_dir / file_path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content)

        errors = reorganizer.validate_structure()
        assert not errors, f"Validation errors found: {errors}"

    def test_should_move_file(self, reorganizer):
        """Test file movement logic"""
        # Test cases
        test_cases = [
            (Path('src/file.py'), Path('src/core/models'), True),
            (Path('src/core/models/file.py'), Path('src/core/models'), False),
            (Path('src/test_file.py'), Path('src/core/models'), False),
            (Path('README.md'), Path('src/core/models'), False)
        ]

        for src, dest, expected in test_cases:
            assert reorganizer._should_move_file(src, dest) == expected

    def test_full_reorganization(self, reorganizer, temp_project_dir):
        """Test complete reorganization process"""
        # Create test project structure
        test_files = {
            'src/app/client/app.js': 'console.log("test")',
            'src/app/server/api.py': 'def api(): pass',
            'src/tests/test_api.py': 'def test_api(): pass',
            'docs/api.md': '# API Documentation',
            'README.md': '# Project Documentation'
        }

        for file_path, content in test_files.items():
            file = temp_project_dir / file_path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content)

        # Run reorganization
        reorganizer.run()

        # Verify final structure
        assert not (temp_project_dir / 'src/tests').exists()
        assert (temp_project_dir / 'tests/unit').exists()
        assert (temp_project_dir / 'docs/api').exists()
        assert reorganizer.backup_dir.exists()

        # Verify no validation errors
        errors = reorganizer.validate_structure()
        assert not errors, f"Validation errors found after reorganization: {errors}"
