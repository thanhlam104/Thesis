from django import forms
from .models import *

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

from django.forms import ClearableFileInput

class ProjectModelForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class FileModelForm(forms.ModelForm):
    class Meta:
        model = FileObject
        fields = ['file']
        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True}),
        }
class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.display_name
class NodeCreateForm(forms.Form):
    def __init__(self, *args, project=None, **kwargs):
        super(NodeCreateForm, self).__init__(*args, **kwargs)
        
        if project is not None:
            self.fields['file'].queryset = project.fileobject_set.all()
    name = forms.CharField(label='Node label', max_length=100)
    file = CustomModelChoiceField(queryset=None)
    property = forms.CharField(label='Node label')
    column = forms.ChoiceField(label='Column name')
