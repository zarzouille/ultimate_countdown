import os
import json
import uuid
import math
from datetime import datetime, timedelta
from io import BytesIO

from flask import Flask, render_template, request, send_file, url_for
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)

# ============================
# CONFIG PAR DÉFAUT
# ============================
DEFAULT_CONFIG = {
    "width": 600,
    "height": 200,
    "template": "circular",  # "basic" ou "circular"

    # Options communes
    "background_color": "#FFFFFF",
    "text_color": "#111111",
    "font_size": 32,
    "message_prefix": "Temps restant : ",
    "target_date": "2025-12-31T23:59:59",
    "show_labels": True,
    "loop_duration": 20,

    # Template CIRCULAR
    "circular_base_color": "#E0EAFF",
    "circular_progress_color": "#4C6FFF",
    "circular_thickness": 10,
    "circular_label_uppercase": True,
    "circular_label_size": 12,
    "circular_label_color": "#555555",
    "circular_spacing": 24,
    "circular_inner_ratio": 0.7,

    # Template BASIC
    "basic_label_color": "#666666",
    "basic_label_size": 12,
    "basic_gap": 4,
}

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

app = Flask(__name__)


# ============================
# OUTILS UTILITAIRES
# ============================

def cfg_path(cid: str) -> str:
    return os.path.join(CONFIG_DIR, f"{cid}.json")


