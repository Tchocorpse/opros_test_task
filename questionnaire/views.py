import datetime
import logging

from django.http import JsonResponse
from django.utils import timezone
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView

from questionnaire.models import Questionnaire, Answer, Question
from questionnaire.serializers import ActualQuestionnairesSerializer, AnswersSerializer


class GetActiveQuestionnaires(APIView):
    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                in_="query",
                name="date",
                type="string",
                description="optional date to specify actual questionnaries. Default is datetime.datetime.now(tz=timezone.utc).",
            )
        ],
        responses={status.HTTP_200_OK: ActualQuestionnairesSerializer,},
    )
    @action(detail=False, methods=["GET"])
    def get(self, request):
        try:
            target_date = request.GET["date"]
        except KeyError:
            target_date = datetime.datetime.now(tz=timezone.utc)

        actual_questionnaires = Questionnaire.objects.prefetch_related(
            "question"
        ).filter(start_date__lte=target_date, end_date__gte=target_date)

        serialized_data = ActualQuestionnairesSerializer(
            actual_questionnaires, many=True
        ).data
        return JsonResponse({"active_questionnaires": serialized_data}, status=200)


class GetUserCompletedQuestionnaires(APIView):
    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                in_="query",
                name="user_id",
                type="number",
                description="special id to identify anonymous or actual user.",
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "answered_questionnaires": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Json with questionnaires",
                        properties={
                            "questionnaire": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                description="questionnaire name",
                                additional_properties=openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Mapped questions and answers",
                                    ),

                            ),
                        },
                    ),
                },
            ),
        },
    )
    @action(detail=False, methods=["GET"])
    def get(self, request):
        try:
            target_user_id = request.GET["user_id"]
        except KeyError:
            return JsonResponse(
                {"error": "missing or invalid user_id in request querystring"},
                status=400,
            )

        user_answers_raw = Answer.objects.select_related(
            "questionnaire", "question"
        ).filter(user=target_user_id)
        if not user_answers_raw:
            return JsonResponse(
                {"answers": f"no answers found for user_id {target_user_id}"},
                status=200,
            )

        result_dict = {}
        for answer in user_answers_raw:
            try:
                result_dict[answer.questionnaire.name][
                    answer.question.question_body
                ] = answer.answer_body
            except KeyError:
                result_dict.update(
                    {
                        answer.questionnaire.name: {
                            answer.question.question_body: answer.answer_body
                        }
                    }
                )

        return JsonResponse({"answered_questionnaires": result_dict}, status=200)


answer_questionnaire_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["user_id", "answers_data"],
    properties={
        "user_id": openapi.Schema(
            type=openapi.TYPE_NUMBER, description="numeric user id"
        ),
        "answers_data": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Json with questions and questionnaire data",
            properties={
                "questionnaire": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="questionnaire id",
                ),
            },
            additional_properties=openapi.Schema(
                type=openapi.TYPE_STRING,
                description="mapped question id to answer string",

            ),
        ),
    },
)


class AnswerQuestionnaire(APIView):
    @swagger_auto_schema(
        method="post",
        request_body=answer_questionnaire_schema,
        responses={status.HTTP_200_OK: AnswersSerializer,},
    )
    @action(detail=False, methods=["POST"])
    def post(self, request):
        try:
            user_id = request.data["user_id"]
        except KeyError:
            return JsonResponse(
                {"error": "missing or invalid user_id in request json"}, status=400
            )

        try:
            answers_data = request.data["answers_data"]
        except KeyError:
            return JsonResponse(
                {"error": "missing or invalid answers_data in request json"}, status=400
            )

        questionnaire_id = answers_data["questionnaire"]
        try:
            questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
        except Questionnaire.DoesNotExist:
            return JsonResponse(
                {"error": f"no such questionnaire with id {questionnaire_id}"},
                status=400,
            )

        questions = Question.objects.filter(questionnaire=questionnaire_id)

        answers_list = []
        for question in questions:
            try:
                answer_str = answers_data[str(question.id)]
            except KeyError:
                return JsonResponse(
                    {"error": f"missing answered question with id {question.id} "},
                    status=400,
                )
            answer = Answer(
                user=user_id,
                answer_body=answer_str,
                questionnaire=questionnaire,
                question=question,
            )
            answers_list.append(answer)

        self.save_models(answers_list)

        serialized_data = AnswersSerializer(answers_list, many=True).data
        return JsonResponse({"answered_questionnaire": serialized_data}, status=200)

    def save_models(self, model_list):
        for model in model_list:
            model.save()
