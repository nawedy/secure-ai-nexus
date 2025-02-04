"""
Project Reorganization Script
Implements comprehensive project structure cleanup and organization
"""

import os
import shutil
from pathlib import Path
import logging
from typing import List, Dict, Set
import filecmp
import hashlib
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reorganization.log'),
        logging.StreamHandler()
    ]
)

class ProjectReorganizer:
    """Handles project reorganization tasks"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.backup_dir = self.root_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.file_hashes: Dict[str, Set[str]] = {}

        # Add file pattern definitions
        self.file_patterns = {
            'python': ['*.py', '*.pyi', '*.pyx', '*.pxd'],
            'javascript': ['*.js', '*.jsx', '*.ts', '*.tsx'],
            'styles': ['*.css', '*.scss', '*.sass', '*.less'],
            'templates': ['*.html', '*.jinja', '*.jinja2', '*.j2'],
            'data': ['*.json', '*.yaml', '*.yml', '*.toml'],
            'docs': ['*.md', '*.rst', '*.txt', '*.pdf'],
            'configs': ['*.ini', '*.cfg', '*.conf', '.env*'],
            'scripts': ['*.sh', '*.bash', '*.zsh', '*.fish'],
            'tests': ['test_*.py', '*_test.py', 'conftest.py'],
            'ml_models': ['*.h5', '*.pkl', '*.joblib', '*.onnx']
        }

        # Add directory mappings
        self.dir_mappings = {
            'src/app/client': self.file_patterns['javascript'] + self.file_patterns['styles'] + self.file_patterns['templates'],
            'src/app/server': self.file_patterns['python'],
            'src/core/models': self.file_patterns['python'] + self.file_patterns['data'],
            'src/api': self.file_patterns['python'],
            'src/security': self.file_patterns['python'],
            'src/ml': self.file_patterns['python'] + self.file_patterns['ml_models'],
            'src/monitoring': self.file_patterns['python'],
            'src/config': self.file_patterns['configs'] + self.file_patterns['data'],
            'tests': self.file_patterns['tests'],
            'scripts': self.file_patterns['scripts'],
            'docs': self.file_patterns['docs']
        }

    def create_backup(self) -> None:
        """Create backup of current project state"""
        logging.info("Creating project backup...")
        shutil.copytree(self.root_dir, self.backup_dir, ignore=shutil.ignore_patterns(
            '.git', '__pycache__', 'node_modules', '.env', 'backup_*'
        ))
        logging.info(f"Backup created at: {self.backup_dir}")

    def get_file_hash(self, file_path: Path) -> str:
        """Calculate file hash for duplicate detection"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def find_duplicates(self) -> Dict[str, List[Path]]:
        """Find duplicate files based on content"""
        logging.info("Scanning for duplicate files...")
        duplicates: Dict[str, List[Path]] = {}

        for root, _, files in os.walk(self.root_dir):
            root_path = Path(root)
            if any(p in str(root_path) for p in ['.git', '__pycache__', 'node_modules', 'backup_']):
                continue

            for file in files:
                file_path = root_path / file
                try:
                    file_hash = self.get_file_hash(file_path)
                    if file_hash in duplicates:
                        duplicates[file_hash].append(file_path)
                    else:
                        duplicates[file_hash] = [file_path]
                except (IOError, OSError) as e:
                    logging.warning(f"Could not read file {file_path}: {e}")

        return {h: paths for h, paths in duplicates.items() if len(paths) > 1}

    def consolidate_tests(self) -> None:
        """Consolidate test files into a single directory"""
        logging.info("Consolidating test files...")
        test_dirs = [
            self.root_dir / 'tests',
            self.root_dir / 'src/tests'
        ]

        # Create new test directory structure
        new_test_structure = {
            'unit': self.root_dir / 'tests/unit',
            'integration': self.root_dir / 'tests/integration',
            'e2e': self.root_dir / 'tests/e2e',
            'performance': self.root_dir / 'tests/performance',
            'security': self.root_dir / 'tests/security'
        }

        for dir_path in new_test_structure.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Move test files to appropriate directories
        for test_dir in test_dirs:
            if not test_dir.exists():
                continue

            for root, _, files in os.walk(test_dir):
                for file in files:
                    if not file.endswith('.py'):
                        continue

                    src_path = Path(root) / file
                    dest_dir = None

                    # Determine appropriate test category
                    if 'unit' in str(src_path):
                        dest_dir = new_test_structure['unit']
                    elif 'integration' in str(src_path):
                        dest_dir = new_test_structure['integration']
                    elif 'e2e' in str(src_path):
                        dest_dir = new_test_structure['e2e']
                    elif 'performance' in str(src_path) or 'benchmark' in str(src_path):
                        dest_dir = new_test_structure['performance']
                    elif 'security' in str(src_path):
                        dest_dir = new_test_structure['security']
                    else:
                        # Default to unit tests if no category is found
                        dest_dir = new_test_structure['unit']

                    if dest_dir:
                        dest_path = dest_dir / file
                        if dest_path.exists():
                            # If file exists, compare content and keep newer version
                            if src_path.stat().st_mtime > dest_path.stat().st_mtime:
                                shutil.copy2(src_path, dest_path)
                        else:
                            shutil.copy2(src_path, dest_path)

        # Remove old test directories
        if (self.root_dir / 'src/tests').exists():
            shutil.rmtree(self.root_dir / 'src/tests')

    def consolidate_documentation(self) -> None:
        """Consolidate documentation files"""
        logging.info("Consolidating documentation...")

        docs_dir = self.root_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)

        # Create documentation structure
        doc_structure = {
            'architecture': docs_dir / 'architecture',
            'api': docs_dir / 'api',
            'guides': docs_dir / 'guides',
            'reports': docs_dir / 'reports'
        }

        for dir_path in doc_structure.values():
            dir_path.mkdir(exist_ok=True)

        # Move documentation files
        doc_patterns = ['*.md', '*.rst', '*.txt']
        for pattern in doc_patterns:
            for doc_file in self.root_dir.glob(pattern):
                if 'node_modules' in str(doc_file):
                    continue

                # Determine appropriate category
                dest_dir = None
                if 'api' in doc_file.name.lower():
                    dest_dir = doc_structure['api']
                elif 'architecture' in doc_file.name.lower():
                    dest_dir = doc_structure['architecture']
                elif any(x in doc_file.name.lower() for x in ['guide', 'tutorial', 'how']):
                    dest_dir = doc_structure['guides']
                elif any(x in doc_file.name.lower() for x in ['report', 'audit', 'status']):
                    dest_dir = doc_structure['reports']
                else:
                    dest_dir = docs_dir

                if dest_dir and doc_file.parent != dest_dir:
                    shutil.copy2(doc_file, dest_dir / doc_file.name)

    def cleanup(self) -> None:
        """Clean up temporary and unnecessary files"""
        logging.info("Cleaning up project...")

        patterns_to_remove = [
            '**/.DS_Store',
            '**/*.pyc',
            '**/__pycache__',
            '**/node_modules',
            '**/dist',
            '**/build',
            '**/.coverage',
            '**/.pytest_cache'
        ]

        for pattern in patterns_to_remove:
            for path in self.root_dir.glob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                except (IOError, OSError) as e:
                    logging.warning(f"Could not remove {path}: {e}")

    def update_imports(self) -> None:
        """Update import statements in Python files"""
        logging.info("Updating import statements...")

        for py_file in self.root_dir.rglob('*.py'):
            if any(x in str(py_file) for x in ['.git', '__pycache__', 'node_modules', 'backup_']):
                continue

            try:
                with open(py_file, 'r') as f:
                    content = f.read()

                # Update import statements based on new structure
                updates = {
                    'from src.': 'from ',
                    'from tests.': 'from ',
                    'import src.': 'import ',
                    'import tests.': 'import '
                }

                for old, new in updates.items():
                    content = content.replace(old, new)

                with open(py_file, 'w') as f:
                    f.write(content)

            except (IOError, OSError) as e:
                logging.warning(f"Could not update imports in {py_file}: {e}")

    def validate_structure(self) -> List[str]:
        """Validate the project structure after reorganization"""
        logging.info("Validating project structure...")
        errors = []

        # Check required directories exist
        required_dirs = [
            'src/app/client',
            'src/app/server',
            'src/core/models',
            'src/api',
            'src/security',
            'src/ml',
            'src/monitoring',
            'src/config',
            'tests/unit',
            'tests/integration',
            'docs/architecture'
        ]

        for dir_path in required_dirs:
            full_path = self.root_dir / dir_path
            if not full_path.exists():
                errors.append(f"Required directory missing: {dir_path}")

        # Validate file locations
        for root, _, files in os.walk(self.root_dir):
            rel_path = Path(root).relative_to(self.root_dir)

            # Skip certain directories
            if any(p in str(rel_path) for p in ['.git', '__pycache__', 'node_modules', 'backup_']):
                continue

            for file in files:
                file_path = Path(root) / file
                rel_file_path = file_path.relative_to(self.root_dir)

                # Check if file is in the correct directory
                correct_location = False
                for dir_pattern, allowed_patterns in self.dir_mappings.items():
                    if str(rel_path).startswith(dir_pattern):
                        if any(file_path.match(pattern) for pattern in allowed_patterns):
                            correct_location = True
                            break

                if not correct_location:
                    errors.append(f"File in incorrect location: {rel_file_path}")

        # Validate import statements
        for py_file in self.root_dir.rglob('*.py'):
            if any(p in str(py_file) for p in ['.git', '__pycache__', 'node_modules', 'backup_']):
                continue

            try:
                with open(py_file, 'r') as f:
                    content = f.read()

                # Check for absolute imports
                if 'from .' in content or 'import .' in content:
                    errors.append(f"Relative import found in: {py_file}")

                # Check for circular imports
                if 'import src.' in content and 'src' in str(py_file):
                    errors.append(f"Potential circular import in: {py_file}")
            except Exception as e:
                errors.append(f"Error checking imports in {py_file}: {e}")

        return errors

    def reorganize_source_code(self) -> None:
        """Reorganize source code directory structure"""
        logging.info("Reorganizing source code...")

        # Define new directory structure with file patterns
        new_structure = {
            'app': {
                'client': self.file_patterns['javascript'] + self.file_patterns['styles'],
                'server': self.file_patterns['python'],
                'shared': self.file_patterns['python'] + self.file_patterns['javascript']
            },
            'core': {
                'models': self.file_patterns['python'],
                'services': self.file_patterns['python'],
                'utils': self.file_patterns['python']
            },
            'api': {
                'routes': self.file_patterns['python'],
                'controllers': self.file_patterns['python'],
                'middleware': self.file_patterns['python']
            },
            'security': {
                'auth': self.file_patterns['python'],
                'encryption': self.file_patterns['python'],
                'validation': self.file_patterns['python']
            },
            'ml': {
                'training': self.file_patterns['python'] + self.file_patterns['ml_models'],
                'inference': self.file_patterns['python'] + self.file_patterns['ml_models'],
                'evaluation': self.file_patterns['python']
            },
            'monitoring': {
                'metrics': self.file_patterns['python'],
                'alerts': self.file_patterns['python'],
                'logging': self.file_patterns['python']
            },
            'config': {
                'environments': self.file_patterns['configs'],
                'settings': self.file_patterns['configs'] + self.file_patterns['data']
            }
        }

        # Create directories and move files
        for dir_name, subdirs in new_structure.items():
            base_dir = self.root_dir / 'src' / dir_name
            base_dir.mkdir(parents=True, exist_ok=True)

            for subdir, patterns in subdirs.items():
                subdir_path = base_dir / subdir
                subdir_path.mkdir(parents=True, exist_ok=True)

                # Find and move matching files
                for pattern in patterns:
                    for file_path in self.root_dir.rglob(pattern):
                        if any(p in str(file_path) for p in ['.git', '__pycache__', 'node_modules', 'backup_']):
                            continue

                        # Determine if file should be moved
                        if self._should_move_file(file_path, subdir_path):
                            dest_path = subdir_path / file_path.name
                            if not dest_path.exists():
                                shutil.copy2(file_path, dest_path)

    def _should_move_file(self, file_path: Path, dest_dir: Path) -> bool:
        """Determine if a file should be moved to the destination directory"""
        # Don't move files that are already in the correct place
        if dest_dir in file_path.parents:
            return False

        # Don't move test files to source directories
        if 'test' in file_path.name.lower() and 'src' in str(dest_dir):
            return False

        # Don't move documentation to source directories
        if file_path.suffix in ['.md', '.rst', '.txt'] and 'src' in str(dest_dir):
            return False

        return True

    def run(self) -> None:
        """Execute the complete reorganization process"""
        try:
            # Create backup
            self.create_backup()

            # Find and report duplicates
            duplicates = self.find_duplicates()
            if duplicates:
                logging.info("Found duplicate files:")
                for _, paths in duplicates.items():
                    logging.info(f"Duplicate set: {[str(p) for p in paths]}")

            # Perform reorganization
            self.consolidate_tests()
            self.reorganize_source_code()
            self.consolidate_documentation()
            self.cleanup()
            self.update_imports()

            # Validate new structure
            errors = self.validate_structure()
            if errors:
                logging.warning("Structure validation found issues:")
                for error in errors:
                    logging.warning(f"- {error}")
            else:
                logging.info("Structure validation passed successfully!")

            logging.info("Project reorganization completed successfully!")

        except Exception as e:
            logging.error(f"Error during reorganization: {e}")
            logging.info("Restoring from backup...")
            if self.backup_dir.exists():
                shutil.rmtree(self.root_dir)
                shutil.copytree(self.backup_dir, self.root_dir)
            logging.info("Backup restored.")
            raise

if __name__ == "__main__":
    reorganizer = ProjectReorganizer(".")
    reorganizer.run()