def save_config(cid: str, cfg: dict):
    with open(cfg_path(cid), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_config(cid: str):
    path = cfg_path(cid)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    return cfg


def dt_for_input(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%dT%H:%M")
    except Exception:
        return iso_str[:16]


def parse_bool(val: str | None) -> bool:
    if not val:
        return False
    return val.lower() in ("1", "true", "on", "yes", "y")


def load_font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


# ============================
# ROUTE PRINCIPALE / SETTINGS
# ============================

@app.route("/", methods=["GET", "POST"])
def settings():
    cfg = DEFAULT_CONFIG.copy()
    img_link = None

    if request.method == "POST":
        form = request.form

        # Template
        tpl = form.get("template") or cfg["template"]
        if tpl not in ("basic", "circular"):
            tpl = "basic"
        cfg["template"] = tpl

        # Options communes
        td_raw = form.get("target_date", "").strip()
        if td_raw:
            iso = td_raw.replace(" ", "T")
            if len(iso) == 16:
                iso += ":00"
            cfg["target_date"] = iso

        cfg["message_prefix"] = form.get("message_prefix", cfg["message_prefix"])
        cfg["background_color"] = form.get("background_color", cfg["background_color"])
        cfg["text_color"] = form.get("text_color", cfg["text_color"])

        try:
            cfg["font_size"] = int(form.get("font_size", cfg["font_size"]))
        except Exception:
            pass

        cfg["show_labels"] = ("show_labels" in form)

        # CIRCULAR
        cfg["circular_base_color"] = form.get("circular_base_color", cfg["circular_base_color"])
        cfg["circular_progress_color"] = form.get("circular_progress_color", cfg["circular_progress_color"])
        try:
            cfg["circular_thickness"] = int(form.get("circular_thickness", cfg["circular_thickness"]))
        except Exception:
            pass
        cfg["circular_label_uppercase"] = ("circular_label_uppercase" in form)
        try:
            cfg["circular_label_size"] = int(form.get("circular_label_size", cfg["circular_label_size"]))
        except Exception:
            pass
        cfg["circular_label_color"] = form.get("circular_label_color", cfg["circular_label_color"])
        try:
            cfg["circular_spacing"] = int(form.get("circular_spacing", cfg["circular_spacing"]))
        except Exception:
            pass
        try:
            cfg["circular_inner_ratio"] = float(form.get("circular_inner_ratio", cfg["circular_inner_ratio"]))
        except Exception:
            pass

        # BASIC
        cfg["basic_label_color"] = form.get("basic_label_color", cfg["basic_label_color"])
        try:
            cfg["basic_label_size"] = int(form.get("basic_label_size", cfg["basic_label_size"]))
        except Exception:
            pass
        try:
            cfg["basic_gap"] = int(form.get("basic_gap", cfg["basic_gap"]))
        except Exception:
            pass

        # Crée un ID et sauvegarde
        cid = uuid.uuid4().hex[:8]
        save_config(cid, cfg)

        img_link = request.url_root.rstrip("/") + url_for("countdown_image", countdown_id=cid)

    target_date_value = dt_for_input(cfg["target_date"])

    return render_template(
        "settings.html",
        config=cfg,
        target_date=target_date_value,
        img_link=img_link,
    )


# ============================
# PREVIEW SVG LIVE
# ============================

@app.route("/preview.svg")
def preview_svg():
    cfg = DEFAULT_CONFIG.copy()
    args = request.args

    # Template
    tpl = args.get("template", cfg["template"])
    if tpl not in ("basic", "circular"):
        tpl = "basic"
    cfg["template"] = tpl

    # Options communes
    bg = args.get("background_color")
    if bg:
        cfg["background_color"] = bg
    tc = args.get("text_color")
    if tc:
        cfg["text_color"] = tc
    fs = args.get("font_size")
    if fs:
        try:
            cfg["font_size"] = int(fs)
        except Exception:
            pass
    mp = args.get("message_prefix")
    if mp is not None:
        cfg["message_prefix"] = mp
    cfg["show_labels"] = parse_bool(args.get("show_labels"))

    td_raw = args.get("target_date")
    if td_raw:
        iso = td_raw.replace(" ", "T")
        if len(iso) == 16:
            iso += ":00"
        cfg["target_date"] = iso

    # CIRCULAR
    cb = args.get("circular_base_color")
    if cb:
        cfg["circular_base_color"] = cb
    cp = args.get("circular_progress_color")
    if cp:
        cfg["circular_progress_color"] = cp
    cth = args.get("circular_thickness")
    if cth:
        try:
            cfg["circular_thickness"] = int(cth)
        except Exception:
            pass
    cfg["circular_label_uppercase"] = parse_bool(args.get("circular_label_uppercase"))
    cls = args.get("circular_label_size")
    if cls:
        try:
            cfg["circular_label_size"] = int(cls)
        except Exception:
            pass
    clc = args.get("circular_label_color")
    if clc:
        cfg["circular_label_color"] = clc
    csp = args.get("circular_spacing")
    if csp:
        try:
            cfg["circular_spacing"] = int(csp)
        except Exception:
            pass
    cir = args.get("circular_inner_ratio")
    if cir:
        try:
            cfg["circular_inner_ratio"] = float(cir)
        except Exception:
            pass

    # BASIC
    blc = args.get("basic_label_color")
    if blc:
        cfg["basic_label_color"] = blc
    bls = args.get("basic_label_size")
    if bls:
        try:
            cfg["basic_label_size"] = int(bls)
        except Exception:
            pass
    bgap = args.get("basic_gap")
    if bgap:
        try:
            cfg["basic_gap"] = int(bgap)
        except Exception:
            pass

    # Calcul du temps restant
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

    w = cfg["width"]
    h = cfg["height"]
    prefix = cfg["message_prefix"]
    show_labels = cfg["show_labels"]
    units = [("J", days), ("H", hours), ("M", minutes), ("S", seconds)]

    def esc(s: str) -> str:
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # TEMPLATE CIRCULAR (SVG)
    if tpl == "circular":
        radius = 32
        spacing = cfg["circular_spacing"]
        total_width = 4 * (radius * 2) + 3 * spacing
        start_x = (w - total_width) / 2
        cy = h / 2 + 8

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            f'<rect width="100%" height="100%" fill="{cfg["background_color"]}"/>'
        ]

        # Préfixe
        svg.append(
            f'<text x="{w/2}" y="26" text-anchor="middle" '
            f'font-family="system-ui, -apple-system, sans-serif" '
            f'font-size="14" fill="{cfg["text_color"]}">{esc(prefix)}</text>'
        )

        max_days = 30
        days_ratio = min(days / max_days, 1.0) if max_days > 0 else 1.0
        hours_ratio = hours / 24 if hours >= 0 else 0
        minutes_ratio = minutes / 60 if minutes >= 0 else 0
        seconds_ratio = seconds / 60 if seconds >= 0 else 0
        ratios = [days_ratio, hours_ratio, minutes_ratio, seconds_ratio]

        for i, ((label, val), ratio) in enumerate(zip(units, ratios)):
            cx = start_x + radius + i * (2 * radius + spacing)
            cy_local = cy

            # cercle de base
            svg.append(
                f'<circle cx="{cx}" cy="{cy_local}" r="{radius}" '
                f'stroke="{cfg["circular_base_color"]}" '
                f'stroke-width="{cfg["circular_thickness"]}" fill="none"/>'
            )

            # progression
            circ = 2 * math.pi * radius
            dash = max(0.0, min(ratio, 1.0)) * circ
            svg.append(
                f'<circle cx="{cx}" cy="{cy_local}" r="{radius}" '
                f'stroke="{cfg["circular_progress_color"]}" '
                f'stroke-width="{cfg["circular_thickness"]}" fill="none" '
                f'stroke-dasharray="{dash} {circ - dash}" '
                f'transform="rotate(-90 {cx} {cy_local})" />'
            )

            # valeur
            svg.append(
                f'<text x="{cx}" y="{cy_local+4}" text-anchor="middle" '
                f'font-size="{cfg["font_size"]}" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'fill="{cfg["text_color"]}" dominant-baseline="middle">{val:02d}</text>'
            )

            # label
            if show_labels:
                lbl = label.upper() if cfg["circular_label_uppercase"] else label
                svg.append(
                    f'<text x="{cx}" y="{cy_local+radius+14}" text-anchor="middle" '
                    f'font-size="{cfg["circular_label_size"]}" '
                    f'font-family="system-ui, -apple-system, sans-serif" '
                    f'fill="{cfg["circular_label_color"]}">{lbl}</text>'
                )

        svg.append("</svg>")
        return app.response_class("\n".join(svg), mimetype="image/svg+xml")

    # TEMPLATE BASIC (SVG)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="{cfg["background_color"]}"/>'
    ]

    svg.append(
        f'<text x="{w/2}" y="26" text-anchor="middle" '
        f'font-family="system-ui, -apple-system, sans-serif" '
        f'font-size="14" fill="{cfg["text_color"]}">{esc(prefix)}</text>'
    )

    center_y = h / 2 + 10
    main_size = cfg["font_size"]
    label_size = cfg["basic_label_size"]
    gap = cfg["basic_gap"]
    between = 18

    # Largeur approximative
    char_w = main_size * 0.7
    label_w = label_size * 0.6

    total_width = 0
    for label, val in units:
        num_w = 2 * char_w
        lab_w = label_w
        bw = max(num_w, lab_w)
        total_width += bw
    total_width += between * (len(units) - 1)
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
            f'fill="{cfg["text_color"]}">{val:02d}</text>'
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
    return app.response_class("\n".join(svg), mimetype="image/svg+xml")


