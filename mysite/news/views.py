from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView

from .models import News, Category
from .forms import NewsForm, UserRegisterForm, UserLoginForm, ContactForm
from ipware import get_client_ip
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from django.contrib import messages
from django.contrib.auth import login, logout

from django.core.mail import send_mail
from django.conf import settings

import random


def identification(request):
    pass


def contact(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                mail = send_mail(form.cleaned_data['subject'], form.cleaned_data['content'], settings.EMAIL_HOST_USER, ['petrov.alexander.00@bk.ru'], fail_silently=False)
                if mail:
                    messages.success(request, 'Письмо отправлено!')
                    return redirect('contact')
                else:
                    messages.error(request, 'Ошибка отправки')
            else:
                messages.error(request, 'Ошибка валидации')
        else:
            form = ContactForm()
        return render(request, 'news/test.html', {"form": form})
    else:
        return user_login(request)


def register(request):
    ip, is_routable = get_client_ip(request)
    if ip is None:
        ip = '0.0.0.0'
    else:
        if is_routable:
            ipv = "Public"
        else:
            ipv = "Private"
    print(ip, ipv)

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            identification_code = random.randint(10000, 99999)
            mail = send_mail('Подтвердите регистрацию', str(identification_code), settings.EMAIL_HOST_USER,
                             [form.cleaned_data['email']], fail_silently=False)
            if mail:
                messages.success(request, 'Письмо отправлено!')
            else:
                messages.error(request, 'Ошибка отправки')


            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались')
            return redirect('home')

        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()

    return render(request, 'news/register.html', {"form": form})


def user_login(request):
    ip, is_routable = get_client_ip(request)
    if ip is None:
        ip = '0.0.0.0'
    else:
        if is_routable:
            ipv = "Public"
        else:
            ipv = "Private"
    print(ip, ipv)
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'news/login.html', {"form": form})


def user_logout(request):
    logout(request)
    return redirect('login')


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