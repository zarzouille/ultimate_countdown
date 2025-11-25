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

    # -----------------------------
    # 1) Récupération du temps restant
    # -----------------------------
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

    # Gras
    prefix_weight = "700" if cfg.get("prefix_bold") else "500"
    number_weight = "700" if cfg.get("font_bold") else "500"
    label_weight = "700" if cfg.get("label_bold") else "500"

    units = [("J", days), ("H", hours), ("M", minutes), ("S", seconds)]

    # -----------------------------
    # 2) Structure SVG
    # -----------------------------
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="{bg}"/>'
    ]

    # -----------------------------
    # 3) Préfixe
    # -----------------------------
    if prefix:
        svg.append(
            f'<text x="{w/2}" y="26" text-anchor="middle" '
            f'font-family="system-ui, -apple-system, sans-serif" '
            f'font-size="18" font-weight="{prefix_weight}" '
            f'fill="{text_color}">{_esc(prefix)}</text>'
        )

    # -----------------------------
    # 4) TEMPLATE CIRCULAR
    # -----------------------------
    if template == "circular":
        spacing = cfg["circular_spacing"]
        base_color = cfg["circular_base_color"]
        progress_color = cfg["circular_progress_color"]
        label_color = cfg["circular_label_color"]
        label_size = cfg["circular_label_size"]
        uppercase = cfg["circular_label_uppercase"]
        thickness = cfg["circular_thickness"]

        padding = 40
        available_w = w - padding * 2
        count = 4

        radius = int((available_w - (count - 1) * spacing) / (count * 2))
        radius = max(radius, 20)

        center_y = h / 2 + 4

        max_days = 30
        ratios = [
            min(days / max_days, 1.0),
            hours / 24,
            minutes / 60,
            seconds / 60,
        ]

        total_width = count * (2 * radius) + (count - 1) * spacing
        start_x = (w - total_width) / 2

        for i, ((label, val), ratio) in enumerate(zip(units, ratios)):
            cx = start_x + radius + i * (2 * radius + spacing)
            cy = center_y

            # Cercle base
            svg.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
                f'stroke="{base_color}" stroke-width="{thickness}" fill="none"/>'
            )

            # Progression
            circ = 2 * math.pi * radius
            dash = max(0.0, min(ratio, 1.0)) * circ

            svg.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
                f'stroke="{progress_color}" stroke-width="{thickness}" fill="none" '
                f'stroke-dasharray="{dash} {circ - dash}" '
                f'transform="rotate(-90 {cx} {cy})"/>'
            )

            # Valeur
            svg.append(
                f'<text x="{cx}" y="{cy+4}" text-anchor="middle" '
                f'font-size="{cfg["font_size"]}" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'font-weight="{number_weight}" '
                f'fill="{text_color}" dominant-baseline="middle">{val:02d}</text>'
            )

            # Label
            if show_labels:
                lbl = label.upper() if uppercase else label
                svg.append(
                    f'<text x="{cx}" y="{cy + radius + 32}" text-anchor="middle" '
                    f'font-size="{label_size}" '
                    f'font-family="system-ui, -apple-system, sans-serif" '
                    f'font-weight="{label_weight}" '
                    f'fill="{label_color}">{lbl}</text>'
                )

        svg.append("</svg>")
        return "\n".join(svg)

    # -----------------------------
    # 5) TEMPLATE BASIC (inchangé)
    # -----------------------------
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

        svg.append(
            f'<text x="{num_x}" y="{center_y}" text-anchor="middle" '
            f'font-size="{main_size}" '
            f'font-family="system-ui, -apple-system, sans-serif" '
            f'font-weight="{number_weight}" '
            f'fill="{text_color}">{val:02d}</text>'
        )

        if show_labels:
            svg.append(
                f'<text x="{num_x}" y="{center_y + main_size + gap}" text-anchor="middle" '
                f'font-size="{label_size}" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'font-weight="{label_weight}" '
                f'fill="{cfg["basic_label_color"]}">{label}</text>'
            )

        x += bw + between

    svg.append("</svg>")
    return "\n".join(svg)