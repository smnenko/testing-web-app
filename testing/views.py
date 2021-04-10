from django.shortcuts import render


def index(request):
    try:
        if request.user.is_authenticated:
            context = {
                'authenticated': request.user.username
            }
        else:
            return render(request, 'testing/index.html')

        return render(request, 'testing/index.html', context)
    except AttributeError:
        return render(request, 'testing/index.html')
