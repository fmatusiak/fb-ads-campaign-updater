import html
import json


class AppError(Exception):
    def __init__(self, title, detail=None, context=None, meta=None, hint=None, cause=None):
        super().__init__(title)
        self.title = title
        self.detail = detail
        self.context = context or {}
        self.meta = meta or {}
        self.hint = hint
        self.cause = cause

    def to_text(self):
        lines = [self.title]

        if self.detail:
            lines.append(f"Co sie stalo: {self.detail}")

        if self.hint:
            lines.append(f"Co sprawdzic: {self.hint}")

        if self.context:
            lines.append("Czego dotyczy:")
            for key, value in self.context.items():
                if value not in (None, ""):
                    lines.append(f"- {key}: {value}")

        if self.meta:
            lines.append("Meta API:")
            for key, value in self.meta.items():
                if value not in (None, ""):
                    lines.append(f"- {key}: {value}")

        if self.cause:
            causeText = format_exception_for_display(self.cause)
            if causeText and causeText != self.title:
                lines.append("Przyczyna:")
                lines.extend(causeText.splitlines())

        return "\n".join(lines)

    def __str__(self):
        return self.to_text()


def create_http_error(operation, response, url=None):
    status = getattr(response, "status_code", None)
    responseText = getattr(response, "text", "")
    meta = {}
    detail = responseText

    try:
        payload = response.json()
    except Exception:
        payload = None

    if isinstance(payload, dict):
        error = payload.get("error", payload)
        if isinstance(error, dict):
            detail = error.get("message") or responseText
            meta = {
                "type": error.get("type"),
                "code": error.get("code"),
                "subcode": error.get("error_subcode"),
                "fbtrace_id": error.get("fbtrace_id"),
            }

    hint = explain_meta_error(detail, meta)
    context = {
        "krok": operation,
        "HTTP status": status,
        "URL": url,
    }

    return AppError(
        "Meta odrzucila zapytanie",
        detail=detail,
        context=context,
        meta=meta,
        hint=hint,
    )


def explain_meta_error(detail, meta=None):
    meta = meta or {}
    message = (detail or "").lower()
    code = meta.get("code")
    subcode = meta.get("subcode")

    if code in (190, 102) or "access token" in message or "session" in message:
        return (
            "token dostepu jest niewazny albo wygasl. Wygeneruj nowy access-token "
            "i upewnij sie, ze nalezy do tego samego Business Managera/konta reklamowego."
        )

    if code in (10, 200, 294) or "permission" in message or "permissions" in message:
        return (
            "brakuje uprawnien do tego zasobu. Sprawdz role uzytkownika, dostep aplikacji "
            "oraz uprawnienia ads_management/ads_read dla konta reklamowego."
        )

    if code in (4, 17, 32, 613) or "rate limit" in message or "too many calls" in message:
        return (
            "Meta ograniczyla liczbe zapytan. Odczekaj kilka minut i uruchom ponownie mniejsza paczke kampanii."
        )

    if subcode == 2446289 or "reel" in message or "rolka" in message:
        return (
            "kreacja wskazuje na rolke/post/material, ktory zostal usuniety albo nie jest dostepny "
            "dla tego konta. Sprawdz ID reklamy i kreacji w Menedzerze reklam."
        )

    if "advantage+" in message or "automated shopping" in message or "smart app" in message:
        return (
            "to wyglada na stary typ Advantage+ Shopping/App. W API v25 Meta blokuje aktualizacje "
            "legacy ASC/AAC; kampanie trzeba zmigrowac w Ads Managerze."
        )

    if "video_feeds" in message or "placement" in message:
        return (
            "problem dotyczy placementow w AdSecie. Sprawdz, czy kampania nie ma starego lub juz "
            "niewspieranego placementu."
        )

    if "daily_budget" in message or "budget" in message:
        return (
            "problem dotyczy budzetu. Sprawdz wartosc daily_budget w Excelu, walute konta i minimalny budzet Meta."
        )

    if (
        "targeting" in message
        or "custom_locations" in message
        or "latitude" in message
        or "longitude" in message
        or "radius" in message
    ):
        return (
            "problem dotyczy targetowania AdSetu. Sprawdz latitude, longitude i radius w Excelu "
            "oraz czy lokalizacja jest dozwolona dla kampanii."
        )

    if (
        "creative" in message
        or "object_story_spec" in message
        or "asset_feed_spec" in message
        or "degrees_of_freedom_spec" in message
    ):
        return (
            "problem dotyczy kreacji reklamy. Sprawdz teksty, URL, media oraz czy oryginalna kreacja "
            "nadal istnieje i jest dostepna dla konta."
        )

    if code == 100:
        return (
            "Meta odrzucila parametry zapytania. Najczesciej oznacza to niepoprawne ID, pole z Excela "
            "albo wartosc niedozwolona dla tego typu kampanii."
        )

    return None


def format_exception_for_display(error, context=None):
    lines = []

    if context:
        lines.append(str(context))

    if isinstance(error, AppError):
        lines.append(error.to_text())
    elif isinstance(error, Exception):
        lines.extend(_flatten_exception(error))
    else:
        lines.append(str(error))

    return "\n".join(line for line in lines if line)


def message_to_html(message):
    return html.escape(str(message)).replace("\n", "<br>")


def _flatten_exception(error):
    parts = []

    if not getattr(error, "args", None):
        return [str(error)]

    for arg in error.args:
        if isinstance(arg, AppError):
            parts.append(arg.to_text())
        elif isinstance(arg, Exception):
            parts.extend(_flatten_exception(arg))
        elif isinstance(arg, (list, tuple)):
            parts.extend(_flatten_sequence(arg))
        else:
            parts.append(_format_value(arg))

    if not parts:
        parts.append(str(error))

    return parts


def _flatten_sequence(values):
    parts = []

    for value in values:
        if isinstance(value, AppError):
            parts.append(value.to_text())
        elif isinstance(value, Exception):
            parts.extend(_flatten_exception(value))
        elif isinstance(value, (list, tuple)):
            parts.extend(_flatten_sequence(value))
        else:
            parts.append(_format_value(value))

    return parts


def _format_value(value):
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False, indent=2)
        except Exception:
            return str(value)

    return str(value)
