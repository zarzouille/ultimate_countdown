import os
import json
import uuid
from datetime import datetime, timedelta
from io import BytesIO

from flask import Flask, render_template, request, send_file, url_for, redirect
from PIL import Image, ImageDraw, ImageFont

# ============================
# CONFIG GLOBALE
# ============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    # dimensions GIF
    "width": 400,
    "height": 160,

    # options communes
    "template": "basic",  # "basic" ou "circular"
    "background_color": "#FFFFFF",
    "text_color": "#111111",
    "font_size": 32,
    "message_prefix": "Temps restant : ",
    "target_date": "2025-12-31T23:59:59",
    "show_labels": True,
    "loop_duration": 10,  # nb d’images dans le GIF

    # options template CIRCULAR
    "circular_base_color": "#E0EAFF",
    "circular_progress_color": "#4C6FFF",
    "circular_thickness": 6,
    "circular_label_uppercase": True,
    "circular_label_size": 11,
    "circular_label_color": "#555555",
    "circular_spacing": 12,
    "circular_inner_ratio": 0.7,  # 0.0–1.0

    # options template BASIC
    "basic_label_color": "#666666",
    "basic_label_size": 11,
    "basic_gap": 4,  # espace nombre–label
}

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


# ============================
# OUTILS CONFIG
# ============================

def cfg_path(countdown_id: str) -> str:
    return os.path.join(CONFIG_DIR, f"{countdown_id}.json")


