from ckeditor.widgets import CKEditorWidget
from django import forms
from core.models import Subject, Lesson, LessonDocs, Reading


# Subject
# ----------------------------------------------------------------------------------------------------------------------
class SubjectAdminForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(config_name='default'),
        }


# Lesson
# ----------------------------------------------------------------------------------------------------------------------
class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(config_name='default'),
        }


# Lesson
# ----------------------------------------------------------------------------------------------------------------------
class ReadingAdminForm(forms.ModelForm):
    class Meta:
        model = Reading
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(config_name='default'),
        }

