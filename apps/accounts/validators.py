import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ComplexPasswordValidator:
    uppercase_pattern = re.compile(r"[A-Z]")
    digit_pattern = re.compile(r"\d")
    special_pattern = re.compile(r"[!@#$%^&*(),.?\":{}|<>_\-\[\]\\';+/=]")

    def validate(self, password, user=None):
        errors = []

        if not self.uppercase_pattern.search(password):
            errors.append(_("Password must contain at least one uppercase letter."))
        if not self.digit_pattern.search(password):
            errors.append(_("Password must contain at least one number."))
        if not self.special_pattern.search(password):
            errors.append(_("Password must contain at least one special character."))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long and include at least one uppercase letter, one number, and one special character."
        )
