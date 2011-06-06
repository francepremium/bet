from django.conf.urls.defaults import *
from django.conf import settings
from django.views import generic

import views, models

urlpatterns = patterns('',
    url(
        r'create/$',
        views.ArticleCreateView.as_view(),
        name='article_create',
    ),
    url(
        r'(?P<slug>[^/]+)/edit/$',
        views.ArticleUpdateView.as_view(),
        name='article_update',
    ),
    url(
        r'(?P<slug>[^/]+)/delete/$',
        'django.views.generic.create_update.delete_object', {
            'model': models.Article,
            'post_delete_redirect': '../post/',
        },
    ),
    url(
        r'(?P<slug>[^/]+)/$',
        generic.DetailView.as_view(
            model=models.Article,
            context_object_name='article'
        ),
        name='article_detail',
    ),
    url(
        r'',
        generic.ListView.as_view(
            model=models.Article, 
            queryset=models.Article.objects.all(),
            context_object_name='article_list'
        ),
        name='article_list',
    )
)
