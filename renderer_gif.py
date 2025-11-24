from datetime import datetime, timedelta
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SCALE = 4  # supersampling x4


def _load_font(px_size: int):
    try:
        return ImageFont.truetype(FONT_PATH, px_size)
    except Exception:
        return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    return w, h


# ============================
# BASIC TEMPLATE
# ============================

def _draw_basic_frame(draw, cfg, days, hours, minutes, seconds):
    W = cfg["width"] * SCALE
    H = cfg["height"] * SCALE

    main_font = _load_font(cfg["font_size"] * SCALE)
    label_font = _load_font(cfg["basic_label_size"] * SCALE)

    units = [("J", days), ("H", hours), ("M", minutes), ("S", seconds)]
    gap = cfg["basic_gap"] * SCALE
    show_labels = cfg["show_labels"]

    prefix = cfg.get("message_prefix") or ""
    if prefix:
        prefix_font = _load_font(int(cfg["font_size"] * 0.6) * SCALE)
        tw, th = _text_size(draw, prefix, prefix_font)
        draw.text(
            ((W - tw) // 2, 18 * SCALE),
            prefix,
            font=prefix_font,
            fill=cfg["text_color"],
        )

    blocks = []
    between = 18 * SCALE
    total_w = 0

    for label, val in units:
        val_txt = f"{val:02}"
        tw, th = _text_size(draw, val_txt, main_font)
        if show_labels:
            lw, lh = _text_size(draw, label, label_font)
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

        vx = x + (bw - b["tw"]) // 2
        vy = top
        draw.text((vx, vy), b["val"], font=main_font, fill=cfg["text_color"])

        if show_labels:
            lx = x + (bw - b["lw"]) // 2
            ly = vy + b["th"] + gap
            draw.text(
                (lx, ly),
                b["label"],
                font=label_font,
                fill=cfg["basic_label_color"],
            )

        x += bw + between


# ============================
# CIRCULAR TEMPLATE
# ============================

def _draw_circular_frame(draw, cfg, days, hours, minutes, seconds):
    W = cfg["width"] * SCALE
    H = cfg["height"] * SCALE

    base_color = cfg["circular_base_color"]
    progress_color = cfg["circular_progress_color"]
    thickness = max(1, cfg["circular_thickness"] * SCALE)
    spacing = cfg["circular_spacing"] * SCALE

    units = [("J", days, 30), ("H", hours, 24),
             ("M", minutes, 60), ("S", seconds, 60)]

    padding = 40 * SCALE
    available_w = W - padding * 2
    count = 4
    radius = int((available_w - (count - 1) * spacing) / (count * 2))
    radius = max(radius, 20 * SCALE)

    center_y = H // 2 + 4 * SCALE

    font_main = _load_font(cfg["font_size"] * SCALE)
    font_label = _load_font(cfg["circular_label_size"] * SCALE)

    prefix = cfg.get("message_prefix") or ""
    if prefix:
        prefix_font = _load_font(int(cfg["font_size"] * 0.6) * SCALE)
        tw, th = _text_size(draw, prefix, prefix_font)
        draw.text(
            ((W - tw) // 2, center_y - radius - th - 8 * SCALE),
            prefix,
            font=prefix_font,
            fill=cfg["text_color"],
        )

    total_width = count * (2 * radius) + (count - 1) * spacing
    start_x = (W - total_width) // 2

    for i, (label, value, max_value) in enumerate(units):
        ratio = 0 if max_value <= 0 else max(0.0, min(value / max_value, 1.0))
        cx = start_x + radius + i * (2 * radius + spacing)
        cy = center_y

        draw.arc(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            start=0, end=359,
            fill=base_color,
            width=thickness,
        )

        end_angle = -90 + 360 * ratio
        draw.arc(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            start=-90, end=end_angle,
            fill=progress_color,
            width=thickness,
        )

        # 🔥 FIX CENTRAGE PARFAIT
        num_txt = f"{value:02}"
        bbox = draw.textbbox((0, 0), num_txt, font=font_main)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        text_x = cx - tw / 2
        text_y = cy - th / 2   # CORRECTION

        draw.text(
            (text_x, text_y),
            num_txt,
            font=font_main,
            fill=cfg["text_color"],
        )

        if cfg["show_labels"]:
            lbl = label.upper() if cfg["circular_label_uppercase"] else label
            lw, lh = _text_size(draw, lbl, font_label)
            draw.text(
                (cx - lw // 2, cy + radius + 8 * SCALE),
                lbl,
                font=font_label,
                fill=cfg["circular_label_color"],
            )


# ============================
# GÉNÉRATION DU GIF COMPLET
# ============================

def generate_gif(cfg: dict, end_time: datetime) -> BytesIO:
    now = datetime.utcnow()
    loop_duration = int(cfg.get("loop_duration", 20))

    frames = []

    for i in range(loop_duration):
        current = now + timedelta(seconds=i)
        remaining = int((end_time - current).total_seconds())

        big = Image.new(
            "RGB",
            (cfg["width"] * SCALE, cfg["height"] * SCALE),
            cfg["background_color"],
        )
        draw = ImageDraw.Draw(big)

        if remaining <= 0:
            txt = "⏰ Terminé !"
            font_big = _load_font(cfg["font_size"] * SCALE)
            tw, th = _text_size(draw, txt, font_big)
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

            if cfg.get("template") == "circular":
                _draw_circular_frame(draw, cfg, days, hours, minutes, seconds)
            else:
                _draw_basic_frame(draw, cfg, days, hours, minutes, seconds)

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
    return buf