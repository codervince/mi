from .forms import UserRegistrationForm
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.contrib.auth import views as auth_views


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
            login(request, user)
            return HttpResponseRedirect(reverse('userdetail'))
    else:
        user_form = UserRegistrationForm()
    return render(request, 'investment/account/registration.html', {'user_form': user_form})


def logout_view(request):
    logout(request)
    redirect_to=request.GET.get('next', '/account/login')
    return HttpResponseRedirect(redirect_to)



def login_view(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(0)
    return auth_views.login(request, *args, **kwargs)