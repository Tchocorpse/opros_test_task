from django.contrib import admin
from django.urls import path

from questionnaire.views import GetActiveQuestionnaires, GetUserCompletedQuestionnaires, AnswerQuestionnaire

from rest_framework import permissions
from drf_yasg2.views import get_schema_view
from drf_yasg2 import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="API references",
      default_version='v1',
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('questionnaires/', GetActiveQuestionnaires.as_view()),
    path('answers/', GetUserCompletedQuestionnaires.as_view()),
    path('make_answers/', AnswerQuestionnaire.as_view()),

    #drf-yasg part
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
