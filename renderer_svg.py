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
    w = cfg["width"]
    h = cfg["height"]

    # Temps restant
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
    bg = cfg["background_color"]
    text_color = cfg["text_color"]
    show_labels = cfg["show_labels"]

    # Header SVG
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="{bg}"/>'
    ]

    if prefix:
        svg.append(
            f'<text x="{w/2}" y="26" text-anchor="middle" '
            f'font-size="18" font-family="system-ui" fill="{text_color}">{_esc(prefix)}</text>'
        )

    # =====================================================
    # CIRCULAR (match GIF)
    # =====================================================
    if template == "circular":
        spacing = cfg["circular_spacing"]
        base_color = cfg["circular_base_color"]
        progress_color = cfg["circular_progress_color"]
        thickness = cfg["circular_thickness"]
        label_color = cfg["circular_label_color"]
        label_size = cfg["circular_label_size"]
        uppercase = cfg["circular_label_uppercase"]
        inner_ratio = float(cfg.get("circular_inner_ratio", 0.7))

        # Protection identique
        inner_ratio = max(0.1, min(inner_ratio, 0.95))

        units = [("J", days), ("H", hours), ("M", minutes), ("S", seconds)]

        padding = 40
        available_w = w - padding * 2
        count = 4

        radius = int((available_w - (count - 1) * spacing) / (count * 2))
        radius = max(radius, 20)

        # Correction thickness identique au GIF
        if radius * inner_ratio + thickness >= radius:
            thickness = max(1, int(radius - radius * inner_ratio - 4))

        center_y = h / 2 + 4

        ratios = [
            min(days / 30, 1.0),
            min(hours / 24, 1.0),
            min(minutes / 60, 1.0),
            min(seconds / 60, 1.0),
        ]

        total_width = count * (2 * radius) + (count - 1) * spacing
        start_x = (w - total_width) / 2

        for i, ((label, val), ratio) in enumerate(zip(units, ratios)):
            cx = start_x + radius + i * (2 * radius + spacing)
            cy = center_y

            circ = 2 * math.pi * radius
            dash = max(0.0, min(ratio, 1.0)) * circ

            # Base
            svg.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
                f'stroke="{base_color}" stroke-width="{thickness}" fill="none"/>'
            )

            # Progression
            svg.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
                f'stroke="{progress_color}" stroke-width="{thickness}" fill="none" '
                f'stroke-dasharray="{dash} {circ - dash}" '
                f'transform="rotate(-90 {cx} {cy})"/>'
            )

            # Valeur centrée (match GIF)
            svg.append(
                f'<text x="{cx}" y="{cy+2}" text-anchor="middle" '
                f'font-size="{cfg["font_size"]}" '
                f'font-family="system-ui" fill="{text_color}" '
                f'dominant-baseline="middle">{val:02d}</text>'
            )

            # Label
            if show_labels:
                lbl = label.upper() if uppercase else label
                svg.append(
                    f'<text x="{cx}" y="{cy + radius + 14}" text-anchor="middle" '
                    f'font-size="{label_size}" '
                    f'font-family="system-ui" fill="{label_color}">{lbl}</text>'
                )

        svg.append("</svg>")
        return "\n".join(svg)

    # =====================================================
    # BASIC (inchangé)
    # =====================================================
    units = [("J", days), ("H", hours), ("M", minutes), ("S", seconds)]

    main_size = cfg["font_size"]
    label_size = cfg["basic_label_size"]
    gap = cfg["basic_gap"]
    between = 18

    char_w = main_size * 0.7
    label_w = label_size * 0.6

    total_width = 0
    for label, val in units:
        bw = max(2 * char_w, label_w)
        total_width += bw
    total_width += between * (len(units) - 1)

    center_y = h / 2 + 10
    x = (w - total_width) / 2

    for label, val in units:
        bw = max(2 * char_w, label_w)
        num_x = x + bw / 2

        svg.append(
            f'<text x="{num_x}" y="{center_y}" '
            f'text-anchor="middle" font-size="{main_size}" '
            f'font-family="system-ui" fill="{text_color}">{val:02d}</text>'
        )

        if show_labels:
            svg.append(
                f'<text x="{num_x}" y="{center_y + main_size + gap}" '
                f'text-anchor="middle" font-size="{label_size}" '
                f'font-family="system-ui" fill="{cfg["basic_label_color"]}">{label}</text>'
            )

        x += bw + between

    svg.append("</svg>")
    return "\n".join(svg)
