from django import forms
from ckeditor.widgets import CKEditorWidget
from core.models import VideoTask, ReadingTask, Question, Option, MatchingPair


class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = VideoTask
        fields = '__all__'
        widgets = {
            'url': CKEditorWidget(config_name='default'),
        }


class ReadingAdminForm(forms.ModelForm):
    class Meta:
        model = ReadingTask
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(config_name='default'),
        }


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'text': CKEditorWidget(config_name='default'),
        }


class OptionAdminForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = '__all__'
        widgets = {
            'text': CKEditorWidget(config_name='default'),
        }


class MatchingPairAdminForm(forms.ModelForm):
    class Meta:
        model = MatchingPair
        fields = '__all__'
        widgets = {
            'left_text': CKEditorWidget(config_name='default'),
            'right_text': CKEditorWidget(config_name='default'),
        }
