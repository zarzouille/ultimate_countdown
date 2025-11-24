import math
from datetime import datetime, timedelta


def _esc(s: str) -> str:
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def svg_preview(cfg: dict) -> str:
    """
    Génère le SVG d'aperçu pour la config donnée.
    Le layout du template 'circular' est calqué sur celui du GIF,
    y compris la compensation de baseline utilisée dans Pillow.
    """
    w = cfg["width"]
    h = cfg["height"]

    # --- Temps restant ---
    try:
        end = datetime.fromisoformat(cfg["target_date"])
    except Exception:
        end = datetime.utcnow() + timedelta(days=3)

    now = datetime.utcnow()
    remaining = int((end - now).total_seconds())
    if remaining <= 0:
        days = hours = minutes = seconds = 0
    else:
        days, rem = divmod(remaining, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)

    template = cfg.get("template", "circular")
    prefix = cfg.get("message_prefix", "")
    bg = cfg.get("background_color", "#FFFFFF")
    text_color = cfg.get("text_color", "#111111")
    show_labels = cfg.get("show_labels", True)

    units = [("J", days), ("H", hours), ("M", minutes), ("S", seconds)]

    # --- En-tête SVG ---
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="{bg}"/>'
    ]

    # Préfixe centré en haut
    if prefix:
        svg.append(
            f'<text x="{w/2}" y="26" text-anchor="middle" '
            f'font-family="system-ui, -apple-system, sans-serif" '
            f'font-size="18" font-weight="500" fill="{text_color}">{_esc(prefix)}</text>'
        )

    # ===================================================================
    # TEMPLATE CIRCULAR  (100% synchronisé avec renderer_gif.py)
    # ===================================================================
    if template == "circular":
        spacing = cfg["circular_spacing"]
        base_color = cfg["circular_base_color"]
        progress_color = cfg["circular_progress_color"]
        label_color = cfg["circular_label_color"]
        label_size = cfg["circular_label_size"]
        uppercase = cfg["circular_label_uppercase"]
        thickness = cfg["circular_thickness"]

        # Même logique de rayon que dans GIF (mais sans SCALE)
        padding = 40
        available_w = w - padding * 2
        count = 4
        radius = int((available_w - (count - 1) * spacing) / (count * 2))
        radius = max(radius, 20)

        # même position que GIF
        center_y = h / 2 + 4

        # ratios identiques
        ratios = [
            min(days / 30, 1.0),
            hours / 24 if hours >= 0 else 0,
            minutes / 60 if minutes >= 0 else 0,
            seconds / 60 if seconds >= 0 else 0,
        ]

        total_width = count * (2 * radius) + (count - 1) * spacing
        start_x = (w - total_width) / 2

        for i, ((label, val), ratio) in enumerate(zip(units, ratios)):
            cx = start_x + radius + i * (2 * radius + spacing)
            cy = center_y

            # cercle base
            svg.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
                f'stroke="{base_color}" stroke-width="{thickness}" '
                f'fill="none"/>'
            )

            # progression (stroke-dasharray)
            circ = 2 * math.pi * radius
            dash = max(0.0, min(ratio, 1.0)) * circ
            svg.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
                f'stroke="{progress_color}" stroke-width="{thickness}" '
                f'fill="none" stroke-dasharray="{dash} {circ - dash}" '
                f'transform="rotate(-90 {cx} {cy})"/>'
            )

            # valeur numérique
            #
            # ⬇️ Compensation identique à renderer_gif :
            #     text_y = cy - th * 0.56
            #
            # En SVG, on utilise dominant-baseline="central"
            # puis on applique un léger shift identique à GIF.
            #
            baseline_fix = cfg["font_size"] * 0.56
            text_y = cy - baseline_fix

            svg.append(
                f'<text x="{cx}" y="{text_y}" text-anchor="middle" '
                f'font-size="{cfg["font_size"]}" '
                f'dominant-baseline="middle" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'fill="{text_color}">{val:02d}</text>'
            )

            # label
            if show_labels:
                lbl = label.upper() if uppercase else label
                svg.append(
                    f'<text x="{cx}" y="{cy + radius + 16}" text-anchor="middle" '
                    f'font-size="{label_size}" '
                    f'font-family="system-ui, -apple-system, sans-serif" '
                    f'fill="{label_color}">{lbl}</text>'
                )

        svg.append("</svg>")
        return "\n".join(svg)

    # ===================================================================
    # TEMPLATE BASIC (inchangé)
    # ===================================================================
    main_size = cfg["font_size"]
    label_size = cfg["basic_label_size"]
    gap = cfg["basic_gap"]
    between = 18

    char_w = main_size * 0.7
    label_w = label_size * 0.6

    total_width = 0
    for label, val in units:
        num_w = 2 * char_w
        lab_w = label_w
        bw = max(num_w, lab_w)
        total_width += bw
    total_width += between * (len(units) - 1)

    center_y = h / 2 + 10
    start_x = (w - total_width) / 2
    x = start_x

    for label, val in units:
        num_w = 2 * char_w
        lab_w = label_w
        bw = max(num_w, lab_w)
        num_x = x + bw / 2

        # valeur
        svg.append(
            f'<text x="{num_x}" y="{center_y}" text-anchor="middle" '
            f'font-size="{main_size}" '
            f'font-family="system-ui, -apple-system, sans-serif" '
            f'fill="{text_color}">{val:02d}</text>'
        )

        # label
        if show_labels:
            svg.append(
                f'<text x="{num_x}" y="{center_y + main_size + gap}" text-anchor="middle" '
                f'font-size="{label_size}" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'fill="{cfg["basic_label_color"]}">{label}</text>'
            )

        x += bw + between

    svg.append("</svg>")
    return "\n".join(svg)