"""Views — Corp Hauling verdiensten-tracker."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from esi.decorators import token_required

from .esi import CHAR_CONTRACTS_SCOPE, has_char_contracts_token
from .hauls import capture_hauls, haul_history, haul_stats, user_hauls


def _character_ids(user):
    try:
        from allianceauth.eveonline.models import EveCharacter

        return list(EveCharacter.objects.filter(character_ownership__user=user)
                    .values_list("character_id", flat=True))
    except Exception:  # noqa: BLE001
        return []


@login_required
@permission_required("corphauling.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """Haul-verdiensten, per maand — met een historie die zich opbouwt."""
    if not has_char_contracts_token(_character_ids(request.user)):
        return render(request, "corphauling/hauls.html", {"no_token": True})

    # Live ophalen, de afgeronde ritten vastleggen, dan de historie per maand lezen.
    live, _met = user_hauls(request.user)
    capture_hauls(request.user, live)
    maanden = haul_history(request.user)
    in_progress = [h for h in live if h["is_bezig"]]

    # Welke maand-tab is gekozen? Default = de nieuwste maand.
    keys = [m["key"] for m in maanden]
    gekozen = request.GET.get("maand")
    if gekozen not in keys:
        gekozen = keys[0] if keys else None

    actief = next((m for m in maanden if m["key"] == gekozen), None)
    maand_hauls = actief["hauls"] if actief else []
    # Lopende ritten horen bij 'nu', dus alleen op de nieuwste maand-tab tonen
    # (niet in een historische maand waar ze niet thuishoren).
    toon_bezig = in_progress if (not keys or gekozen == keys[0]) else []
    lijst = toon_bezig + maand_hauls

    return render(request, "corphauling/hauls.html", {
        "maanden": maanden,
        "gekozen": gekozen,
        "hauls": lijst,
        "stats": haul_stats(maand_hauls + toon_bezig),
        "heeft_historie": bool(maanden),
    })


@login_required
@permission_required("corphauling.basic_access")
@token_required(scopes=[CHAR_CONTRACTS_SCOPE])
def koppel_contracts(request: WSGIRequest, token) -> HttpResponse:
    """Je character koppelen zodat we je afgeleverde ritten kunnen lezen."""
    cache.delete(f"cc_charcontracts_{token.character_id}")
    messages.success(
        request,
        _("%(naam)s is gekoppeld — je haul-verdiensten worden nu getoond.")
        % {"naam": token.character_name},
    )
    return redirect("corphauling:index")
