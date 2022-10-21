from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import Creationform


class SignUp(CreateView):
    form_class = Creationform
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
