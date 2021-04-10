from django.urls import path
from .views import index, test, answer, delete, results


urlpatterns = [
    path('', index),
    path('test', test),
    path('answer', answer),
    path('results', results),
    path('delete', delete)
]
