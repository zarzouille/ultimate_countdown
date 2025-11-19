import os
import json
import uuid
from datetime import datetime, timedelta
from io import BytesIO

from flask import Flask, render_template, request, send_file, url_for, redirect
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
DEFAULT_CONFIG = {
    "template": "circular",  # circular / basic
    "background_color": "#FFFFFF",
    "text_color": "#000000",
    "font_size": 48,
    "message_prefix": "Temps restant : ",
    "target_date": "2025-12-31T23:59:59",
    "show_labels": True,

    # Circular-specific
    "circle_bg_color": "#D4E8FF",
    "circle_fg_color": "#3A5CC2",
    "circle_thickness": 14,
    "circle_gap": 40,
    "circle_inner_padding": 12,

    # Basic-specific
    "label_color": "#444444",
    "label_size": 18,
    "label_gap": 6,

    # Output
    "width": 600,
    "height": 200,
    "loop_duration": 10,
}

CONFIG_DIR = "configs"


def ensure_configs():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def save_config(cid, cfg):
    ensure_configs()
    with open(os.path.join(CONFIG_DIR, f"{cid}.json"), "w") as f:
        json.dump(cfg, f, indent=2)


def load_config(cid):
    path = os.path.join(CONFIG_DIR, f"{cid}.json")
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        data = json.load(f)

    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    return cfg


# ---------------------------------------------------------
# FLASK APP
# ---------------------------------------------------------
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def settings():
    cfg = DEFAULT_CONFIG.copy()
    link = None

    if request.method == "POST":
        # Template
        cfg["template"] = request.form.get("template", "circular")

        # Communes
        cfg["background_color"] = request.form.get("background_color")
        cfg["text_color"] = request.form.get("text_color")
        cfg["font_size"] = int(request.form.get("font_size"))
        cfg["message_prefix"] = request.form.get("message_prefix")
        cfg["show_labels"] = (request.form.get("show_labels") == "on")

        # Date
        td = request.form.get("target_date")
        if td:
            if "T" not in td:
                td += "T00:00"
            cfg["target_date"] = td

        # Circular
        cfg["circle_bg_color"] = request.form.get("circle_bg_color")
        cfg["circle_fg_color"] = request.form.get("circle_fg_color")
        cfg["circle_thickness"] = int(request.form.get("circle_thickness"))
        cfg["circle_gap"] = int(request.form.get("circle_gap"))
        cfg["circle_inner_padding"] = int(request.form.get("circle_inner_padding"))

        # Basic
        cfg["label_color"] = request.form.get("label_color")
        cfg["label_size"] = int(request.form.get("label_size"))
        cfg["label_gap"] = int(request.form.get("label_gap"))

        # Create ID
        cid = uuid.uuid4().hex[:8]
        save_config(cid, cfg)

        link = request.url_root.rstrip("/") + url_for("gif_image", cid=cid)

    # date input format
    td = cfg["target_date"]
    try:
        dt = datetime.fromisoformat(td)
        td = dt.strftime("%Y-%m-%dT%H:%M")
    except:
        pass

    return render_template("settings.html", config=cfg, target_date=td, link=link)


# ---------------------------------------------------------
# DRAWING HELPERS
# ---------------------------------------------------------
def draw_circular(draw, img, cfg, days, hours, minutes, seconds, remaining, total_initial, SCALE):
    """
    Dessin du template CIRCULAR (avec supersampling ×4).
    """
    W = cfg["width"] * SCALE
    H = cfg["height"] * SCALE

    center_y = H // 2
    gap = cfg["circle_gap"] * SCALE

    radius = int((H // 2) - (40 * SCALE))
    thickness = cfg["circle_thickness"] * SCALE

    numbers = [days, hours, minutes, seconds]
    labels = ["J", "H", "M", "S"]
    count = 4

    total_width = count * (radius * 2) + (count - 1) * gap
    offset_x = (W - total_width) // 2

    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", cfg["font_size"] * SCALE)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16 * SCALE)
    except:
        font_big = ImageFont.load_default()
        font_label = ImageFont.load_default()

    for i in range(count):
        angle_ratio = [days, hours, minutes, seconds][i] / ([365, 24, 60, 60][i])

        x_center = offset_x + i * (2 * radius + gap)
        y_center = center_y

        # FOND du cercle
        draw.arc(
            (x_center - radius, y_center - radius, x_center + radius, y_center + radius),
            start=0,
            end=359.9,
            fill=cfg["circle_bg_color"],
            width=thickness
        )

        # PROGRESSION
        draw.arc(
            (x_center - radius, y_center - radius, x_center + radius, y_center + radius),
            start=-90,
            end=-90 + (angle_ratio * 360),
            fill=cfg["circle_fg_color"],
            width=thickness
        )

        # Texte numérique
        num_txt = f"{numbers[i]:02}"
        tw, th = draw.textsize(num_txt, font=font_big)
        draw.text(
            (x_center - tw // 2, y_center - th // 2),
            num_txt,
            font=font_big,
            fill=cfg["text_color"]
        )

        # Label sous le cercle
        if cfg["show_labels"]:
            label = labels[i]
            lw, lh = draw.textsize(label, font=font_label)
            draw.text(
                (x_center - lw // 2, y_center + radius + (10 * SCALE)),
                label,
                font=font_label,
                fill=cfg["text_color"]
            )


def draw_basic(draw, img, cfg, days, hours, minutes, seconds, SCALE):
    """
    Template BASIC (texte simple)
    """
    text = f"{days:02}  {hours:02}  {minutes:02}  {seconds:02}"

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", cfg["font_size"] * SCALE)
    except:
        font = ImageFont.load_default()

    tw, th = draw.textsize(text, font=font)
    W = cfg["width"] * SCALE
    H = cfg["height"] * SCALE

    draw.text(
        ((W - tw) // 2, (H - th) // 2),
        text,
        font=font,
        fill=cfg["text_color"]
    )


# ---------------------------------------------------------
# GIF RENDERING (SUPER SAMPLING ×4)
# ---------------------------------------------------------
@app.route("/c/<cid>.gif")
def gif_image(cid):
    cfg = load_config(cid)
    if not cfg:
        return "Not found", 404

    SCALE = 4  # Supersampling

    try:
        end = datetime.fromisoformat(cfg["target_date"])
    except:
        return "Bad date", 400

    now = datetime.utcnow()
    total_initial = max((end - now).total_seconds(), 1)

    frames = []

    for i in range(cfg["loop_duration"]):
        t = now + timedelta(seconds=i)
        remaining = max((end - t).total_seconds(), 0)

        days, rem = divmod(int(remaining), 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)

        # Image HD
        big = Image.new("RGB", (cfg["width"] * SCALE, cfg["height"] * SCALE), cfg["background_color"])
        draw = ImageDraw.Draw(big)

        if remaining <= 0:
            # Terminé
            try:
                font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", cfg["font_size"] * SCALE)
            except:
                font_big = ImageFont.load_default()

            msg = "⏰ Terminé !"
            tw, th = draw.textsize(msg, font=font_big)
            draw.text(
                ((cfg["width"] * SCALE - tw) // 2, (cfg["height"] * SCALE - th) // 2),
                msg, font=font_big, fill=cfg["text_color"]
            )
        else:
            if cfg["template"] == "circular":
                draw_circular(draw, big, cfg, days, hours, minutes, seconds, remaining, total_initial, SCALE)
            else:
                draw_basic(draw, big, cfg, days, hours, minutes, seconds, SCALE)

        # Downscale
        final = big.resize((cfg["width"], cfg["height"]), Image.LANCZOS)
        frames.append(final)

    # GIF
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


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)