import os
import json
from datetime import datetime
from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

CONFIG_PATH = "config.json"

# --- 1️⃣ Chargement de la configuration ---
def load_config():
    """Charge le fichier de configuration ou renvoie les valeurs par défaut."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Erreur de lecture du config.json — fichier réinitialisé.")
    # Valeurs par défaut
    return {
        "target_date": "2025-12-31T23:59",
        "background_color": "#000000",
        "text_color": "#FFFFFF",
        "font_size": 40,
        "message_prefix": "Temps restant :"
    }

CONFIG = load_config()

# --- 2️⃣ Sauvegarde de la config ---
def save_config():
    """Sauvegarde la configuration actuelle dans le fi
