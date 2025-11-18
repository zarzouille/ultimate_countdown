import os
import json
import sys
import uuid
from functools import wraps
from datetime import datetime, timedelta
from io import BytesIO

from flask import (
    Flask,
    send_file,
    request,
    render_template,
    url_for,
    redirect,
    session,
)
from PIL import Image, ImageDraw, ImageFont
from json import JSONDecodeError

# -----------------------------
# CONFIG PAR DÉFAUT
# -----------------------------
DEFAULT_CONFIG = {
    "width": 600,
    "height": 200,
    "background_color": "#FFFFFF",
    "text_color": "#000000",
    "font_path": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "font_size": 40,
    "message_prefix": "Temps restant : ",
    "target_date": "2025-12-31T23:59:59",
    "loop_duration": 10,

    "title": "Ultimate Countdown",

    "template": "classic",
    "show_labels": True,
    "labels_custom": False,
    "label_color": "#444444",
    "labels_personalized": {
        "days": "Jours",
        "hours": "Heures",
        "minutes": "Minutes",
        "seconds": "Secondes"
    },

    "block_bg_color": "#FFFFFF",
    "block_border_color": "#000000",
    "block_border_width": 2,
    "block_radius": 12,
    "block_padding_x": 16,
    "block_padding_y": 8,
    "blocks_gap": 12,

    "alignment": "center",
    "padding": 20,

    "icon": "🕒",
    "icon_position": "left",

    "progress_bg_color": "#EEEEEE",
    "progress_fg_color": "#00AAFF",
    "progress_height": 16,
    "progress_max_days": 30,

    "banner_bg_color": "#222222",
    "banner_text_color": "#FFFFFF"
}

CONFIG_DIR = "configs"
ADMIN_PASSWORD = "Doudou2904!!"
SECRET_KEY_DEFAULT = "change-me-secret"

SAFE_MARGIN = 10

# -----------------------------
# UTILITAIRES
# -----------------------------
def ensure_configs_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def countdown_path(countdown_id: str) -> str:
    return os.path.join(CONFIG_DIR, f"{countdown_id}.json")

def load_countdown_config(countdown_id: str):
    ensure_configs_dir()
    path = countdown_path(countdown_id)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError
    except Exception:
        return None

    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    cfg.update(data)
    return cfg

