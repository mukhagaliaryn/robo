from ckeditor.widgets import CKEditorWidget
from django import forms
from core.models import Book


# Subject
# ----------------------------------------------------------------------------------------------------------------------
class BookAdminForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(config_name='default'),
        }