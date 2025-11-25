import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, send_file, url_for

import renderer_svg
import renderer_gif

# ============================
# CONFIG GLOBALE
# ============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)

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

    # Gras
    "font_bold": False,
    "label_bold": False,
    "prefix_bold": False,

    # Template CIRCULAR (Pro)
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


def parse_bool(val):
    if not val:
        return False
    return str(val).lower() in ("1", "true", "on", "yes", "y")


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

        # Gras
        cfg["font_bold"] = ("font_bold" in form)
        cfg["label_bold"] = ("label_bold" in form)
        cfg["prefix_bold"] = ("prefix_bold" in form)

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

        # Nouveau countdown → ID
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
    q = request.args

    # Template
    tpl = q.get("template", cfg["template"])
    if tpl not in ("basic", "circular"):
        tpl = "basic"
    cfg["template"] = tpl

    # Commun
    bg = q.get("background_color")
    if bg:
        cfg["background_color"] = bg
    tc = q.get("text_color")
    if tc:
        cfg["text_color"] = tc
    fs = q.get("font_size")
    if fs:
        try:
            cfg["font_size"] = int(fs)
        except Exception:
            pass

    mp = q.get("message_prefix")
    if mp is not None:
        cfg["message_prefix"] = mp

    cfg["show_labels"] = parse_bool(q.get("show_labels"))

    # Gras
    cfg["font_bold"] = parse_bool(q.get("font_bold"))
    cfg["label_bold"] = parse_bool(q.get("label_bold"))
    cfg["prefix_bold"] = parse_bool(q.get("prefix_bold"))

    td_raw = q.get("target_date")
    if td_raw:
        iso = td_raw.replace(" ", "T")
        if len(iso) == 16:
            iso += ":00"
        cfg["target_date"] = iso

    # CIRCULAR
    cb = q.get("circular_base_color")
    if cb:
        cfg["circular_base_color"] = cb
    cp = q.get("circular_progress_color")
    if cp:
        cfg["circular_progress_color"] = cp
    cth = q.get("circular_thickness")
    if cth:
        try:
            cfg["circular_thickness"] = int(cth)
        except Exception:
            pass
    cfg["circular_label_uppercase"] = parse_bool(q.get("circular_label_uppercase"))
    cls = q.get("circular_label_size")
    if cls:
        try:
            cfg["circular_label_size"] = int(cls)
        except Exception:
            pass
    clc = q.get("circular_label_color")
    if clc:
        cfg["circular_label_color"] = clc
    csp = q.get("circular_spacing")
    if csp:
        try:
            cfg["circular_spacing"] = int(csp)
        except Exception:
            pass
    cir = q.get("circular_inner_ratio")
    if cir:
        try:
            cfg["circular_inner_ratio"] = float(cir)
        except Exception:
            pass

    # BASIC
    blc = q.get("basic_label_color")
    if blc:
        cfg["basic_label_color"] = blc
    bls = q.get("basic_label_size")
    if bls:
        try:
            cfg["basic_label_size"] = int(bls)
        except Exception:
            pass
    bgap = q.get("basic_gap")
    if bgap:
        try:
            cfg["basic_gap"] = int(bgap)
        except Exception:
            pass

    svg_str = renderer_svg.svg_preview(cfg)
    return app.response_class(svg_str, mimetype="image/svg+xml")


# ============================
# GÉNÉRATION GIF FINALE
# ============================

@app.route("/c/<countdown_id>.gif")
def countdown_image(countdown_id):
    cfg = load_config(countdown_id)
    if cfg is None:
        return "Compte introuvable", 404

    # Validation date cible
    try:
        end_time = datetime.fromisoformat(cfg["target_date"])
    except Exception:
        return "Date invalide", 400

    buf = renderer_gif.generate_gif(cfg, end_time)
    return send_file(buf, mimetype="image/gif")


# ============================
# MAIN
# ============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
