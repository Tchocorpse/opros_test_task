from django.contrib import admin

from questionnaire.models import Questionnaire, Question, Answer


class QuestionInLine(admin.TabularInline):
    model = Question.questionnaire.through


class QuestionnaireAdmin(admin.ModelAdmin):
    model = Questionnaire
    inlines = [QuestionInLine]
    list_display = ('name', 'end_date', 'description')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('start_date',) + self.readonly_fields
        return self.readonly_fields


admin.site.register(Questionnaire, QuestionnaireAdmin)
admin.site.register(Question)
admin.site.register(Answer)
