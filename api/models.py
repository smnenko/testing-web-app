from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    questions_per_try = models.IntegerField('questions per try', default=15)
    percents_for_pass = models.FloatField('percents for pass', default=60)
    date_published = models.DateTimeField('date published', default=timezone.now)
    visible = models.BooleanField('is test visible', default=True)
    img_url = models.URLField('image url', default='https://spar.org.ua/img.php?ipt=https://images11.popmeh.ru/upload/img_cache/8e4/8e48d8427f00992897d21297a086e2e7_ce_1708x910x135x160.jpg')

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    title = models.TextField(max_length=200)

    def __str__(self):
        return self.title


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Answer(models.Model):
    attempt = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    choice = models.ForeignKey(Choice, on_delete=models.PROTECT)
    date_entered = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.test)


class UserTestAnswered(models.Model):
    attempt = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    total = models.FloatField(default=0)
    result = models.CharField(max_length=200)
    time_passing = models.TextField('time')

    def __str__(self):
        return str(self.test)


class UserTestQuestion(models.Model):
    attempt = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)

