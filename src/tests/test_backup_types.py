import pytest
from src.types.backup import (
    BackupCode,
    BackupCodesState,
    BackupCodesValidation,
    BackupCodesGenerationOptions,
)


def test_backup_code_creation():
    backup_code = BackupCode(code="123456", used=False, hashedValue="hashed")
    assert backup_code.code == "123456"
    assert backup_code.used is False
    assert backup_code.usedAt is None
    assert backup_code.hashedValue == "hashed"


def test_backup_codes_state_creation():
    backup_code1 = BackupCode(code="123456", used=False, hashedValue="hashed")
    backup_code2 = BackupCode(code="789012", used=True, usedAt="2023-10-28", hashedValue="hashed2")
    backup_codes_state = BackupCodesState(
        codes=[backup_code1, backup_code2], generatedAt="2023-10-27", remainingCodes=2
    )
    assert len(backup_codes_state.codes) == 2
    assert backup_codes_state.codes[0].code == "123456"
    assert backup_codes_state.codes[1].code == "789012"
    assert backup_codes_state.generatedAt == "2023-10-27"
    assert backup_codes_state.lastUsed is None
    assert backup_codes_state.remainingCodes == 2


def test_backup_codes_validation_creation():
    validation = BackupCodesValidation(valid=True, used=False)
    assert validation.valid is True
    assert validation.used is False
    assert validation.error is None


def test_backup_codes_generation_options_creation():
    options = BackupCodesGenerationOptions(
        numberOfCodes=10, codeLength=6, format="groups", groupSize=3
    )
    assert options.numberOfCodes == 10
    assert options.codeLength == 6
    assert options.format == "groups"
    assert options.groupSize == 3

def test_backup_codes_generation_options_creation_with_defaults():
    options = BackupCodesGenerationOptions()
    assert options.numberOfCodes is None
    assert options.codeLength is None
    assert options.format is None
    assert options.groupSize is None

def test_backup_codes_generation_invalid_format():
    with pytest.raises(ValueError):
        BackupCodesGenerationOptions(
            numberOfCodes=10, codeLength=6, format="invalid", groupSize=3
        )