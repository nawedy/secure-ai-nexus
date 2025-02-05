import pytest
import hashlib
from src.utils.backupCodes import BackupCodesManager, BackupCodesStorage, store_backup_codes, validate_and_use_backup_code


def test_generate_single_code():
    code = BackupCodesManager._BackupCodesManager__generate_single_code()
    assert len(code) == 10
    for char in code:
        assert char in '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'


def test_generate_codes():
    codes = BackupCodesManager.generate_codes()
    assert len(codes) == 10
    assert len(set(codes)) == 10  # Check for uniqueness
    for code in codes:
        assert len(code) == 10
        for char in code:
            assert char in '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'


def test_hash_code():
    code = "ABCDEFGH12"
    hashed_code = BackupCodesManager.hash_code(code)
    assert len(hashed_code) == 64
    assert all(c in '0123456789abcdef' for c in hashed_code)
    # Check that it's a valid SHA256 hash
    assert hashlib.sha256(code.encode()).hexdigest() == hashed_code


def test_format_code():
    code = "ABCDEFGH12"
    formatted_code = BackupCodesManager.format_code(code)
    assert formatted_code == "ABCDE-FGH12"

    code = "ABCDEFGHIJ"
    formatted_code = BackupCodesManager.format_code(code)
    assert formatted_code == "ABCDE-FGHIJ"

    code = "ABCDEFGHIJKL"
    formatted_code = BackupCodesManager.format_code(code)
    assert formatted_code == "ABCDE-FGHIJ-KL"


def test_validate_code():
    code = "ABCDEFGHIJ"
    hashed_codes = [BackupCodesManager.hash_code(code)]
    assert BackupCodesManager.validate_code(code, hashed_codes) is True

    code2 = "1234567890"
    assert BackupCodesManager.validate_code(code2, hashed_codes) is False

    assert BackupCodesManager.validate_code("abcde-fghij", hashed_codes) is True
    assert BackupCodesManager.validate_code("ABCDE-FGHIJ", hashed_codes) is True
    assert BackupCodesManager.validate_code("ABCDEfghij", hashed_codes) is True