from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import EmployerSignUpForm, JobSeekerSignUpForm, ProfileForm
from .models import CustomUser, JobSeeker, Employer, Profile
from apps.jobs.models import Application


@ensure_csrf_cookie
def login_view(request):
    session_key = "login_form_data"
    default_form_data = {
        "user_type": request.GET.get("user_type", "job_seeker"),
        "username_or_email": "",
        "remember": False,
    }
    form_data = request.session.pop(session_key, default_form_data)

    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email", "").strip()
        password = request.POST.get("password")
        user_type = request.POST.get("user_type", "job_seeker")
        remember = "remember" in request.POST
        resolved_type = None

        try:
            user = CustomUser.objects.get(
                Q(username=username_or_email) | Q(email=username_or_email)
            )
        except CustomUser.DoesNotExist:
            messages.error(request, "No account found with these credentials.")
        else:
            available_roles = []
            if user.is_job_seeker:
                available_roles.append("job_seeker")
            if user.is_employer:
                available_roles.append("employer")

            resolved_type = user_type

            if not available_roles:
                messages.error(
                    request,
                    "This account has no assigned role. Please contact support.",
                )
                resolved_type = None
            elif resolved_type not in available_roles:
                if len(available_roles) == 1:
                    resolved_type = available_roles[0]
                else:
                    messages.error(
                        request,
                        "Please select the correct user type before signing in.",
                    )
                    resolved_type = None

            if resolved_type:
                authenticated_user = authenticate(
                    request, username=user.username, password=password
                )
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    if not remember:
                        request.session.set_expiry(0)
                    messages.success(request, f"Welcome back, {user.username}!")
                    if resolved_type == "employer":
                        return redirect("dashboard:employer_dashboard")
                    return redirect("dashboard:jobseeker_dashboard")
                messages.error(request, "Invalid password.")

        request.session[session_key] = {
            "user_type": user_type,
            "username_or_email": username_or_email,
            "remember": remember,
        }
        return redirect("accounts:login")

    return render(request, "accounts/login.html", {"form_data": form_data})


def logout_view(request):
    logout(request)
    return redirect("/")


@login_required
def profile_view(request):
    if request.user.is_employer:
        return redirect("dashboard:employer_dashboard")
    elif request.user.is_job_seeker:
        return redirect("dashboard:jobseeker_dashboard")
    return redirect("home")


def employer_signup(request):
    session_key = "employer_signup_form"
    if request.method == "POST":
        form = EmployerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Welcome! Your employer account has been created."
            )
            return redirect("dashboard:employer_dashboard")
        cleaned_post = request.POST.dict()
        cleaned_post.pop("csrfmiddlewaretoken", None)
        request.session[session_key] = cleaned_post
        messages.error(request, "Please correct the errors below.")
        return redirect("accounts:employer_signup")
    stored_data = request.session.pop(session_key, None)
    if stored_data:
        form = EmployerSignUpForm(stored_data)
        form.is_valid()
    else:
        form = EmployerSignUpForm()
    return render(request, "accounts/signup_employer.html", {"form": form})


def jobseeker_signup(request):
    session_key = "jobseeker_signup_form"
    if request.method == "POST":
        form = JobSeekerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Welcome! Your job seeker account has been created."
            )
            return redirect("dashboard:jobseeker_dashboard")
        cleaned_post = request.POST.dict()
        cleaned_post.pop("csrfmiddlewaretoken", None)
        request.session[session_key] = cleaned_post
        messages.error(request, "Please correct the errors below.")
        return redirect("accounts:jobseeker_signup")
    stored_data = request.session.pop(session_key, None)
    if stored_data:
        form = JobSeekerSignUpForm(stored_data)
        form.is_valid()
    else:
        form = JobSeekerSignUpForm()
    return render(request, "accounts/signup_jobseeker.html", {"form": form})


def signup_view(request):
    return render(request, "accounts/signup_choice.html")


@login_required
def user_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    jobseeker = request.user.jobseeker if request.user.is_job_seeker and hasattr(request.user, "jobseeker") else None
    employer = request.user.employer if request.user.is_employer and hasattr(request.user, "employer") else None
    applications = None
    if jobseeker:
        applications = Application.objects.filter(job_seeker=request.user.jobseeker).order_by("-applied_date")[:3]

    jobs = None
    if employer:
        jobs = employer.jobs.filter(is_active=True).order_by("-posted_date")[:5]

    skills = []
    if jobseeker and jobseeker.skills:
        skills = [skill.strip() for skill in jobseeker.skills.split(",") if skill.strip()]

    context = {
        "profile": profile,
        "jobseeker": jobseeker,
        "employer": employer,
        "applications": applications,
        "jobs": jobs,
        "skills": skills,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("accounts:user_profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def employer_profile(request):
    if not request.user.is_employer:
        messages.error(request, "Access denied. Employer account required.")
        return redirect("home")

    context = {
        "user": request.user,
        "employer": request.user.employer,
        "jobs": request.user.employer.jobs.all(),
    }
    return render(request, "accounts/employer_profile.html", context)
