from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import ProfileForm, RegistrationForm
from django.contrib.auth.decorators import login_required

def register(request):
    if request.user.is_authenticated:
        return redirect("restaurant:home")

    form = RegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)

        messages.success(
            request,
            "Votre compte a été créé.",
        )

        return redirect("restaurant:home")

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )

@login_required
def profile(request):
    form = ProfileForm(
        request.POST or None,
        instance=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Vos informations ont été mises à jour.",
        )

        return redirect("accounts:profile")

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
        },
    )