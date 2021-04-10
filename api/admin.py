from django.contrib import admin
from django.contrib.auth.models import Group
from nested_inline.admin import NestedTabularInline, NestedModelAdmin
from .models import Test, Question, Choice, Answer, UserTestAnswered, UserTestQuestion


class ChoiceInstanceInline(NestedTabularInline):
    model = Choice


class QuestionInstanceInline(NestedTabularInline):
    model = Question
    extra = 1
    inlines = [ChoiceInstanceInline]


@admin.register(Test)
class TestAdmin(NestedModelAdmin):
    list_display = ['title', 'description', 'date_published', 'visible']
    list_filter = ['visible', 'date_published']
    inlines = [QuestionInstanceInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'question', 'choice', 'date_entered', 'attempt']
    list_filter = ['user', 'test', 'date_entered']


@admin.register(UserTestAnswered)
class UserTestAnsweredAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'total', 'result', 'time_passing', 'attempt']
    list_filter = ['user', 'test', 'total', 'result']


@admin.register(UserTestQuestion)
class UserTestQuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'question', 'attempt']


admin.site.unregister(Group)
