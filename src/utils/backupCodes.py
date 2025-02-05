import secrets
import random
import hashlib
import requests
from typing import List
from datetime import datetime
from dataclasses import dataclass


BACKUP_CODE_ALPHABET = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
BACKUP_CODE_LENGTH = 10
NUMBER_OF_CODES = 10


class BackupCodesManager:
    @staticmethod
    def __generate_single_code():
        return ''.join(secrets.choice(BACKUP_CODE_ALPHABET) for _ in range(BACKUP_CODE_LENGTH))

    @staticmethod
    def generate_codes():
        codes = []
        while len(codes) < NUMBER_OF_CODES:
            code = BackupCodesManager.__generate_single_code()
            if code not in codes:
                codes.append(code)
        return codes

    @staticmethod
    def hash_code(code: str):
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    def format_code(code: str):
        return '-'.join(code[i:i + 5] for i in range(0, len(code), 5))

    @staticmethod
    def validate_code(code: str, hashed_codes: List[str]):
        normalized_code = code.replace('-', '').upper()
        hashed_code = BackupCodesManager.hash_code(normalized_code)
        return hashed_code in hashed_codes
    
@dataclass
class BackupCodesStorage:
    hashedCodes: List[str]
    lastGenerated: str
    usedCodes: List[str]
        

async def store_backup_codes(user_id: str, codes: List[str]):
    hashed_codes = [BackupCodesManager.hash_code(code) for code in codes]
    storage = BackupCodesStorage(
        hashedCodes=hashed_codes,
        lastGenerated=datetime.now().isoformat(),
        usedCodes=[],
    )

    # Store in secure backend storage (replace with actual implementation)
    response = requests.post(
        '/api/auth/backup-codes',
        headers={'Content-Type': 'application/json'},
        json={
            'userId': user_id,
            'codes': storage.__dict__,
        },
    )
    response.raise_for_status()  # Raise an exception for bad responses


async def validate_and_use_backup_code(user_id: str, code: str):
    try:
        response = requests.post(
            '/api/auth/backup-codes/verify',
            headers={'Content-Type': 'application/json'},
            json={'userId': user_id, 'code': code},
        )
        response.raise_for_status()  # Raise an exception for bad responses
        result = response.json()
        return result.get('valid', False)
    except requests.exceptions.RequestException as error:
        print('Backup code validation failed:', error)
        return False