# ============================
# DESSIN PILLOW (GIF, SUPER SAMPLING x4)
# ============================

def draw_circular_gif(draw, cfg, days, hours, minutes, seconds, remaining, total_initial, SCALE):
    W = cfg["width"] * SCALE
    H = cfg["height"] * SCALE

    padding = 30 * SCALE
    spacing = cfg["circular_spacing"] * SCALE

    available_w = W - padding * 2
    count = 4
    # 4 cercles + 3 espaces
    radius = int((available_w - 3 * spacing) / (count * 2))
    radius = max(radius, 20 * SCALE)

    center_y = H // 2 + 4 * SCALE
    thickness = max(1, cfg["circular_thickness"] * SCALE)

    units = [("J", days), ("H", hours), ("M", minutes), ("S", seconds)]
    max_days = 30
    days_ratio = min(days / max_days, 1.0) if max_days > 0 else 1.0
    hours_ratio = hours / 24 if hours >= 0 else 0
    minutes_ratio = minutes / 60 if minutes >= 0 else 0
    seconds_ratio = seconds / 60 if seconds >= 0 else 0
    ratios = [days_ratio, hours_ratio, minutes_ratio, seconds_ratio]

    font_big = load_font(cfg["font_size"] * SCALE)
    font_label = load_font(cfg["circular_label_size"] * SCALE)

    start_x = (W - (count * (radius * 2) + (count - 1) * spacing)) // 2

    # Préfixe
    prefix = cfg.get("message_prefix") or ""
    if prefix:
        font_prefix = load_font(int(cfg["font_size"] * 0.6) * SCALE)
        tw, th = draw.textsize(prefix, font=font_prefix)
        draw.text(
            ((W - tw) // 2, center_y - radius - th - 8 * SCALE),
            prefix,
            font=font_prefix,
            fill=cfg["text_color"],
        )

    for i, ((label, val), ratio) in enumerate(zip(units, ratios)):
        cx = start_x + radius + i * (2 * radius + spacing)
        cy = center_y

        # Cercle base
        draw.arc(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            start=0,
            end=359,
            fill=cfg["circular_base_color"],
            width=thickness,
        )

        # Progression
        end_angle = -90 + 360 * max(0.0, min(ratio, 1.0))
        draw.arc(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            start=-90,
            end=end_angle,
            fill=cfg["circular_progress_color"],
            width=thickness,
        )

        # Valeur
        num_txt = f"{val:02}"
        tw, th = draw.textsize(num_txt, font=font_big)
        draw.text(
            (cx - tw // 2, cy - th // 2),
            num_txt,
            font=font_big,
            fill=cfg["text_color"],
        )

        # Label
        if cfg["show_labels"]:
            lbl = label.upper() if cfg["circular_label_uppercase"] else label
            lw, lh = draw.textsize(lbl, font=font_label)
            draw.text(
                (cx - lw // 2, cy + radius + 8 * SCALE),
                lbl,
                font=font_label,
                fill=cfg["circular_label_color"],
            )


def draw_basic_gif(draw, cfg, days, hours, minutes, seconds, SCALE):
    W = cfg["width"] * SCALE
    H = cfg["height"] * SCALE

    main_font = load_font(cfg["font_size"] * SCALE)
    label_font = load_font(cfg["basic_label_size"] * SCALE)

    units = [("J", days), ("H", hours), ("M", minutes), ("S", seconds)]
    gap = cfg["basic_gap"] * SCALE
    show_labels = cfg["show_labels"]

    # Préfixe
    prefix = cfg.get("message_prefix") or ""
    if prefix:
        font_prefix = load_font(int(cfg["font_size"] * 0.6) * SCALE)
        tw, th = draw.textsize(prefix, font=font_prefix)
        draw.text(
            ((W - tw) // 2, 18 * SCALE),
            prefix,
            font=font_prefix,
            fill=cfg["text_color"],
        )

    # Mesure des blocs
    blocks = []
    between = 18 * SCALE
    total_w = 0

    for label, val in units:
        val_txt = f"{val:02}"
        tw, th = draw.textsize(val_txt, font=main_font)
        if show_labels:
            lw, lh = draw.textsize(label, font=label_font)
        else:
            lw = lh = 0
        bw = max(tw, lw)
        bh = th + (gap + lh if show_labels else 0)
        total_w += bw
        blocks.append({
            "label": label,
            "val": val_txt,
            "tw": tw,
            "th": th,
            "lw": lw,
            "lh": lh,
            "bw": bw,
            "bh": bh,
        })

    total_w += between * (len(blocks) - 1)
    center_y = H // 2 + 10 * SCALE
    x = (W - total_w) // 2

    for b in blocks:
        bw, bh = b["bw"], b["bh"]
        top = center_y - bh // 2

        # valeur
        vx = x + (bw - b["tw"]) // 2
        vy = top
        draw.text((vx, vy), b["val"], font=main_font, fill=cfg["text_color"])

        # label
        if show_labels:
            lx = x + (bw - b["lw"]) // 2
            ly = vy + b["th"] + gap
            draw.text((lx, ly), b["label"], font=label_font, fill=cfg["basic_label_color"])

        x += bw + between


# ============================
# GÉNÉRATION GIF FINALE
# ============================

@app.route("/c/<countdown_id>.gif")
def countdown_image(countdown_id):
    cfg = load_config(countdown_id)
    if cfg is None:
        return "Compte introuvable", 404

    try:
        end = datetime.fromisoformat(cfg["target_date"])
    except Exception:
        return "Date invalide", 400

    now = datetime.utcnow()
    total_initial = max(int((end - now).total_seconds()), 1)

    SCALE = 4
    frames = []

    for i in range(cfg.get("loop_duration", 20)):
        current = now + timedelta(seconds=i)
        remaining = int((end - current).total_seconds())

        big = Image.new(
            "RGB",
            (cfg["width"] * SCALE, cfg["height"] * SCALE),
            cfg["background_color"],
        )
        draw = ImageDraw.Draw(big)

        if remaining <= 0:
            txt = "⏰ Terminé !"
            font_big = load_font(cfg["font_size"] * SCALE)
            tw, th = draw.textsize(txt, font=font_big)
            draw.text(
                ((cfg["width"] * SCALE - tw) // 2, (cfg["height"] * SCALE - th) // 2),
                txt,
                font=font_big,
                fill=cfg["text_color"],
            )
        else:
            total_sec = remaining
            days, rem = divmod(total_sec, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, seconds = divmod(rem, 60)

            if cfg["template"] == "circular":
                draw_circular_gif(draw, cfg, days, hours, minutes, seconds, remaining, total_initial, SCALE)
            else:
                draw_basic_gif(draw, cfg, days, hours, minutes, seconds, SCALE)

        # Downscale pour un rendu ultra net
        final = big.resize((cfg["width"], cfg["height"]), Image.LANCZOS)
        frames.append(final)

    buf = BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=1000,
        loop=0,
    )
    buf.seek(0)
    return send_file(buf, mimetype="image/gif")


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)