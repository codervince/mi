from .forms import UserRegistrationForm
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.contrib.auth import views as auth_views
from systems.models import System, SystemSnapshot
import pytz
from pytz import timezone
from django.db.models import Count
from datetime import datetime

def getracedatetime(racedate, racetime):

    _rt = datetime.strptime(racetime,'%I:%M %p').time()
    racedatetime = datetime.combine(racedate, _rt)
    localtz = timezone('Europe/London')
    racedatetime = localtz.localize(racedatetime)
    return racedatetime

def landing(request):
    if request.user.is_authenticated():
        #get systems and return template with this as context
        # ss_2016_start = (getracedatetime(datetime.strptime("20160101", "%Y%m%d").date(), '12:00 AM')).date()
        #
        # all_snaps_2016 = SystemSnapshot.thisyear.filter(validfrom__date=ss_2016_start).annotate(
        #     null_position=Count('levelbspprofit')).order_by('-null_position', '-levelbspprofit')
        return redirect('systems:systems_index')
        # return render_to_response('investment/landing.html', {'snaps': all_snaps_2016})
    else:
        #return normal template
        return render_to_response('investment/landing.html')




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