def save_countdown_config(countdown_id: str, cfg: dict):
    ensure_configs_dir()
    with open(countdown_path(countdown_id), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def list_countdowns():
    ensure_configs_dir()
    out = []
    for f in os.listdir(CONFIG_DIR):
        if not f.endswith(".json"):
            continue
        cid = f[:-5]
        full = countdown_path(cid)
        try:
            m = datetime.fromtimestamp(os.path.getmtime(full))
        except:
            m = None
        out.append({"id": cid, "mtime": m})
    out.sort(key=lambda x: x["mtime"] or datetime.min, reverse=True)
    return out

# -----------------------------
# FLASK APP
# -----------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", SECRET_KEY_DEFAULT)

def is_admin():
    return session.get("is_admin") is True

def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not is_admin():
            return redirect(url_for("admin_login", next=request.path))
        return fn(*a, **kw)
    return wrapper

# -----------------------------
# ADMIN
# -----------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None
    nxt = request.args.get("next") or url_for("admin_list")
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(nxt)
        error = "Mot de passe incorrect."
    return render_template("admin.html", error=error)

@app.route("/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("create_countdown"))

# -----------------------------
# CREATION COUNTDOWN
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def create_countdown():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    img_link = None
    countdown_id = None

    if request.method == "POST":
        cfg["template"] = request.form.get("template", cfg["template"])
        cfg["title"] = request.form.get("title", cfg["title"])

        raw_date = request.form.get("target_date", "")
        if raw_date:
            if len(raw_date) == 16:
                raw_date += ":00"
            cfg["target_date"] = raw_date.replace(" ", "T")

        cfg["background_color"] = request.form.get("background_color", cfg["background_color"])
        cfg["text_color"] = request.form.get("text_color", cfg["text_color"])
        cfg["font_size"] = int(request.form.get("font_size", cfg["font_size"]) or cfg["font_size"])
        cfg["message_prefix"] = request.form.get("message_prefix", cfg["message_prefix"])
        cfg["padding"] = int(request.form.get("padding", cfg["padding"]))
        cfg["icon"] = request.form.get("icon", cfg["icon"])

        cfg["show_labels"] = (request.form.get("show_labels") == "on")
        cfg["labels_custom"] = (request.form.get("labels_custom") == "on")
        cfg["label_color"] = request.form.get("label_color", cfg["label_color"])

        if cfg["labels_custom"]:
            cfg["labels_personalized"]["days"] = request.form.get("label_days") or "Jours"
            cfg["labels_personalized"]["hours"] = request.form.get("label_hours") or "Heures"
            cfg["labels_personalized"]["minutes"] = request.form.get("label_minutes") or "Minutes"
            cfg["labels_personalized"]["seconds"] = request.form.get("label_seconds") or "Secondes"

        cfg["block_bg_color"] = request.form.get("block_bg_color", cfg["block_bg_color"])
        cfg["block_border_color"] = request.form.get("block_border_color", cfg["block_border_color"])
        cfg["block_border_width"] = int(request.form.get("block_border_width", cfg["block_border_width"]))
        cfg["block_radius"] = int(request.form.get("block_radius", cfg["block_radius"]))
        cfg["block_padding_x"] = int(request.form.get("block_padding_x", cfg["block_padding_x"]))
        cfg["block_padding_y"] = int(request.form.get("block_padding_y", cfg["block_padding_y"]))
        cfg["blocks_gap"] = int(request.form.get("blocks_gap", cfg["blocks_gap"]))

        cfg["progress_bg_color"] = request.form.get("progress_bg_color", cfg["progress_bg_color"])
        cfg["progress_fg_color"] = request.form.get("progress_fg_color", cfg["progress_fg_color"])
        cfg["progress_height"] = int(request.form.get("progress_height", cfg["progress_height"]))
        cfg["progress_max_days"] = int(request.form.get("progress_max_days", cfg["progress_max_days"]))

        cfg["banner_bg_color"] = request.form.get("banner_bg_color", cfg["banner_bg_color"])
        cfg["banner_text_color"] = request.form.get("banner_text_color", cfg["banner_text_color"])

        countdown_id = uuid.uuid4().hex[:8]
        save_countdown_config(countdown_id, cfg)

        img_link = request.url_root.rstrip("/") + url_for("countdown_image", countdown_id=countdown_id)

    try:
        dt = datetime.fromisoformat(cfg["target_date"])
        target_date_for_input = dt.strftime("%Y-%m-%dT%H:%M")
    except:
        target_date_for_input = DEFAULT_CONFIG["target_date"][:16]

    return render_template(
        "settings.html",
        config=cfg,
        target_date=target_date_for_input,
        img_link=img_link,
        countdown_id=countdown_id,
        uuid=uuid.uuid4().hex
    )

@app.route("/settings")
def redirect_settings():
    return redirect(url_for("create_countdown"))

# -----------------------------
# TEMPLATE LIST (ADMIN)
# -----------------------------
@app.route("/list")
@admin_required
def admin_list():
    base = request.url_root.rstrip("/")
    out = []
    for it in list_countdowns():
        cid = it["id"]
        cfg = load_countdown_config(cid) or {}
        out.append({
            "id": cid,
            "mtime": it["mtime"],
            "template": cfg.get("template"),
            "gif_url": base + url_for("countdown_image", countdown_id=cid)
        })
    return render_template("list.html", countdowns=out)

# -----------------------------
# PREVIEW (ADMIN)
# -----------------------------
@app.route("/preview/<countdown_id>")
@admin_required
def preview_countdown(countdown_id):
    cfg = load_countdown_config(countdown_id)
    if cfg is None:
        return "Compte introuvable", 404

    try:
        dt = datetime.fromisoformat(cfg["target_date"])
        target_date_for_input = dt.strftime("%Y-%m-%dT%H:%M")
    except:
        target_date_for_input = cfg["target_date"][:16]

    gif_url = request.url_root.rstrip("/") + url_for("countdown_image", countdown_id=countdown_id)

    return render_template(
        "preview.html",
        countdown_id=countdown_id,
        config=cfg,
        target_date=target_date_for_input,
        gif_url=gif_url
    )


# -----------------------------
# EXPORT / IMPORT (ADMIN)
# -----------------------------
@app.route("/export/<countdown_id>")
@admin_required
def export_countdown(countdown_id):
    path = countdown_path(countdown_id)
    if not os.path.exists(path):
        return "Not found", 404

    return send_file(
        path,
        mimetype="application/json",
        as_attachment=True,
        download_name=f"{countdown_id}.json"
    )

@app.route("/import", methods=["POST"])
@admin_required
def import_countdown():
    raw = request.form.get("import_json", "").strip()
    custom_id = request.form.get("import_id", "").strip() or None

    if not raw:
        return redirect(url_for("admin_list"))

    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError
    except:
        return redirect(url_for("admin_list"))

    countdown_id = custom_id or uuid.uuid4().hex[:8]
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    cfg.update(data)
    save_countdown_config(countdown_id, cfg)

    return redirect(url_for("admin_list"))

@app.route("/delete/<countdown_id>", methods=["POST"])
@admin_required
def delete_countdown(countdown_id):
    p = countdown_path(countdown_id)
    if os.path.exists(p):
        os.remove(p)
    return redirect(url_for("admin_list"))


# -----------------------------
# DRAW HELPERS
# -----------------------------
def draw_centered(draw, cfg, text, font):
    W, H = cfg["width"], cfg["height"]
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((W - tw) // 2, (H - th) // 2), text, font=font, fill=cfg["text_color"])


# -----------------------------
# ALL TEMPLATE RENDERERS
# -----------------------------
def render_classic(draw, cfg, font, d, h, m, s):
    txt = f"{cfg['message_prefix']}{d}j {h:02}:{m:02}:{s:02}"
    if cfg["icon"]:
        txt = f"{cfg['icon']}  {txt}"
    draw_centered(draw, cfg, txt, font)

def render_blocks(draw, cfg, font, d, h, m, s, shape):
    W, H = cfg["width"], cfg["height"]
    pad_x = cfg["block_padding_x"]
    pad_y = cfg["block_padding_y"]
    border = cfg["block_border_width"]
    rad = cfg["block_radius"]
    gap = cfg["blocks_gap"]

    units = [
        ("days", d),
        ("hours", h),
        ("minutes", m),
        ("seconds", s),
    ]

    if cfg["labels_custom"]:
        labels = cfg["labels_personalized"]
    else:
        labels = {"days": "J", "hours": "H", "minutes": "M", "seconds": "S"}

    lb_font_size = int(cfg["font_size"] * 0.45)
    try:
        label_font = ImageFont.truetype(cfg["font_path"], lb_font_size)
    except:
        label_font = ImageFont.load_default()

    blocks = []
    for key, val in units:
        val_txt = f"{val:02}"

        tb = draw.textbbox((0, 0), val_txt, font=font)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[0]

        lbl = labels[key]
        if cfg["show_labels"]:
            lb = draw.textbbox((0, 0), lbl, font=label_font)
            lw = lb[2] - lb[0]
            lh = lb[3] - lb[1]
        else:
            lw = lh = 0

        bw = max(tw, lw) + pad_x * 2
        bh = th + lh + pad_y * 4

        blocks.append({
            "val": val_txt,
            "label": lbl,
            "bw": bw,
            "bh": bh,
            "tw": tw,
            "th": th,
            "lw": lw,
            "lh": lh
        })

    total_w = sum(b["bw"] for b in blocks) + gap * (len(blocks) - 1)
    x = (W - total_w) // 2
    cy = H // 2

    for b in blocks:
        bw, bh = b["bw"], b["bh"]
        top = cy - bh // 2
        bot = top + bh

        if shape == "bubble":
            draw.ellipse((x, top, x + bw, bot), fill=cfg["block_bg_color"], outline=cfg["block_border_color"], width=border)
        else:
            draw.rounded_rectangle((x, top, x + bw, bot), radius=rad, fill=cfg["block_bg_color"], outline=cfg["block_border_color"], width=border)
            if shape == "flip":
                mid = (top + bot) // 2
                draw.line((x, mid, x + bw, mid), fill=cfg["block_border_color"], width=1)

        txt_x = x + (bw - b["tw"]) // 2
        txt_y = top + pad_y
        draw.text((txt_x, txt_y), b["val"], font=font, fill=cfg["text_color"])

        if cfg["show_labels"]:
            lbl_x = x + (bw - b["lw"]) // 2
            lbl_y = bot - pad_y - b["lh"]
            draw.text((lbl_x, lbl_y), b["label"], font=label_font, fill=cfg["label_color"])

        x += bw + gap


def render_minimal(draw, cfg, font, d, h, m, s):
    draw_centered(draw, cfg, f"{d:02}:{h:02}:{m:02}:{s:02}", font)


def render_banner(draw, cfg, font, d, h, m, s):
    W, H = cfg["width"], cfg["height"]
    text = f"{cfg['message_prefix']}{d}j {h:02}:{m:02}:{s:02}"
    draw.rectangle((0, 0, W, H), fill=cfg["banner_bg_color"])
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((W - tw) // 2, (H - th) // 2), text, font=font, fill=cfg["banner_text_color"])


def render_progress(draw, cfg, font, d, h, m, s, remaining, total_initial):
    W, H = cfg["width"], cfg["height"]
    pad = cfg["padding"]

    ratio = 1 - (remaining / total_initial)
    ratio = min(max(ratio, 0), 1)

    bh = cfg["progress_height"]
    left = pad
    right = W - pad
    top = H//2 - bh//2
    bottom = top + bh

    draw.rounded_rectangle((left, top, right, bottom), radius=bh//2, fill=cfg["progress_bg_color"])

    filled = left + int((right - left) * ratio)
    draw.rounded_rectangle((left, top, filled, bottom), radius=bh//2, fill=cfg["progress_fg_color"])

    txt = f"{cfg['message_prefix']}{d}j {h:02}:{m:02}:{s:02}"
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((W - tw) // 2, bottom + 10), txt, font=font, fill=cfg["text_color"])


# -----------------------------
# GENERATION GIF
# -----------------------------
@app.route("/c/<countdown_id>.gif")
def countdown_image(countdown_id):
    cfg = load_countdown_config(countdown_id)
    if cfg is None:
        return "Not found", 404

    try:
        end = datetime.fromisoformat(cfg["target_date"])
    except:
        return "Date invalide", 400

    now = datetime.utcnow()
    total_initial = max(int((end - now).total_seconds()), 1)
    frames = []
    loop = cfg.get("loop_duration", 10)

    for i in range(loop):
        t = now + timedelta(seconds=i)
        rem = int((end - t).total_seconds())

        img = Image.new("RGB", (cfg["width"], cfg["height"]), cfg["background_color"])
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(cfg["font_path"], cfg["font_size"])
        except:
            font = ImageFont.load_default()

        if rem <= 0:
            draw_centered(draw, cfg, "⏰ Terminé !", font)
        else:
            d, r = divmod(rem, 86400)
            h, r = divmod(r, 3600)
            m, s = divmod(r, 60)

            tplt = cfg.get("template", "classic")
            if tplt == "classic":
                render_classic(draw, cfg, font, d, h, m, s)
            elif tplt == "blocks":
                render_blocks(draw, cfg, font, d, h, m, s, "rect")
            elif tplt == "flip":
                render_blocks(draw, cfg, font, d, h, m, s, "flip")
            elif tplt == "bubble":
                render_blocks(draw, cfg, font, d, h, m, s, "bubble")
            elif tplt == "minimal":
                render_minimal(draw, cfg, font, d, h, m, s)
            elif tplt == "banner":
                render_banner(draw, cfg, font, d, h, m, s)
            elif tplt == "progress":
                render_progress(draw, cfg, font, d, h, m, s, rem, total_initial)
            else:
                render_classic(draw, cfg, font, d, h, m, s)

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


# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)