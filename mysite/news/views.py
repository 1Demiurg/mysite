from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView

from .models import News, Category
from .forms import NewsForm
from ipware import get_client_ip
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

class HomeNews(ListView):
    model = News
    template_name = "news/index.html"
    context_object_name = "news"
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context

    def get_queryset(self):
        ip, is_routable = get_client_ip(self.request)
        if ip is None:
            ip = '0.0.0.0'
        else:
            if is_routable:
                ipv = "Public"
            else:
                ipv = "Private"
        print(ip, ipv)
        return News.objects.filter(is_published=True).select_related('category')


class NewsByCategory(ListView):
    model = News
    template_name = "news/index.html"
    context_object_name = "news"

    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Category.objects.get(pk=self.kwargs['category_id'])
        return context

    def get_queryset(self):
        return News.objects.filter(category_id=self.kwargs['category_id'], is_published=True).select_related('category')


class ViewNews(DetailView):
    model = News
    template_name = "news/view_news.html"
    context_object_name = "news_item"


class CreateNews(LoginRequiredMixin, CreateView):
    form_class = NewsForm
    template_name = "news/add_news.html"
    login_url = '/admin/'