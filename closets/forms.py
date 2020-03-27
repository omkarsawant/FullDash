from django import forms
from .models import Closets
from overview.models import Overview


class ClosetsCreateForm(forms.ModelForm):
    class Meta:
        model = Closets
        fields = ['floor',
                  'category',
                  ]


class ClosetsCreateBaseModelFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)


ClosetsCreateFormset = forms.modelformset_factory(
    Closets, can_delete=True, extra=1, form=ClosetsCreateForm, formset=ClosetsCreateBaseModelFormset)
