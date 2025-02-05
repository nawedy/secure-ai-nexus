import bleach
import re
from src.utils.constants import (
    PASSWORD_MUST_CONTAIN_DIGIT,
    PASSWORD_MUST_CONTAIN_LETTER,
    INVALID_CONTACT_NAME,
    INVALID_CONTACT_MESSAGE,
    PASSWORD_MUST_CONTAIN_SPECIAL_CHAR,
    PASSWORD_TOO_SHORT,
    INVALID_INPUT,
    INVALID_EMAIL,
)
from fastapi import HTTPException, status

ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "strong",
    "ul",
    "p",
]  # Authorized HTML tags


def is_email(value: str) -> bool:
    """Check if the value is a valid email."""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.fullmatch(email_regex, value))


def sanitize_text(text: str) -> str:
    """Sanitize the text using the bleach library."""
    if not isinstance(text, str) or len(text) < 1:
        raise ValueError(INVALID_INPUT)
    return bleach.clean(text, tags=ALLOWED_TAGS, strip=True)


def password_validator(cls, value):
    sanitized_value = sanitize_text(value)
    if len(sanitized_value) < 8:
        raise ValueError(PASSWORD_TOO_SHORT)
    if not any(char.isdigit() for char in sanitized_value):
        raise ValueError(PASSWORD_MUST_CONTAIN_DIGIT)
    if not any(char.isalpha() for char in sanitized_value):
        raise ValueError(PASSWORD_MUST_CONTAIN_LETTER)
    if not any(char in "!@#$%^&*()" for char in sanitized_value):
        raise ValueError(PASSWORD_MUST_CONTAIN_SPECIAL_CHAR)
    return sanitized_value


def validate_contact(name: str, message: str):
    """
    Validates the contact form inputs.

    Args:
        name: name of the contact.
        message: message of the contact.

    Raises:
        HTTPException: if the name or message are not valid.
    """
    if not isinstance(name, str) or not isinstance(message, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_INPUT)
    sanitized_name = sanitize_text(name)
    sanitized_message = sanitize_text(message)
    if len(sanitized_name) < 3 or len(sanitized_name) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_CONTACT_NAME)
    if len(sanitized_message) < 10 or len(sanitized_message) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_CONTACT_MESSAGE)
