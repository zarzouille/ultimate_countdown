const htmlPreview = document.getElementById("htmlPreview");
const fontSizeInput = document.getElementById("font_size");
const fontSizeValue = document.getElementById("fontSizeValue");
const templateSelect = document.getElementById("template");
const form = document.getElementById("configForm");

/* ========= Accordéons ========= */

document.querySelectorAll(".uc-acc-header").forEach(btn => {
    btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-acc-target");
        if (!targetId) return;
        const body = document.getElementById(targetId);
        if (!body) return;
        const chevron = btn.querySelector(".uc-acc-chevron");

        const isOpen = body.classList.contains("uc-acc-open");
        if (isOpen) {
            body.classList.remove("uc-acc-open");
            if (chevron) chevron.textContent = "▾";
        } else {
            body.classList.add("uc-acc-open");
            if (chevron) chevron.textContent = "▴";
        }
    });
});

/* ========= Sections par template ========= */

function updateTemplateSections() {
    const currentTemplate = templateSelect.value;
    document.querySelectorAll(".uc-template-section").forEach(sec => {
        const list = (sec.getAttribute("data-templates") || "")
            .split(",")
            .map(t => t.trim())
            .filter(Boolean);
        if (list.includes(currentTemplate)) {
            sec.classList.add("uc-template-visible");
        } else {
            sec.classList.remove("uc-template-visible");
        }
    });
}

/* ========= Rendu templates ========= */

