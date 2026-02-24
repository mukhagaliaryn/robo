from ckeditor.widgets import CKEditorWidget
from django import forms
from core.models import Course, Category, Module, Lesson


class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(config_name='default'),
        }


class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(config_name='default'),
        }
