"""Tag dan filter template untuk komponen antarmuka PilihCuk."""
from django import forms, template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# ---------------------------------------------------------------------------
# Ikon (Lucide, lisensi ISC). Tambah ikon baru di sini lalu pakai {% icon "nama" %}.
# ---------------------------------------------------------------------------
ICONS = {
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "menu": '<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "minus": '<path d="M5 12h14"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "circle-check": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "circle-x": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "circle-alert": '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
    "circle-help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "triangle-alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "arrow-left": '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "log-out": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "external-link": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "trash-2": '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/>',
    "pencil": '<path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/>',
    "refresh-cw": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "layout-dashboard": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "shield-check": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
}


@register.simple_tag
def icon(name, size=20, css="", label=""):
    """Ikon SVG inline. Dekoratif (aria-hidden) kecuali `label` diisi.

    {% icon "check" %}  {% icon "x" 16 %}  {% icon "info" css="mr-2" label="Info" %}
    """
    body = ICONS.get(name)
    if body is None:
        return ""
    if label:
        aria = format_html('role="img" aria-label="{}"', label)
    else:
        aria = mark_safe('aria-hidden="true" focusable="false"')
    return format_html(
        '<svg class="icon {}" xmlns="http://www.w3.org/2000/svg" width="{}" height="{}" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" {}>{}</svg>',
        css, size, size, aria, mark_safe(body),
    )


# ---------------------------------------------------------------------------
# Badge skor. Nilai dari API dinormalisasi di sini juga, supaya template tidak
# pernah menampilkan "unknown" mentah.
# ---------------------------------------------------------------------------
SCORE_KINDS = {
    "nutri": {"name": "Nutri-Score", "allowed": "abcde", "css": "nutri"},
    "green": {"name": "Green-Score", "allowed": "abcde", "css": "green"},
    "nova": {"name": "NOVA", "allowed": "1234", "css": "nova"},
}
NOT_APPLICABLE = {"not-applicable", "not_applicable", "not applicable", "na", "n/a"}


def normalize_score(kind, value):
    """Kembalikan (state, grade). state: 'ok' | 'unknown' | 'na'."""
    if kind not in SCORE_KINDS:
        raise ValueError(f"Jenis skor tidak dikenal: {kind!r}")
    text = "" if value is None else str(value).strip().lower()
    if text in NOT_APPLICABLE:
        return "na", ""
    if len(text) == 1 and text in SCORE_KINDS[kind]["allowed"]:
        return "ok", text
    return "unknown", ""  # "", "unknown", None, dan nilai tak dikenal


@register.inclusion_tag("components/score_badge.html")
def score_badge(kind, value, size="md", estimate=False, label=False):
    """Badge skor.

    {% score_badge "nutri" product.nutriscore_grade %}
    {% score_badge "green" product.green_grade estimate=product.green_is_estimate label=True %}
    """
    state, grade = normalize_score(kind, value)
    info = SCORE_KINDS[kind]
    is_estimate = bool(estimate) and state == "ok"  # hanya nilai yang ada yang bisa "estimasi"
    if state == "ok":
        text = f"{info['name']} {grade.upper()}"
        glyph = grade.upper()
        label_text = "Estimasi" if is_estimate else ""
    elif state == "na":
        text = f"{info['name']} tidak berlaku"
        glyph = "\u2013"
        label_text = "Tidak berlaku"
    else:
        text = f"{info['name']} tidak diketahui"
        glyph = "?"
        label_text = "Tidak diketahui"
    if is_estimate:
        text += " (estimasi)"
    return {
        "css_kind": info["css"], "state": state, "grade": grade, "glyph": glyph,
        "aria_label": text, "size": size, "estimate": is_estimate,
        "label": label, "label_text": label_text,
    }


# ---------------------------------------------------------------------------
# Field formulir Django -> kelas komponen + atribut aksesibilitas
# ---------------------------------------------------------------------------
@register.filter
def control(bound_field):
    """{{ field|control }}: render widget dengan kelas .input/.select/.textarea."""
    widget = bound_field.field.widget
    attrs = {}
    if isinstance(widget, forms.Select) and not isinstance(widget, forms.RadioSelect):
        css = "select"
    elif isinstance(widget, forms.Textarea):
        css = "textarea"
    elif isinstance(widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
        css = ""
    else:
        css = "input"
    if bound_field.errors and css:
        css += " is-invalid"
    if css:
        attrs["class"] = css
    described = []
    if bound_field.help_text:
        described.append(f"{bound_field.auto_id}_help")
    if bound_field.errors:
        described.append(f"{bound_field.auto_id}_error")
        attrs["aria-invalid"] = "true"
    if described:
        attrs["aria-describedby"] = " ".join(described)
    return bound_field.as_widget(attrs=attrs)
