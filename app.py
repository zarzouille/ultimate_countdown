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
    "width": 400,
    "height": 160,
    "template": "basic",  # "basic" ou "circular"

    # Options communes
    "background_color": "#FFFFFF",
    "text_color": "#111111",
    "font_size": 32,
    "message_prefix": "Temps restant : ",
    "target_date": "2025-12-31T23:59:59",
    "show_labels": True,
    "loop_duration": 20,  # nb d'images -> 20s d'animation

    # Template CIRCULAR
    "circular_base_color": "#E0EAFF",
    "circular_progress_color": "#4C6FFF",
    "circular_thickness": 6,
    "circular_label_uppercase": True,
    "circular_label_size": 11,
    "circular_label_color": "#555555",
    "circular_spacing": 12,
    "circular_inner_ratio": 0.7,

    # Template BASIC
    "basic_label_color": "#666666",
    "basic_label_size": 11,
    "basic_gap": 4,
}

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

app = Flask(__name__)


# ============================
# OUTILS CONFIG
# ============================

def cfg_path(cid: str) -> str:
    return os.path.join(CONFIG_DIR, f"{cid}.json")


def save_config(cid: str, cfg: dict) -> None:
    with open(cfg_path(cid), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_config(cid: str):
    path = cfg_path(cid)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
    except Exception:
        return None
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    return cfg


def dt_for_input(iso_str: str) -> str:
    """
    Transforme "2025-12-31T23:59:59" en "2025-12-31T23:59"
    compatible avec <input type="datetime-local">
    """
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

        # Template choisi
        tpl = form.get("template") or cfg["template"]
        if tpl not in ("basic", "circular"):
            tpl = "basic"
        cfg["template"] = tpl

        # Options communes
        raw_date = form.get("target_date", "").strip()
        if raw_date:
            iso = raw_date.replace(" ", "T")
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

        cfg["show_labels"] = bool(form.get("show_labels"))

        # CIRCULAR
        cfg["circular_base_color"] = form.get("circular_base_color", cfg["circular_base_color"])
        cfg["circular_progress_color"] = form.get("circular_progress_color", cfg["circular_progress_color"])
        try:
            cfg["circular_thickness"] = int(form.get("circular_thickness", cfg["circular_thickness"]))
        except Exception:
            pass
        cfg["circular_label_uppercase"] = bool(form.get("circular_label_uppercase"))
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

        # On crée un nouvel ID & on stocke
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
# DESSIN PILLOW (GIF)
# ============================

def draw_centered_text(draw: ImageDraw.ImageDraw, cfg: dict, text: str, font, fill=None):
    w, h = cfg["width"], cfg["height"]
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (w - tw) // 2
    y = (h - th) // 2
    draw.text((x, y), text, font=font, fill=fill or cfg["text_color"])


def draw_basic(draw: ImageDraw.ImageDraw, cfg: dict, days: int, hours: int, minutes: int, seconds: int):
    w, h = cfg["width"], cfg["height"]
    main_font = load_font(cfg["font_size"])
    label_font = load_font(cfg["basic_label_size"])

    show_labels = cfg["show_labels"]
    gap = cfg["basic_gap"]
    label_color = cfg["basic_label_color"]

    units = [
        ("J", days),
        ("H", hours),
        ("M", minutes),
        ("S", seconds),
    ]

    blocks = []
    total_w = 0
    between = 18

    for label, val in units:
        val_txt = f"{val:02}"
        tb = draw.textbbox((0, 0), val_txt, font=main_font)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]

        if show_labels:
            lb = draw.textbbox((0, 0), label, font=label_font)
            lw = lb[2] - lb[0]
            lh = lb[3] - lb[1]
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
            "bh": bh
        })

    total_w += between * (len(blocks) - 1)
    x = (w - total_w) // 2
    center_y = h // 2 + 10

    for b in blocks:
        bw, bh = b["bw"], b["bh"]
        top = center_y - bh // 2

        # nombre
        val_x = x + (bw - b["tw"]) // 2
        val_y = top
        draw.text((val_x, val_y), b["val"], font=main_font, fill=cfg["text_color"])

        # label
        if show_labels:
            label_x = x + (bw - b["lw"]) // 2
            label_y = val_y + b["th"] + gap
            draw.text((label_x, label_y), b["label"], font=label_font, fill=label_color)

        x += bw + between

    # Préfixe au-dessus
    prefix = cfg.get("message_prefix") or ""
    if prefix:
        pf = load_font(max(10, int(cfg["font_size"] * 0.5)))
        pb = draw.textbbox((0, 0), prefix, font=pf)
        pw = pb[2] - pb[0]
        ph = pb[3] - pb[1]
        px = (w - pw) // 2
        py = center_y - (blocks[0]["bh"] // 2) - ph - 4
        draw.text((px, max(4, py)), prefix, font=pf, fill=cfg["text_color"])


def draw_circular(draw: ImageDraw.ImageDraw, cfg: dict, days: int, hours: int, minutes: int, seconds: int):
    w, h = cfg["width"], cfg["height"]
    main_font = load_font(cfg["font_size"])
    label_font = load_font(cfg["circular_label_size"])

    base_color = cfg["circular_base_color"]
    prog_color = cfg["circular_progress_color"]
    thickness = cfg["circular_thickness"]
    spacing = cfg["circular_spacing"]
    label_color = cfg["circular_label_color"]
    show_labels = cfg["show_labels"]

    radius = 28
    center_y = h // 2 + 8

    max_days = 30
    days_ratio = min(days / max_days, 1.0) if max_days > 0 else 1.0
    hours_ratio = hours / 24 if hours >= 0 else 0
    minutes_ratio = minutes / 60 if minutes >= 0 else 0
    seconds_ratio = seconds / 60 if seconds >= 0 else 0

    units = [
        ("J", days, days_ratio),
        ("H", hours, hours_ratio),
        ("M", minutes, minutes_ratio),
        ("S", seconds, seconds_ratio),
    ]

    total_width = 4 * (radius * 2) + 3 * spacing
    start_x = (w - total_width) // 2

    for i, (label, val, ratio) in enumerate(units):
        cx = start_x + radius + i * (2 * radius + spacing)
        cy = center_y

        bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
        draw.ellipse(bbox, outline=base_color, width=thickness)

        start_angle = -90
        end_angle = start_angle + int(360 * max(0.0, min(ratio, 1.0)))
        if end_angle > start_angle:
            draw.arc(bbox, start=start_angle, end=end_angle, fill=prog_color, width=thickness)

        val_txt = f"{val:02}"
        vb = draw.textbbox((0, 0), val_txt, font=main_font)
        vw = vb[2] - vb[0]
        vh = vb[3] - vb[1]
        draw.text((cx - vw // 2, cy - vh // 2), val_txt, font=main_font, fill=cfg["text_color"])

        if show_labels:
            lbl = label.upper() if cfg["circular_label_uppercase"] else label
            lb = draw.textbbox((0, 0), lbl, font=label_font)
            lw = lb[2] - lb[0]
            lh = lb[3] - lb[1]
            draw.text((cx - lw // 2, cy + radius + 4), lbl, font=label_font, fill=label_color)

    prefix = cfg.get("message_prefix") or ""
    if prefix:
        pf = load_font(max(10, int(cfg["font_size"] * 0.5)))
        pb = draw.textbbox((0, 0), prefix, font=pf)
        pw = pb[2] - pb[0]
        ph = pb[3] - pb[1]
        px = (w - pw) // 2
        py = center_y - radius - ph - 6
        draw.text((px, max(4, py)), prefix, font=pf, fill=cfg["text_color"])


# ============================
# PREVIEW LIVE (SVG)
# ============================

@app.route("/preview.svg")
def preview_svg():
    cfg = DEFAULT_CONFIG.copy()
    args = request.args

    tpl = args.get("template", cfg["template"])
    if tpl not in ("basic", "circular"):
        tpl = "basic"
    cfg["template"] = tpl

    bg = args.get("background_color")
    if bg:
        cfg["background_color"] = bg
    txtc = args.get("text_color")
    if txtc:
        cfg["text_color"] = txtc
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

    cbg = args.get("circular_base_color")
    if cbg:
        cfg["circular_base_color"] = cbg
    cpg = args.get("circular_progress_color")
    if cpg:
        cfg["circular_progress_color"] = cpg
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

    target_date = args.get("target_date")
    if target_date:
        iso = target_date.replace(" ", "T")
        if len(iso) == 16:
            iso += ":00"
        cfg["target_date"] = iso

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

    units = [
        ("J", days),
        ("H", hours),
        ("M", minutes),
        ("S", seconds),
    ]

    def esc(text: str) -> str:
        return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # TEMPLATE CIRCULAR EN SVG
    if tpl == "circular":
        radius = 28
        spacing = cfg["circular_spacing"]
        total_width = 4 * (radius * 2) + 3 * spacing
        start_x = (w - total_width) / 2
        cy = h / 2 + 8

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            f'<rect width="100%" height="100%" fill="{cfg["background_color"]}"/>'
        ]

        # Préfixe
        svg_parts.append(
            f'<text x="{w/2}" y="24" text-anchor="middle" '
            f'font-family="system-ui, -apple-system, sans-serif" font-size="14" '
            f'fill="{cfg["text_color"]}">{esc(prefix)}</text>'
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
            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy_local}" r="{radius}" '
                f'stroke="{cfg["circular_base_color"]}" stroke-width="{cfg["circular_thickness"]}" '
                f'fill="none" />'
            )

            # progression
            circ = 2 * math.pi * radius
            dash = max(0.0, min(ratio, 1.0)) * circ
            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy_local}" r="{radius}" '
                f'stroke="{cfg["circular_progress_color"]}" stroke-width="{cfg["circular_thickness"]}" '
                f'fill="none" stroke-dasharray="{dash} {circ - dash}" '
                f'transform="rotate(-90 {cx} {cy_local})" />'
            )

            # valeur
            svg_parts.append(
                f'<text x="{cx}" y="{cy_local+4}" text-anchor="middle" '
                f'font-size="{cfg["font_size"]}" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'fill="{cfg["text_color"]}" dominant-baseline="middle">{val:02d}</text>'
            )

            # label
            if show_labels:
                lbl = label.upper() if cfg["circular_label_uppercase"] else label
                svg_parts.append(
                    f'<text x="{cx}" y="{cy_local+radius+14}" text-anchor="middle" '
                    f'font-size="{cfg["circular_label_size"]}" '
                    f'font-family="system-ui, -apple-system, sans-serif" '
                    f'fill="{cfg["circular_label_color"]}">{lbl}</text>'
                )

        svg_parts.append("</svg>")
        svg_str = "\n".join(svg_parts)
        return app.response_class(svg_str, mimetype="image/svg+xml")

    # TEMPLATE BASIC EN SVG
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="{cfg["background_color"]}"/>'
    ]

    svg_parts.append(
        f'<text x="{w/2}" y="28" text-anchor="middle" '
        f'font-family="system-ui, -apple-system, sans-serif" '
        f'font-size="14" fill="{cfg["text_color"]}">{esc(prefix)}</text>'
    )

    center_y = h / 2 + 12
    main_size = cfg["font_size"]
    label_size = cfg["basic_label_size"]
    gap = cfg["basic_gap"]

    total_width = 0
    char_width = main_size * 0.75
    label_width = label_size * 0.7
    between = 18

    for label, val in units:
        num_w = 2 * char_width
        lab_w = label_width
        bw = max(num_w, lab_w)
        total_width += bw
    total_width += between * (len(units) - 1)
    start_x = (w - total_width) / 2

    x = start_x
    for label, val in units:
        num_w = 2 * char_width
        lab_w = label_width
        bw = max(num_w, lab_w)

        num_x = x + bw / 2
        svg_parts.append(
            f'<text x="{num_x}" y="{center_y}" text-anchor="middle" '
            f'font-size="{main_size}" '
            f'font-family="system-ui, -apple-system, sans-serif" '
            f'fill="{cfg["text_color"]}">{val:02d}</text>'
        )

        if show_labels:
            svg_parts.append(
                f'<text x="{num_x}" y="{center_y + main_size + gap}" text-anchor="middle" '
                f'font-size="{label_size}" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'fill="{cfg["basic_label_color"]}">{label}</text>'
            )

        x += bw + between

    svg_parts.append("</svg>")
    svg_str = "\n".join(svg_parts)
    return app.response_class(svg_str, mimetype="image/svg+xml")


# ============================
# GIF FINAL
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

    frames = []
    loop = cfg.get("loop_duration", 20)

    for i in range(loop):
        current = now + timedelta(seconds=i)
        remaining = int((end - current).total_seconds())

        img = Image.new("RGB", (cfg["width"], cfg["height"]), cfg["background_color"])
        draw = ImageDraw.Draw(img)

        if remaining <= 0:
            font = load_font(cfg["font_size"])
            draw_centered_text(draw, cfg, "⏰ Terminé !", font)
        else:
            total_sec = remaining
            days, rem = divmod(total_sec, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, seconds = divmod(rem, 60)

            if cfg.get("template") == "circular":
                draw_circular(draw, cfg, days, hours, minutes, seconds)
            else:
                draw_basic(draw, cfg, days, hours, minutes, seconds)

        frames.append(img)

    buf = BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=1000,
    )
    buf.seek(0)
    return send_file(buf, mimetype="image/gif")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)