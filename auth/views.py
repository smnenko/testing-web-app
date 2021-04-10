from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def authorize(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'auth/login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.first_name is not "" and user.last_name is not "":
                try:
                    request.session['test'] = int(user.first_name)
                    request.session['question'] = int(user.last_name)
                except ValueError:
                    pass
            return redirect('/')
        else:
            context = {
                'message': 'Неверный логин или пароль'
            }
            return render(request, 'auth/login.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeat_password = request.POST['repeat_password']
        if password != repeat_password:
            context = {
                'message': 'Пароли не совпадают, попробуйте ещё раз'
            }
            return render(request, 'auth/register.html', context)
        try:
            User.objects.create_user(username=username, email=email, password=password)
            context = {
                'message': 'Вы успешно зарегистрировались'
            }
            return render(request, 'auth/register.html', context)
        except:
            context = {
                'message': 'Во время регистрации произошла ошибка, введите другой юзернейм и попробуйте ещё раз'
            }
            return render(request, 'auth/register.html', context)
    elif request.method == 'GET':
        return render(request, 'auth/register.html')


def login_out(request):
    user = User.objects.get(username=request.user)
    try:
        test = request.session['test']
        question = request.session['question']
        user.first_name = test
        user.last_name = question
    except KeyError:
        user.first_name = ''
        user.last_name = ''
    user.save()
    logout(request)
    return redirect('/')


def index(request):
    if request.user.is_authenticated:
        context = {
            'authenticated': request.user.username
        }
        return render(request, 'auth/index.html', context)
    else:
        return render(request, 'auth/index.html')
