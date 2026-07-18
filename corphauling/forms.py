"""Formulieren — Corp Hauling."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CorpFit, Schip


class SchipForm(forms.ModelForm):
    """Eén jump freighter: kies een corp-fit, de rest volgt daaruit."""

    class Meta:
        model = Schip
        fields = ("corp_fit", "naam")
        widgets = {
            "corp_fit": forms.Select(attrs={"class": "form-select"}),
            "naam": forms.TextInput(attrs={"class": "form-control",
                                           "placeholder": _("bijv. grote hauler")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["corp_fit"].queryset = CorpFit.objects.all()
        self.fields["corp_fit"].required = True
        self.fields["corp_fit"].empty_label = _("— kies een fit —")
        self.fields["corp_fit"].help_text = _(
            "Het schip volgt uit de fit. Staat de jouwe er niet bij? Vraag een "
            "beheerder om 'm toe te voegen."
        )
