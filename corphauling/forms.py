"""Formulieren — Corp Hauling."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Piloot, Schip


class PilootForm(forms.ModelForm):
    """Je skills — die gelden voor al je schepen."""

    class Meta:
        model = Piloot
        fields = ("skills_uit_esi", "jdc", "jfc", "jf_skill", "rassen_skill")
        widgets = {
            "skills_uit_esi": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "jdc": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 5}),
            "jfc": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 5}),
            "jf_skill": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 5}),
            "rassen_skill": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 5}),
        }

    def _begrens(self, veld):
        return min(5, max(0, self.cleaned_data[veld]))

    def clean_jdc(self):
        return self._begrens("jdc")

    def clean_jfc(self):
        return self._begrens("jfc")

    def clean_jf_skill(self):
        return self._begrens("jf_skill")

    def clean_rassen_skill(self):
        return self._begrens("rassen_skill")


class SchipForm(forms.ModelForm):
    """Eén jump freighter met z'n fit."""

    class Meta:
        model = Schip
        fields = ("schip_type_id", "naam", "fit", "hold_handmatig")
        widgets = {
            "schip_type_id": forms.Select(attrs={"class": "form-select"}),
            "naam": forms.TextInput(attrs={"class": "form-control",
                                           "placeholder": _("bijv. grote hauler")}),
            "fit": forms.Textarea(attrs={
                "class": "form-control", "rows": 7,
                "placeholder": (
                    "[Rhea, mijn hauler]\n"
                    "Expanded Cargohold II\n"
                    "Expanded Cargohold II\n"
                    "Expanded Cargohold II"
                ),
            }),
            "hold_handmatig": forms.NumberInput(attrs={"class": "form-control",
                                                       "min": 0, "step": 1000}),
        }
