from django.core.validators import RegexValidator

PASSWORD_VALIDATOR = RegexValidator(
    regex=r"^\S{8,}$",
    message="Password must be at least 8 characters long and cannot contain spaces."
)