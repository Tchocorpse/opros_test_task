from rest_framework import serializers

from questionnaire.models import Questionnaire, Question, Answer


class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_body', 'question_type',)


class ActualQuestionnairesSerializer(serializers.ModelSerializer):
    question = QuestionsSerializer(many=True)

    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'start_date', 'end_date', 'description', 'question',)


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'
