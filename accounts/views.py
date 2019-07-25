from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView, CreateView, View
from . forms import UserCreateForm, LoginForm


# Create your views here.

class IndexView(TemplateView):
    template_name = "accounts/index.html"


index = IndexView.as_view()

# ログイン


class Account_login(View):
    # template_name = "accounts/login.html"
    def post(self, request, *arg, **kwargs):
        if 'c_data' in request.POST:
            form = LoginForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                user = User.objects.get(username=username)
                login(request, user)
                login_user = request.user
                return redirect('c_data:user_detail', pk=login_user.id)
        if 'reservation' in request.POST:
            form = LoginForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                user = User.objects.get(username=username)
                login(request, user)
                login_user = request.user
                return redirect('reservation:index')
        return render(request, 'accounts/login.html', {'form': form, })

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        return render(request, 'accounts/login.html', {'form': form, })


account_login = Account_login.as_view()

# 新規作成


class Create_Account(CreateView):
    def post(self, request, *args, **kwargs):
        form = UserCreateForm(data=request.POST)
        if form.is_valid():
            form.save()
            # フォームから'username'を読み取る
            username = form.cleaned_data.get('username')
            # フォームから'password1'を読み取る
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/users/{}/'.format(user.id))
        return render(request, 'create.html', {'form': form, })

    def get(self, request, *args, **kwargs):
        form = UserCreateForm(request.POST)
        return render(request, 'create.html', {'form': form, })


create_account = Create_Account.as_view()
