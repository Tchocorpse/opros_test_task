from enum import Enum

from django.contrib.auth.models import User
from django.db import models


class QuestionTypeEnum(Enum):
    text = "text"
    choose_one = "choose_one"
    choose_many = "choose_many"


class Questionnaire(models.Model):
    name = models.CharField(
        verbose_name="Наименование", max_length=255, blank=False, null=False
    )
    start_date = models.DateTimeField(verbose_name="Дата начала", blank=False, null=False)
    end_date = models.DateTimeField(verbose_name="Дата окончания", blank=False, null=False)
    description = models.TextField(verbose_name="Описание", blank=True, null=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    question_body = models.CharField(verbose_name="Текст вопроса", max_length=255, blank=False, null=False)
    question_type = models.CharField(
        verbose_name="Тип вопроса",
        max_length=20,
        choices=[(tag.name, tag.value) for tag in QuestionTypeEnum],
        blank=False,
        null=False,
    )
    questionnaire = models.ManyToManyField(Questionnaire, related_name='question')

    def __str__(self):
        return self.question_body


class Answer(models.Model):
    user = models.IntegerField(verbose_name="Идентификатор пользователя", blank=True, null=True)
    answer_body = models.TextField(verbose_name="Ответ", blank=True, null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)

    def __str__(self):
        return self.answer_body