def save_config(countdown_id: str, cfg: dict) -> None:
    path = cfg_path(countdown_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_config(countdown_id: str) -> dict | None:
    path = cfg_path(countdown_id)
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
    compatible <input type="datetime-local">
    """
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%dT%H:%M")
    except Exception:
        # fallback : on tronque simplement
        return iso_str[:16]


# ============================
# FLASK APP
# ============================

app = Flask(__name__)


# ============================
# ROUTE PRINCIPALE
# ============================

@app.route("/", methods=["GET", "POST"])
def settings():
    cfg = DEFAULT_CONFIG.copy()
    img_link = None

    if request.method == "POST":
        # --- template choisi ---
        tpl = request.form.get("template", "").strip() or cfg["template"]
        if tpl not in ("basic", "circular"):
            tpl = "basic"
        cfg["template"] = tpl

        # --- options communes ---
        raw_date = request.form.get("target_date", "").strip()
        if raw_date:
            # on garde tel quel, fromisoformat accepte HH:MM ou HH:MM:SS
            cfg["target_date"] = raw_date.replace(" ", "T")

        cfg["message_prefix"] = request.form.get("message_prefix", cfg["message_prefix"])
        cfg["background_color"] = request.form.get("background_color", cfg["background_color"])
        cfg["text_color"] = request.form.get("text_color", cfg["text_color"])

        try:
            cfg["font_size"] = int(request.form.get("font_size", cfg["font_size"]))
        except ValueError:
            pass

        cfg["show_labels"] = bool(request.form.get("show_labels"))

        # --- options CIRCULAR ---
        cfg["circular_base_color"] = request.form.get("circular_base_color", cfg["circular_base_color"])
        cfg["circular_progress_color"] = request.form.get("circular_progress_color", cfg["circular_progress_color"])
        try:
            cfg["circular_thickness"] = int(request.form.get("circular_thickness", cfg["circular_thickness"]))
        except ValueError:
            pass
        cfg["circular_label_uppercase"] = bool(request.form.get("circular_label_uppercase"))
        try:
            cfg["circular_label_size"] = int(request.form.get("circular_label_size", cfg["circular_label_size"]))
        except ValueError:
            pass
        cfg["circular_label_color"] = request.form.get("circular_label_color", cfg["circular_label_color"])
        try:
            cfg["circular_spacing"] = int(request.form.get("circular_spacing", cfg["circular_spacing"]))
        except ValueError:
            pass
        try:
            cfg["circular_inner_ratio"] = float(request.form.get("circular_inner_ratio", cfg["circular_inner_ratio"]))
        except ValueError:
            pass

        # --- options BASIC ---
        cfg["basic_label_color"] = request.form.get("basic_label_color", cfg["basic_label_color"])
        try:
            cfg["basic_label_size"] = int(request.form.get("basic_label_size", cfg["basic_label_size"]))
        except ValueError:
            pass
        try:
            cfg["basic_gap"] = int(request.form.get("basic_gap", cfg["basic_gap"]))
        except ValueError:
            pass

        # --- on génère un ID, on sauvegarde, on crée le lien ---
        countdown_id = uuid.uuid4().hex[:8]
        save_config(countdown_id, cfg)

        img_link = request.url_root.rstrip("/") + url_for("countdown_image", countdown_id=countdown_id)

    target_date_value = dt_for_input(cfg["target_date"])

    return render_template(
        "settings.html",
        config=cfg,
        target_date=target_date_value,
        img_link=img_link,
    )


# ============================
# OUTILS DESSIN
# ============================

def load_font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def draw_centered_text(draw: ImageDraw.ImageDraw, cfg: dict, text: str, font, fill: str | None = None):
    w, h = cfg["width"], cfg["height"]
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (w - tw) // 2
    y = (h - th) // 2
    draw.text((x, y), text, font=font, fill=fill or cfg["text_color"])


# ============================
# TEMPLATE BASIC
# ============================

def draw_basic(draw: ImageDraw.ImageDraw, cfg: dict, days: int, hours: int, minutes: int, seconds: int):
    w, h = cfg["width"], cfg["height"]
    font_main = load_font(cfg["font_size"])
    label_size = cfg["basic_label_size"]
    font_label = load_font(label_size)

    show_labels = cfg["show_labels"]
    label_gap = cfg["basic_gap"]
    label_color = cfg["basic_label_color"]

    units = [
        ("J", days),
        ("H", hours),
        ("M", minutes),
        ("S", seconds),
    ]

    # Mesure
    blocks = []
    total_w = 0
    gap_between = 18
    for label, val in units:
        val_txt = f"{val:02}"
        tb = draw.textbbox((0, 0), val_txt, font=font_main)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]

        if show_labels:
            lb = draw.textbbox((0, 0), label, font=font_label)
            lw = lb[2] - lb[0]
            lh = lb[3] - lb[1]
        else:
            lw = lh = 0

        bw = max(tw, lw)
        bh = th + (label_gap + lh if show_labels else 0)

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

    total_w += gap_between * (len(blocks) - 1)
    x = (w - total_w) // 2
    center_y = h // 2

    for b in blocks:
        bw, bh = b["bw"], b["bh"]
        top = center_y - bh // 2

        # nombre
        val_x = x + (bw - b["tw"]) // 2
        val_y = top
        draw.text((val_x, val_y), b["val"], font=font_main, fill=cfg["text_color"])

        # label
        if show_labels:
            label_x = x + (bw - b["lw"]) // 2
            label_y = val_y + b["th"] + label_gap
            draw.text((label_x, label_y), b["label"], font=font_label, fill=label_color)

        x += bw + gap_between

    # Préfixe au-dessus
    prefix = cfg.get("message_prefix", "")
    if prefix:
        prefix_font = load_font(max(10, int(cfg["font_size"] * 0.5)))
        pb = draw.textbbox((0, 0), prefix, font=prefix_font)
        pw = pb[2] - pb[0]
        ph = pb[3] - pb[1]
        px = (w - pw) // 2
        py = max(4, center_y - (blocks[0]["bh"] // 2) - ph - 6)
        draw.text((px, py), prefix, font=prefix_font, fill=cfg["text_color"])

# ============================
# TEMPLATE CIRCULAR
# ============================

def draw_circular(draw: ImageDraw.ImageDraw, cfg: dict, days: int, hours: int, minutes: int, seconds: int, remaining: int, total_initial: int):
    w, h = cfg["width"], cfg["height"]
    radius = 30  # rayon externe
    spacing = cfg["circular_spacing"]
    thickness = cfg["circular_thickness"]
    base_color = cfg["circular_base_color"]
    prog_color = cfg["circular_progress_color"]
    inner_ratio = max(0.0, min(cfg["circular_inner_ratio"], 0.95))

    font_main = load_font(cfg["font_size"])
    font_label = load_font(cfg["circular_label_size"])
    label_color = cfg["circular_label_color"]
    show_labels = cfg["show_labels"]

    # unités et progression associée
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

    total_width_circles = 4 * (radius * 2) + 3 * spacing
    start_x = (w - total_width_circles) // 2
    center_y = h // 2 + 4  # léger décalage vers le bas

    for i, (label, val, ratio) in enumerate(units):
        cx = start_x + radius + i * (2 * radius + spacing)
        cy = center_y

        # cercle de base
        bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
        draw.ellipse(bbox, outline=base_color, width=thickness)

        # arc de progression
        start_angle = -90  # en haut
        end_angle = start_angle + int(360 * max(0.0, min(ratio, 1.0)))
        if end_angle > start_angle:
            draw.arc(bbox, start=start_angle, end=end_angle, fill=prog_color, width=thickness)

        # texte (valeur)
        val_txt = f"{val:02}"
        vb = draw.textbbox((0, 0), val_txt, font=font_main)
        vw = vb[2] - vb[0]
        vh = vb[3] - vb[1]
        draw.text((cx - vw // 2, cy - vh // 2), val_txt, font=font_main, fill=cfg["text_color"])

        # label
        if show_labels:
            lbl_txt = label
            if cfg["circular_label_uppercase"]:
                lbl_txt = lbl_txt.upper()
            lb = draw.textbbox((0, 0), lbl_txt, font=font_label)
            lw = lb[2] - lb[0]
            lh = lb[3] - lb[1]
            draw.text((cx - lw // 2, cy + radius + 4), lbl_txt, font=font_label, fill=label_color)

    # Préfixe au-dessus (centré)
    prefix = cfg.get("message_prefix", "")
    if prefix:
        prefix_font = load_font(max(10, int(cfg["font_size"] * 0.45)))
        pb = draw.textbbox((0, 0), prefix, font=prefix_font)
        pw = pb[2] - pb[0]
        ph = pb[3] - pb[1]
        px = (w - pw) // 2
        py = max(4, center_y - radius - ph - 8)
        draw.text((px, py), prefix, font=prefix_font, fill=cfg["text_color"])


# ============================
# ROUTE GIF
# ============================

@app.route("/c/<countdown_id>.gif")
def countdown_image(countdown_id):
    cfg = load_config(countdown_id)
    if cfg is None:
        return "Compte introuvable", 404

    try:
        end_time = datetime.fromisoformat(cfg["target_date"])
    except Exception:
        return "Date cible invalide", 400

    now = datetime.utcnow()
    total_initial = max(int((end_time - now).total_seconds()), 1)

    frames: list[Image.Image] = []
    loop_duration = cfg.get("loop_duration", 10)

    for i in range(loop_duration):
        current_time = now + timedelta(seconds=i)
        remaining = int((end_time - current_time).total_seconds())

        img = Image.new("RGB", (cfg["width"], cfg["height"]), cfg["background_color"])
        draw = ImageDraw.Draw(img)

        if remaining <= 0:
            font = load_font(cfg["font_size"])
            draw_centered_text(draw, cfg, "⏰ Terminé !", font)
        else:
            total_seconds = remaining
            days, rem = divmod(total_seconds, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, seconds = divmod(rem, 60)

            tpl = cfg.get("template", "basic")
            if tpl == "circular":
                draw_circular(draw, cfg, days, hours, minutes, seconds, remaining, total_initial)
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


# ============================
# MAIN
# ============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
