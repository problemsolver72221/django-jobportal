from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import CustomUser, Employer, JobSeeker, Profile


def _validate_password_similarity(password: str, username: str = "", email: str = ""):
    errors = []
    lowered_password = (password or "").lower()
    username = (username or "").lower()
    email_local_part = ""
    if email:
        email_local_part = email.split("@", 1)[0].lower()

    if username and username in lowered_password:
        errors.append("Password is too similar to the username.")
    if email_local_part and email_local_part in lowered_password:
        errors.append("Password is too similar to the email address.")

    if errors:
        raise ValidationError(errors)


class EmployerSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=255)
    company_description = forms.CharField(widget=forms.Textarea, required=False)
    company_website = forms.URLField(required=False)
    company_logo = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = (
            "w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm "
            "focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400"
        )
        textarea_class = f"{base_class} resize-y"
        file_class = (
            "w-full px-2 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm "
            "focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400"
        )
        placeholders = {
            "username": "Choose a username",
            "email": "company@example.com",
            "password1": "Enter a password",
            "password2": "Confirm your password",
            "company_name": "Your company name",
            "company_description": "A few sentences about your company",
            "company_website": "https://example.com",
        }

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault("class", file_class)
                continue

            base = textarea_class if isinstance(field.widget, forms.Textarea) else base_class
            field.widget.attrs.setdefault("class", base)
            if name in placeholders:
                field.widget.attrs.setdefault("placeholder", placeholders[name])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn’t match.")

        if password2:
            _validate_password_similarity(
                password2,
                username=self.cleaned_data.get("username", ""),
                email=self.cleaned_data.get("email", ""),
            )

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_employer = True
        if commit:
            user.save()
            Employer.objects.create(
                user=user,
                company_name=self.cleaned_data.get("company_name"),
                company_description=self.cleaned_data.get("company_description"),
                company_website=self.cleaned_data.get("company_website"),
                company_logo=self.cleaned_data.get("company_logo"),
            )
        return user


class JobSeekerSignUpForm(UserCreationForm):
    skills = forms.CharField(widget=forms.Textarea, required=False)
    resume = forms.FileField(required=False)
    experience = forms.CharField(widget=forms.Textarea, required=False)
    education = forms.CharField(widget=forms.Textarea, required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = (
            "w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm "
            "focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all group-hover:border-purple-400"
        )
        textarea_class = f"{base_class} resize-y"
        file_class = (
            "w-full px-2 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm "
            "focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all group-hover:border-purple-400"
        )
        placeholders = {
            "username": "Choose a username",
            "email": "your.email@example.com",
            "password1": "Enter your password",
            "password2": "Confirm your password",
            "skills": "List your key skills (e.g., Python, JavaScript, Project Management)",
            "experience": "Describe your work experience",
            "education": "List your educational background",
        }

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault("class", file_class)
                continue

            base = textarea_class if isinstance(field.widget, forms.Textarea) else base_class
            field.widget.attrs.setdefault("class", base)
            if name in placeholders:
                field.widget.attrs.setdefault("placeholder", placeholders[name])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn’t match.")

        if password2:
            _validate_password_similarity(
                password2,
                username=self.cleaned_data.get("username", ""),
                email=self.cleaned_data.get("email", ""),
            )

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_job_seeker = True
        if commit:
            user.save()
            JobSeeker.objects.create(
                user=user,
                skills=self.cleaned_data.get("skills"),
                resume=self.cleaned_data.get("resume"),
                experience=self.cleaned_data.get("experience"),
                education=self.cleaned_data.get("education"),
            )
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar", "bio", "location")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base_class = (
            "w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm "
            "focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400"
        )
        textarea_class = f"{base_class} resize-y"

        self.fields["bio"].widget.attrs.setdefault(
            "placeholder", "Tell others a little about yourself"
        )
        self.fields["bio"].widget.attrs.setdefault("class", textarea_class)

        self.fields["location"].widget.attrs.setdefault(
            "placeholder", "Where are you based?"
        )
        self.fields["location"].widget.attrs.setdefault("class", base_class)

        self.fields["avatar"].widget.attrs.setdefault(
            "class",
            "w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm "
            "focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400",
        )