function renderTemplate(template, bg, txt, size, prefix, dateValue) {
    if (!dateValue) {
        return "Choisis une date pour voir l’aperçu.";
    }

    const target = new Date(dateValue);
    const now = new Date();
    const diff = target - now;

    if (isNaN(diff)) {
        return "Date invalide";
    }

    if (diff <= 0) {
        return prefix + "⏰ Terminé !";
    }

    const totalSeconds = Math.floor(diff / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    const labelDays = document.getElementById("label_days")?.value || "J";
    const labelHours = document.getElementById("label_hours")?.value || "H";
    const labelMinutes = document.getElementById("label_minutes")?.value || "M";
    const labelSeconds = document.getElementById("label_seconds")?.value || "S";
    const showLabels = document.getElementById("show_labels")?.checked;

    const blockBg = document.getElementById("block_bg_color")?.value || "#f3f4f6";
    const blockBorder = document.getElementById("block_border_color")?.value || "#e5e7eb";
    const blockRadius = parseInt(document.getElementById("block_radius")?.value || "12", 10);
    const blocksGap = parseInt(document.getElementById("blocks_gap")?.value || "10", 10);

    const bannerBg = document.getElementById("banner_bg_color")?.value || "#1d4ed8";
    const bannerTxt = document.getElementById("banner_text_color")?.value || "#ffffff";

    const progressBg = document.getElementById("progress_bg_color")?.value || "#e5e7eb";
    const progressFg = document.getElementById("progress_fg_color")?.value || "#3b82f6";
    const progressHeight = parseInt(document.getElementById("progress_height")?.value || "16", 10);
    const progressMaxDays = parseInt(document.getElementById("progress_max_days")?.value || "30", 10);

    const neonGlowColor = document.getElementById("neon_glow_color")?.value || txt;
    const glassBorder = document.getElementById("glass_border_color")?.value || "#d1d5db";
    const glassTint = document.getElementById("glass_bg_tint")?.value || "#e5f0ff";
    const circleAccent = document.getElementById("circle_accent_color")?.value || txt;
    const badgeBg = document.getElementById("badge_bg_color")?.value || "#111827";
    const badgeAccent = document.getElementById("badge_accent_color")?.value || "#3b82f6";

    const labelFactor = parseFloat(document.getElementById("label_size_factor")?.value || "0.5");
    const labelFontSize = size * Math.max(0.3, Math.min(1, labelFactor));

    const blurAmount = parseInt(document.getElementById("blur_amount")?.value || "10", 10);
    const textShadowEnabled = document.getElementById("text_shadow")?.checked;
    const blockShadowEnabled = document.getElementById("block_shadow")?.checked;
    const rotateDeg = parseFloat(document.getElementById("rotate_deg")?.value || "0");

    const icon = document.getElementById("icon")?.value || "";
    const baseTimeText =
        `${days}j ${String(hours).padStart(2,"0")}:` +
        `${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;

    const textShadow = textShadowEnabled
        ? "0 1px 1px rgba(0,0,0,0.18), 0 2px 4px rgba(15,23,42,0.25)"
        : "none";
    const blockShadow = blockShadowEnabled
        ? "0 10px 25px rgba(15,23,42,0.18)"
        : "none";

    const wrapperTransform = `transform: rotate(${rotateDeg}deg);`;

    // ---------- TEMPLATES ----------

    if (template === "classic") {
        const line = `${prefix}${baseTimeText}`;
        return `
      <div style="${wrapperTransform}">
        <div style="
          display:inline-flex;
          align-items:center;
          gap:8px;
          padding:10px 16px;
          border-radius:999px;
          background:${bg};
          color:${txt};
          box-shadow:${blockShadow};
          font-size:${size}px;
          text-shadow:${textShadow};
        ">
          ${icon ? `<span>${icon}</span>` : ""}
          <span>${line}</span>
        </div>
      </div>
    `;
    }

    if (template === "blocks") {
        const items = [
            [days, labelDays],
            [hours, labelHours],
            [minutes, labelMinutes],
            [seconds, labelSeconds],
        ];
        return `
      <div style="${wrapperTransform}">
        <div style="display:inline-flex;gap:${blocksGap}px;">
          ${items.map(([v, label]) => `
            <div style="
              padding:10px 14px;
              border-radius:${blockRadius}px;
              background:${blockBg};
              border:1px solid ${blockBorder};
              min-width:60px;
              text-align:center;
              box-shadow:${blockShadow};
            ">
              <div style="font-size:${size}px;color:${txt};text-shadow:${textShadow};">
                ${String(v).padStart(2,"0")}
              </div>
              ${showLabels
            ? `<div style="margin-top:4px;font-size:${labelFontSize}px;color:#6b7280;">${label}</div>`
            : ""
        }
            </div>
          `).join("")}
        </div>
      </div>
    `;
    }

    if (template === "flip") {
        const flipDigit = (value, label) => `
      <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
        <div style="
          position:relative;
          width:70px;
          height:60px;
          border-radius:${blockRadius}px;
          background:#111827;
          color:${txt};
          box-shadow:${blockShadow};
          overflow:hidden;
        ">
          <div style="
            position:absolute;top:0;left:0;right:0;height:50%;
            display:flex;align-items:center;justify-content:center;
            border-bottom:1px solid rgba(55,65,81,0.9);
            background:#0f172a;
          ">
            <span style="font-size:${size * 0.9}px;text-shadow:${textShadow};">
              ${String(value).padStart(2,"0")}
            </span>
          </div>
          <div style="
            position:absolute;bottom:0;left:0;right:0;height:50%;
            display:flex;align-items:center;justify-content:center;
            background:#020617;
          ">
            <span style="font-size:${size * 0.9}px;text-shadow:${textShadow};">
              ${String(value).padStart(2,"0")}
            </span>
          </div>
        </div>
        ${showLabels
            ? `<div style="font-size:${labelFontSize}px;color:#6b7280;">${label}</div>`
            : ""
        }
      </div>
    `;
        return `
      <div style="${wrapperTransform}">
        <div style="display:inline-flex;gap:${blocksGap}px;align-items:flex-end;">
          ${flipDigit(days, labelDays)}
          ${flipDigit(hours, labelHours)}
          ${flipDigit(minutes, labelMinutes)}
          ${flipDigit(seconds, labelSeconds)}
        </div>
      </div>
    `;
    }

    if (template === "bubble") {
        const bubble = (value, label) => `
      <div style="
        padding:10px 16px;
        border-radius:999px;
        background:linear-gradient(135deg, #ffffff, #e5edff);
        border:1px solid #d1d5db;
        box-shadow:${blockShadow};
        min-width:68px;
        text-align:center;
      ">
        <div style="font-size:${size}px;color:${txt};text-shadow:${textShadow};">
          ${String(value).padStart(2,"0")}
        </div>
        ${showLabels
            ? `<div style="margin-top:2px;font-size:${labelFontSize}px;color:#6b7280;">${label}</div>`
            : ""
        }
      </div>
    `;
        return `
      <div style="${wrapperTransform}">
        <div style="display:inline-flex;gap:${blocksGap}px;align-items:center;">
          ${bubble(days, labelDays)}
          ${bubble(hours, labelHours)}
          ${bubble(minutes, labelMinutes)}
          ${bubble(seconds, labelSeconds)}
        </div>
      </div>
    `;
    }

    if (template === "minimal") {
        const text =
            `${String(days).padStart(2,"0")}:` +
            `${String(hours).padStart(2,"0")}:` +
            `${String(minutes).padStart(2,"0")}:` +
            `${String(seconds).padStart(2,"0")}`;
        return `
      <div style="${wrapperTransform}">
        <span style="font-size:${size}px;color:${txt};text-shadow:${textShadow};">
          ${prefix}${text}
        </span>
      </div>
    `;
    }

    if (template === "banner") {
        const text = `${prefix}${baseTimeText}`;
        return `
      <div style="${wrapperTransform}">
        <div style="
          display:inline-flex;
          align-items:center;
          justify-content:center;
          padding:10px 18px;
          border-radius:999px;
          background:${bannerBg};
          color:${bannerTxt};
          font-size:${size * 0.6}px;
          gap:8px;
          box-shadow:${blockShadow};
        ">
          <span>🔔</span>
          <span>${text}</span>
        </div>
      </div>
    `;
    }

    if (template === "progress") {
        const total = progressMaxDays * 86400;
        let ratio = 1 - (totalSeconds / total);
        ratio = Math.max(0, Math.min(1, ratio));
        const percent = (ratio * 100).toFixed(0);
        return `
      <div style="${wrapperTransform}">
        <div style="width:100%;max-width:480px;">
          <div style="
            width:100%;
            height:${progressHeight}px;
            border-radius:999px;
            background:${progressBg};
            overflow:hidden;
          ">
            <div style="
              width:${percent}%;
              height:100%;
              background:${progressFg};
              transition:width 0.2s ease;
            "></div>
          </div>
          <div style="margin-top:8px;font-size:${size * 0.6}px;color:#374151;">
            ${prefix}${baseTimeText} • ${percent}% écoulé
          </div>
        </div>
      </div>
    `;
    }

    if (template === "neon") {
        const text =
            `${String(days).padStart(2,"0")} : ` +
            `${String(hours).padStart(2,"0")} : ` +
            `${String(minutes).padStart(2,"0")} : ` +
            `${String(seconds).padStart(2,"0")}`;
        const glow = `
      0 0 4px ${neonGlowColor},
      0 0 8px ${neonGlowColor},
      0 0 12px ${neonGlowColor},
      0 0 18px ${neonGlowColor}
    `;
        return `
      <div style="${wrapperTransform}">
        <div style="
          padding:10px 16px;
          border-radius:999px;
          background:#020617;
          box-shadow:${blockShadow};
        ">
          <div style="
            font-size:${size}px;
            font-weight:600;
            letter-spacing:0.08em;
            color:${neonGlowColor};
            text-shadow:${glow};
          ">
            ${prefix}${text}
          </div>
        </div>
      </div>
    `;
    }

    if (template === "glass") {
        return `
      <div style="${wrapperTransform}">
        <div style="
          padding:12px 20px;
          border-radius:18px;
          border:1px solid ${glassBorder};
          background:linear-gradient(135deg, rgba(255,255,255,0.9), ${glassTint});
          box-shadow:${blockShadow};
          backdrop-filter:blur(${blurAmount}px);
          -webkit-backdrop-filter:blur(${blurAmount}px);
          font-size:${size * 0.7}px;
          color:#111827;
        ">
          ${prefix}${baseTimeText}
        </div>
      </div>
    `;
    }

    if (template === "pill") {
        const line =
            `${days}j • ${String(hours).padStart(2,"0")}h • ` +
            `${String(minutes).padStart(2,"0")}m • ${String(seconds).padStart(2,"0")}s`;
        return `
      <div style="${wrapperTransform}">
        <div style="
          display:inline-flex;
          align-items:center;
          gap:8px;
          padding:8px 16px;
          border-radius:999px;
          border:1px solid #d1d5db;
          background:#ffffff;
          box-shadow:${blockShadow};
          font-size:${size * 0.6}px;
          color:#111827;
        ">
          ${icon ? `<span>${icon}</span>` : "<span>⏳</span>"}
          <span>${prefix}${line}</span>
        </div>
      </div>
    `;
    }

    if (template === "circle") {
        const maxDays = 30;
        const total = maxDays * 86400;
        let ratio = 1 - (totalSeconds / total);
        ratio = Math.max(0, Math.min(1, ratio));
        const percent = (ratio * 100).toFixed(0);
        return `
      <div style="${wrapperTransform}">
        <div style="display:inline-flex;flex-direction:column;align-items:center;gap:8px;">
          <div style="
            width:140px;
            height:140px;
            border-radius:50%;
            border:8px solid #e5e7eb;
            position:relative;
          ">
            <div style="
              position:absolute;
              inset:10px;
              border-radius:50%;
              background:conic-gradient(${circleAccent} ${percent}%, #e5e7eb ${percent}%);
              display:flex;
              align-items:center;
              justify-content:center;
              color:#111827;
              font-size:${size * 0.6}px;
            ">
              ${percent}%
            </div>
          </div>
          <div style="font-size:${size * 0.55}px;color:#374151;">
            ${prefix}${days}j ${String(hours).padStart(2,"0")}h ${String(minutes).padStart(2,"0")}m
          </div>
        </div>
      </div>
    `;
    }

    if (template === "badge") {
        const text =
            `${days}j ${String(hours).padStart(2,"0")}h ${String(minutes).padStart(2,"0")}m`;
        return `
      <div style="${wrapperTransform}">
        <div style="
          display:inline-flex;
          flex-direction:column;
          align-items:flex-start;
          gap:4px;
          padding:8px 12px;
          border-radius:12px;
          background:${badgeBg};
          border:1px solid ${badgeAccent};
          box-shadow:${blockShadow};
          color:#f9fafb;
          min-width:160px;
          font-size:${size * 0.6}px;
        ">
          <div style="font-size:${size * 0.45}px;color:#9ca3af;">${prefix || "Temps restant :"}</div>
          <div style="font-size:${size * 0.9}px;font-weight:600;">
            ${text}
          </div>
        </div>
      </div>
    `;
    }

    return `
    <span style="font-size:${size}px;color:${txt};text-shadow:${textShadow};">
      ${prefix}${baseTimeText}
    </span>
  `;
}

/* ========= Update preview ========= */

function updatePreview() {
    const template = templateSelect.value;
    const bg = document.getElementById("background_color").value;
    const txt = document.getElementById("text_color").value;
    const size = parseInt(fontSizeInput.value || "40", 10);
    const prefix = document.getElementById("message_prefix").value || "Temps restant : ";
    const dateValue = document.getElementById("target_date").value;
    const padding = parseInt(document.getElementById("padding")?.value || "0", 10);
    const alignment = document.getElementById("alignment").value; // left, center, right

    fontSizeValue.textContent = size;

    // Styles du conteneur PRÉVIEW
    htmlPreview.style.backgroundColor = bg;
    htmlPreview.style.color = txt;
    htmlPreview.style.padding = padding + "px";
    htmlPreview.style.textAlign = alignment;

    const inner = renderTemplate(template, bg, txt, size, prefix, dateValue);

    // On enveloppe toujours dans un inline-block pour que text-align fonctionne
    htmlPreview.innerHTML = `
    <div style="display:inline-block;">
      ${inner}
    </div>
  `;
}

/* ========= Listeners ========= */

templateSelect.addEventListener("change", () => {
    updateTemplateSections();
    updatePreview();
});

form.addEventListener("input", () => {
    updatePreview();
});

setInterval(updatePreview, 1000);

// init
updateTemplateSections();
updatePreview();