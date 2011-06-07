from django.db.models import Q
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic

from models import *
from forms import *

class ArticleCreateView(generic.CreateView):
    model = Article
    form_class = ArticleForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creation_user = self.request.user
        self.object.save()
        messages.success(self.request, _('article %s created') % self.object)
        return super(ArticleCreateView, self).form_valid(form)

class ArticleUpdateView(generic.UpdateView):
    model = Article
    form_class = ArticleForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        messages.success(self.request, _('article %s updated') % self.object)
        return super(ArticleUpdateView, self).form_valid(form)

    def get_object(self, queryset=None):
        obj = super(ArticleUpdateView, self).get_object(queryset=queryset)
        if obj.creation_user != self.request.user and not request.user.is_staff:
            return http.HttpResponseForbidden(_('Not your article, and you are not staff'))
        return obj
