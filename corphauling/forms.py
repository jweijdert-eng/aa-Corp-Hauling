"""Formulieren — Corp Hauling."""

import re

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CorpFit


class CorpFitForm(forms.ModelForm):
    """Corp-fit toevoegen: plak het EFT-blok, de rest leiden we eruit af."""

    class Meta:
        model = CorpFit
        fields = ("naam", "schip_type_id", "fit", "volgorde")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Beide zijn af te leiden uit de kopregel van de fit.
        self.fields["schip_type_id"].required = False
        self.fields["naam"].required = False
        self.fields["fit"].help_text = _(
            "Plak het blok zoals je het in EVE kopieert, inclusief de regel "
            "[Rhea, naam]. Schip en naam worden daaruit overgenomen als je ze "
            "hierboven leeg laat."
        )

    def clean(self):
        from .fit import cargo_multiplier, parse_eft
        from .models import Piloot

        data = super().clean()
        fit = (data.get("fit") or "").strip()
        if not fit:
            return data

        # Kopregel: [Rhea, ORE Expanded Cargohold]
        kop = re.match(r"^\s*\[([^,\]]+)(?:,\s*([^\]]*))?\]", fit)
        schip_naam = (kop.group(1).strip() if kop else "")
        fit_naam = (kop.group(2).strip() if kop and kop.group(2) else "")

        if not data.get("schip_type_id"):
            treffer = next((tid for tid, label in Piloot.SCHEPEN
                            if label.lower().startswith(schip_naam.lower())), None)
            if not treffer:
                raise forms.ValidationError(
                    _("Kon het schip niet uit de fit halen. Kies het hierboven, of zorg "
                      "dat de eerste regel begint met [Ark, ...], [Anshar, ...], "
                      "[Nomad, ...] of [Rhea, ...]."))
            data["schip_type_id"] = treffer

        if not data.get("naam"):
            label = dict(Piloot.SCHEPEN).get(data["schip_type_id"], "").split(" (")[0]
            data["naam"] = f"{label} — {fit_naam}" if fit_naam else label

        # Geen enkele cargo-module herkend? Dan levert de fit niets op.
        _mult, modules = cargo_multiplier(parse_eft(fit))
        if not modules:
            self.add_error("fit", _(
                "In deze fit staat geen module die de vrachtruimte vergroot. "
                "Kloppen de modulenamen? (Controleer de spelling zoals in EVE.)"))
        return data
