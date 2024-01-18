from datetime import datetime

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .forms import *
from .models import User, Profile, Question, Answer


def paginate(content_list, request):
    paginator = Paginator(content_list, 10)

    page = request.GET.get("page")
    content_list = paginator.get_page(page)

    return content_list


def index_page(request):
    questions = Question.objects.new()[::-1]
    content = paginate(questions, request)
    return render(request, 'index.html', context={'questions': content})


@login_required()
def ask_page(request):
    if request.method == "GET":
        form = AskForm()

    if request.method == "POST":
        form = AskForm(data=request.POST)
        if form.is_valid():
            tags = form.save()
            profile = Profile.objects.filter(user=request.user).values("id")
            question = Question.objects.create(author_id=profile,
                                               title=form.cleaned_data["title"],
                                               text=form.cleaned_data["text"],
                                               date=datetime.today())
            for tag in tags:
                question.tags.add(tag)
                question.save()
            return redirect(f"/question/{question.id}")

    return render(request, 'ask.html', context={'form': form})


def login_page(request):
    next_page = request.GET.get('next_page', default="/")
    if request.user.is_authenticated:
        return redirect(next_page)

    if request.method == "GET":
        form = LoginForm()

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect(next_page)
            else:
                form.add_error(None, 'Invalid password and/or login')

    return render(request, 'login.html', context={'form': form, 'user': request.user})


def register_page(request):
    if request.method == "GET":
        form = SignUpForm()

    if request.method == "POST":
        form = SignUpForm(data=request.POST, files=request.FILES)
        print(form.files.get("avatar"))
        if form.is_valid():
            user = form.save()
            if form.files.get("avatar"):
                user.profile.avatar = form.files.get("avatar")
                user.profile.save()
            auth.login(request, user)
            return redirect("/")

    return render(request, "register.html", {"form": form})


def question_page(request, id):
    question = Question.objects.one_question(id)
    answers = Answer.objects.filter(question=question)
    content = paginate(answers, request)
    if request.method == "GET":
        form = AnswerForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('/login/')
        form = AnswerForm(data=request.POST)
        profile = Profile.objects.filter(user=request.user).values("id")
        if form.is_valid():
            Answer.objects.create(question_id=question.id,
                                  author_id=profile,
                                  text=form.cleaned_data["text"])
            return redirect(f"/question/{question.id}")

    return render(request, 'question.html', context={'form': form, "item": question, "content": content})


@login_required
def settings_page(request):
    if request.method == "GET":
        form = SettingsForm()

    if request.method == "POST":
        form = SettingsForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = request.user
            if user.is_authenticated:
                if form.cleaned_data["username"] != user.username and form.cleaned_data["username"] != "":
                    user.username = form.cleaned_data["username"]
                    user.save()
                    auth.login(request, user)
                    Profile.objects.filter(user=user).update(login=user.username)
                if form.cleaned_data["email"] != user.email and form.cleaned_data["email"] != "":
                    user.email = form.cleaned_data["email"]
                    user.save()
                    auth.login(request, user)
                if form.files.get("avatar"):
                    user.profile.avatar = form.files.get("avatar")
                    user.profile.save()

    return render(request, 'settings.html', context={'form': form})


@login_required
def logout(request):
    auth.logout(request)
    return redirect("/")
