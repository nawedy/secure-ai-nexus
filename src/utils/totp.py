import pyotp
import hashlib
import qrcode
import time
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class TOTPSecret:
    secret: str
    uri: str
    qrCode: str


async def generate_totp(user_id: str, issuer: str = 'SecureAI Platform') -> TOTPSecret:
    # Generate a secure random secret
    secret = pyotp.random_base32()

    # Create an otpauth URL for QR codes
    uri = pyotp.TOTP(secret).provisioning_uri(name=user_id, issuer_name=issuer)

    # Generate the QR code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    qr_code = qr.make_image(fill_color="black", back_color="white").to_string(encoding='utf-8')

    return TOTPSecret(secret=secret, uri=uri, qrCode=qr_code)


def verify_totp(token: str, secret: str, options: Optional[Dict] = None) -> bool:
    try:
        totp = pyotp.TOTP(secret, interval=30, digits=6)
        window = options.get('window', 1) if options else 1
        time_value = options.get('time') if options and 'time' in options else None
        return totp.verify(token, for_time=time_value, valid_window=window)
    except Exception as error:
        print('TOTP verification error:', error)
        return False


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def generate_backup_code() -> str:
    code = pyotp.random_base32(20)  # 20 bytes = 40 hex chars
    return '-'.join(code[i:i + 4] for i in range(0, len(code), 4))  # Format as XXXX-XXXX-XXXX-XXXX-XXXX


def validate_totp_setup(secret: str, token: str) -> Dict:
    try:
        if not secret or not token:
            return {'valid': False, 'error': 'Missing required parameters'}

        if not token.isdigit() or len(token) != 6:
            return {'valid': False, 'error': 'Invalid token format'}

        # Verify with a slightly larger window during setup
        is_valid = verify_totp(token, secret, {'window': 2})

        return {'valid': is_valid, **({} if is_valid else {'error': 'Invalid verification code'})}
    except Exception as error:
        print('TOTP setup validation error:', error)
        return {'valid': False, 'error': 'Validation failed'}


def generate_emergency_access_token(user_id: str, expires_in: int = 300) -> str:
    secret = pyotp.random_base32()
    timestamp = int(time.time())
    expiry_timestamp = timestamp + expires_in

    token = hashlib.sha256(f'{user_id}:{secret}:{expiry_timestamp}'.encode()).hexdigest()

    return f'{token}.{expiry_timestamp}'