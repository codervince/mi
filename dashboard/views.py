
from django.views.generic import TemplateView

# -------Dashboard part

class DashBoardView(TemplateView):
    template_name = 'dashboard/index.html'

class DashProfileView(TemplateView):
    template_name = 'dashboard/profile.html'

class DashToday1View(TemplateView):
    template_name = 'dashboard/today1.html'

class DashToday2View(TemplateView):
    template_name = 'dashboard/today2.html'

class DashAboutView(TemplateView):
    template_name = 'dashboard/about.html'

# --- Funds------

class DashFDygraphsView(TemplateView):
    template_name = 'dashboard/f-dygpraphs.html'

class DashFNTablesView(TemplateView):
    template_name = 'dashboard/f-normaltables.html'

class DashFDTablesView(TemplateView):
    template_name = 'dashboard/f-datatables.html'

# --- Systems------

class DashSDygraphsView(TemplateView):
    template_name = 'dashboard/s-dygpraphs.html'

class DashSNTablesView(TemplateView):
    template_name = 'dashboard/s-normaltables.html'

class DashSDTablesView(TemplateView):
    template_name = 'dashboard/s-datatables.html'