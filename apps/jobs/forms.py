from django import forms
from .models import Job, Application
from django_select2.forms import Select2Widget


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "category",
            "description",
            "requirements",
            "location",
            "salary",
            # "salary_currency",
            "salary_type",
            "job_type",
            "deadline",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
            "job_type": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400",
                }
            )
            # ✅ Special styling for salary MoneyField


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["cover_letter"]
        widgets = {
            "cover_letter": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Write your cover letter here..."}
            )
        }


class JobSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Job title or keyword"}),
    )
    location = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"placeholder": "Location"})
    )
    category = forms.ChoiceField(required=False)
    job_type = forms.ChoiceField(
        required=False, choices=[("", "All Types")] + Job.JOB_TYPE_CHOICES
    )


class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "location", "salary", "job_type"]
