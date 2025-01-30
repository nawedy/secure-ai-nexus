from typing import Dict, List, Optional
import re
from dataclasses import dataclass
import logging
from src.security import encryption

logger = logging.getLogger(__name__)

@dataclass
class ScanResult:
    sensitive_ranges: List[tuple]
    pattern_matches: Dict[str, List[str]]

SENSITIVE_DATA_PATTERNS = {
    'pii': {
        'ssn': r'\d{3}-\d{2}-\d{4}',
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'credit_card': r'\b\d{4}[-. ]?\d{4}[-. ]?\d{4}[-. ]?\d{4}\b'
    },
    'financial': {
        'bank_account': r'\b\d{10,12}\b',
        'routing_number': r'\b\d{9}\b'
    },
    'health': {
        'medical_record': r'MRN[-: ]?\d{6,}',
        'diagnosis_code': r'ICD-\d{1,2}[-: ][A-Z0-9.]{3,}'
    }
}

class SensitiveDataScanner:
    def __init__(self, patterns: Dict = SENSITIVE_DATA_PATTERNS):
        self.patterns = patterns
        
    async def scan(self, data: Dict, patterns: Optional[Dict] = None) -> ScanResult:
        """Scan data for sensitive information patterns"""
        patterns = patterns or self.patterns
        matches = {}
        ranges = []
        
        for category, category_patterns in patterns.items():
            matches[category] = []
            for pattern_name, pattern in category_patterns.items():
                for key, value in data.items():
                    if isinstance(value, str):
                        found = re.finditer(pattern, value)
                        for match in found:
                            matches[category].append({
                                'pattern': pattern_name,
                                'value': match.group(),
                                'field': key
                            })
                            ranges.append((key, match.start(), match.end()))
                            
        return ScanResult(
            sensitive_ranges=ranges,
            pattern_matches=matches
        )

class PrivacyTokenizer:
    def __init__(self):
        self.tokenization_map = {}
        
    async def tokenize(
        self, 
        data: Dict, 
        sensitive_ranges: List[tuple],
        preservation_rules: Optional[Dict] = None
    ) -> Dict:
        """Tokenize sensitive information while preserving data structure"""
        result = data.copy()
        
        for field, start, end in sensitive_ranges:
            if field in result:
                original = result[field][start:end]
                if original not in self.tokenization_map:
                    self.tokenization_map[original] = f"<PROTECTED_{len(self.tokenization_map)}>"
                
                result[field] = (
                    result[field][:start] + 
                    self.tokenization_map[original] + 
                    result[field][end:]
                )
                
        return result
    
    async def detokenize(self, data: Dict) -> Dict:
        """Restore original values from tokenized data"""
        result = data.copy()
        reverse_map = {v: k for k, v in self.tokenization_map.items()}
        
        for field, value in result.items():
            if isinstance(value, str):
                for token, original in reverse_map.items():
                    value = value.replace(token, original)
                result[field] = value
                
        return result

class EncryptionManager:
    def __init__(self):
        self.key_manager = KeyRotationManager()
        self.encryptor = encryption.EncryptionManager()
        
    async def encrypt(self, data: Dict, key_rotation_policy: str) -> Dict:
        """Encrypt sensitive data with key rotation"""
        return await self.encryptor.encrypt(data, key_rotation_policy)
    
    async def decrypt(self, data: Dict) -> Dict:
        """Decrypt protected data"""
        return await self.encryptor.decrypt(data)

class KeyRotationManager:
    def __init__(self):
        self.key_vault_client = None  # Initialize Azure Key Vault client
        self.key_cache = {}
        
    async def get_current_key(self, rotation_policy: str) -> bytes:
        """Get current encryption key based on rotation policy"""
        # Implement key rotation logic here
        # This is a placeholder - implement actual key management
        return b'temporary_key' 