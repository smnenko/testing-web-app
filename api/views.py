from django.shortcuts import render, redirect, HttpResponse

from .models import Test, Question, Choice, Answer, UserTestAnswered, UserTestQuestion
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from random import shuffle


# Create your views here.
# TODO выбираю тест без артибутов в сессии крашится прога --- completed
# TODO нужно заключение по тесту т.е. вы ответили на столько-то правильных вопросов из столькито --- completed
# TODO в админпанели показывать % правильных вопросов --- completed
# TODO мешать вопросы и ответы в рандомном порядке --- completed
# TODO несколько попыток в тесте --- completed

@login_required(login_url='/login')
def results(request):
    if request.method == 'POST':
        request.session['result'] = request.POST['test']
        return redirect('/api/results')
    elif request.method == 'GET':
        try:
            test = request.session['result']
            test_instance = Test.objects.filter(pk=test)[0]
            user_test_answered = UserTestAnswered.objects.filter(user=request.user, test=test_instance)[::-1]

            if len(user_test_answered) > 0:
                context = {
                    'tests': user_test_answered
                }
                return render(request, 'api/results.html', context)
            else:
                context = {
                    'message': 'Ответов на данный тест не найдено'
                }
                return render(request, 'api/results.html', context)
        except KeyError:
            return redirect('/api')
        except ValueError:
            return redirect('/api')


@login_required(login_url='/login')
def test(request):
    if request.method == 'POST':
        test = request.POST['test']
        try:
            current = request.session['test']
            if test == current:
                return redirect('/api/test')
            else:
                context = {
                    'unavailable': Test.objects.filter(pk=test)[0]
                }
                return render(request, 'api/test.html', context)
        except KeyError:
            request.session['test'] = test
            request.session['question'] = 1

            test_instance = Test.objects.filter(pk=test)[0]
            attempt = UserTestAnswered.objects.filter(user=request.user, test=test_instance).count()
            questions = list(Question.objects.filter(test=test_instance))
            shuffle(questions)

            for question in questions:
                user_test_question = UserTestQuestion(attempt=attempt + 1, user=request.user, test=test_instance, question=question)
                user_test_question.save_base()

            return redirect('/api/test')

    elif request.method == 'GET':
        try:
            test = request.session['test']
            test_instance = Test.objects.filter(pk=test)[0]
            question_count = test_instance.questions_per_try

            question = int(request.session['question'])
            attempt = UserTestAnswered.objects.filter(user=request.user, test=test_instance).count()

            question_instance = UserTestQuestion.objects.filter(attempt=attempt + 1, user=request.user, test=test_instance)[question - 1]
            choices = list(Choice.objects.filter(question=question_instance.question))
            shuffle(choices)
            context = {
                'test': test,
                'question': question_instance.question,
                'question_number': question,
                'choices': choices,
                'number': question,
                'count': question_count
            }
            return render(request, 'api/test.html', context)
        except KeyError:
            test = request.session['result']
            test_instance = Test.objects.filter(pk=test)[0]
            user_test_answered = UserTestAnswered.objects.filter(user=request.user, test=test_instance)[::-1]
            context = {
                'tests': user_test_answered
            }
            return render(request, 'api/results.html', context)


@login_required(login_url='/login')
def answer(request):
    try:
        if request.method == 'POST':
            test = request.POST['test']
            question = int(request.POST['question'])
            answer = int(request.POST['answer'])

            test_instance = Test.objects.filter(pk=test)[0]
            attempt = UserTestAnswered.objects.filter(user=request.user, test=test_instance).count()

            question_instance = \
            UserTestQuestion.objects.filter(attempt=attempt + 1, user=request.user, test=test_instance)[
                question - 1].question
            choice_instance = Choice.objects.filter(question=question_instance, title=answer)[0]
            questions_count = Question.objects.filter(test=test_instance).count()

            ans = Answer(attempt=attempt + 1, user=request.user, test=test_instance, question=question_instance,
                         choice=choice_instance, date_entered=timezone.now())
            ans.save_base()

            if request.session['question'] == questions_count:
                right_answers = 0
                for a in Answer.objects.filter(attempt=attempt + 1, user=request.user, test=test_instance):
                    if a.choice.correct:
                        right_answers += 1
                total = round(right_answers / test_instance.questions_per_try * 100, 1)
                result = 'Not passed'
                if total >= test_instance.percents_for_pass:
                    result = 'Passed'
                time_passing = Answer.objects.filter(attempt=attempt + 1, user=request.user, test=test_instance)[
                                   question - 1].date_entered - \
                               Answer.objects.filter(attempt=attempt + 1, user=request.user, test=test_instance)[
                                   0].date_entered
                user_test_answered = UserTestAnswered(attempt=attempt + 1, user=request.user, test=test_instance,
                                                      total=total, result=result, time_passing=time_passing)
                user_test_answered.save_base()

                request.session['result'] = request.session['test']
                del request.session['test']
                del request.session['question']

                return render(request, 'api/results.html')

            request.session['question'] += 1
            return HttpResponse('200 OK')
        elif request.method == 'GET':
            return redirect('/api/results')
    except IndexError:
        pass



@login_required(login_url='/login')
def index(request):
    tests = Test.objects.filter(visible=True)

    try:
        context = {
            'tests': tests,
            'uncompleted': Test.objects.filter(pk=request.session['test'])[0]
        }
    except KeyError:
        context = {
            'tests': tests
        }
    return render(request, 'api/api.html', context)


@login_required(login_url='/login')
def delete(request):
    if request.method == 'POST':
        test_instance = Test.objects.filter(pk=request.session['test'])[0]

        attempt = UserTestAnswered.objects.filter(user=request.user, test=test_instance).count()
        right_answers = 0
        for a in Answer.objects.filter(attempt=attempt + 1, user=request.user, test=test_instance):
            if a.choice.correct:
                right_answers += 1
        total = round(right_answers / test_instance.questions_per_try * 100, 1)
        result = 'Not passed'
        if total >= test_instance.percents_for_pass:
            result = 'Passed'

        try:
            time_passing = Answer.objects.filter(user=request.user, test=test_instance)[
                               int(request.session['question']) - 2].date_entered - \
                           Answer.objects.filter(user=request.user, test=test_instance)[0].date_entered
        except AssertionError:
            time_passing = 'None'
        user_test_answered = UserTestAnswered(attempt=attempt + 1, user=request.user, test=test_instance, total=total,
                                              result=result, time_passing=time_passing)
        user_test_answered.save_base()

        del request.session['test']
        del request.session['question']
        return redirect('/api')
    elif request.method == 'GET':
        return redirect('/api')
