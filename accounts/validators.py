from django.core.validators import RegexValidator

PASSWORD_VALIDATOR = RegexValidator(
    regex=r"^\S{8,}$",
    message="Password must be at least 8 characters long and cannot contain spaces."
)

CPF_VALIDATOR = RegexValidator(
    regex=r'^\d{11}$',
    message='CPF must contain exactly 11 digits.'
)

PHONE_VALIDATOR = RegexValidator(
    regex=r'^\d{10,11}$',
    message='Phone number must contain 10 or 11 digits.'
)