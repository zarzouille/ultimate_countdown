const htmlPreview = document.getElementById("htmlPreview");
const fontSizeInput = document.getElementById("font_size");
const fontSizeValue = document.getElementById("fontSizeValue");
const templateSelect = document.getElementById("template");
const form = document.getElementById("configForm");

/* ---------- Accordéons ---------- */

document.querySelectorAll(".uc-acc-header").forEach(btn => {
    btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-acc-target");
        if (!targetId) return;
        const body = document.getElementById(targetId);
        if (!body) return;

        const isOpen = body.classList.contains("uc-acc-open");
        if (isOpen) {
            body.classList.remove("uc-acc-open");
            btn.querySelector(".uc-acc-chevron").textContent = "▾";
        } else {
            body.classList.add("uc-acc-open");
            btn.querySelector(".uc-acc-chevron").textContent = "▴";
        }
    });
});

/* ---------- Affichage des sections selon le template ---------- */

function updateTemplateSections() {
    const template = templateSelect.value;
    const sections = document.querySelectorAll(".uc-template-section");

    sections.forEach(sec => {
        const templatesAttr = sec.getAttribute("data-templates") || "";
        const list = templatesAttr.split(",").map(t => t.trim()).filter(Boolean);
        if (list.includes(template)) {
            sec.classList.add("uc-template-visible");
        } else {
            sec.classList.remove("uc-template-visible");
        }
    });
}

/* ---------- Rendu des templates en preview ---------- */

function renderTemplate(template, bg, txt, size, prefix, dateInput) {
    if (!dateInput) {
        return "Choisis une date pour voir l’aperçu.";
    }

    const target = new Date(dateInput);
    const now = new Date();
    const diff = target - now;

    if (isNaN(diff)) {
        return "Date invalide";
    }

    if (diff <= 0) {
        return "⏰ Terminé !";
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
    const labelFactor = parseFloat(document.getElementById("label_size_factor")?.value || "0.5");
    const labelFontSize = size * Math.max(0.3, Math.min(1, labelFactor));

    const blockRadius = parseInt(document.getElementById("block_radius")?.value || "12", 10);
    const blockPadX = parseInt(document.getElementById("block_padding_x")?.value || "14", 10);
    const blockPadY = parseInt(document.getElementById("block_padding_y")?.value || "8", 10);
    const blocksGap = parseInt(document.getElementById("blocks_gap")?.value || "10", 10);

    const showTextShadow = document.getElementById("text_shadow")?.checked;
    const showBlockShadow = document.getElementById("block_shadow")?.checked;
    const blurAmount = parseInt(document.getElementById("blur_amount")?.value || "10", 10);
    const radiusOverride = parseInt(document.getElementById("border_radius_override")?.value || "0", 10);
    const spacingScale = parseFloat(document.getElementById("spacing_scale")?.value || "1");
    const rotateDeg = parseFloat(document.getElementById("rotate_deg")?.value || "0");
    const gradientBg = document.getElementById("gradient_bg")?.checked;
    const gradientText = document.getElementById("gradient_text")?.checked;
    const textOutline = document.getElementById("text_outline")?.checked;
    const gradientStart = document.getElementById("gradient_start")?.value || "#eff6ff";
    const gradientEnd = document.getElementById("gradient_end")?.value || "#dbeafe";
    const stretchY = parseFloat(document.getElementById("stretch_y")?.value || "1");
    const neonGlowColor = document.getElementById("neon_glow_color")?.value || txt;
    const glassBorder = document.getElementById("glass_border_color")?.value || "#d1d5db";
    const glassTint = document.getElementById("glass_bg_tint")?.value || "#e5f0ff";
    const circleAccent = document.getElementById("circle_accent_color")?.value || txt;
    const badgeBg = document.getElementById("badge_bg_color")?.value || "#111827";
    const badgeAccent = document.getElementById("badge_accent_color")?.value || "#3b82f6";

    const baseText = `${prefix}${days}j ${String(hours).padStart(2,"0")}:${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;

    const radiusGlobal = radiusOverride > 0 ? `${radiusOverride}px` : undefined;
    const gapScaled = blocksGap * spacingScale;

    const textShadowBase = showTextShadow
        ? `0 1px 1px rgba(0,0,0,0.18), 0 2px 4px rgba(15,23,42,0.25)`
        : "none";

    const outlineShadow = textOutline
        ? `0 0 1px #ffffff, 0 0 2px #ffffff`
        : "";

    const textShadowCombined = textShadowBase === "none"
        ? outlineShadow || "none"
        : (outlineShadow ? `${textShadowBase}, ${outlineShadow}` : textShadowBase);

    const blockShadow = showBlockShadow
        ? "0 10px 25px rgba(15,23,42,0.15)"
        : "none";

    const gradientBgStyle = gradientBg
        ? `background: linear-gradient(135deg, ${gradientStart}, ${gradientEnd});`
        : `background: ${bg};`;

    const transformWrapper = `transform: rotate(${rotateDeg}deg) scaleY(${stretchY});`;

    const gradientTextStyle = gradientText
        ? `background: linear-gradient(135deg, ${txt}, ${circleAccent});
       -webkit-background-clip: text;
       background-clip: text;
       color: transparent;`
        : `color:${txt};`;

    // --------- Templates ----------

    if (template === "classic") {
        const icon = document.getElementById("icon")?.value || "";
        const line = `${days}j ${String(hours).padStart(2,"0")}:${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;
        return `
      <div style="display:flex;align-items:center;justify-content:center;${transformWrapper}">
        <div style="padding:${10 * spacingScale}px ${14 * spacingScale}px;border-radius:${radiusGlobal || '999px'};${gradientBgStyle}box-shadow:${blockShadow};">
          <div style="display:flex;align-items:center;gap:8px;font-size:${size}px;${gradientTextStyle}text-shadow:${textShadowCombined};">
            ${icon ? `<span>${icon}</span>` : ""}
            <span>${prefix}</span>
            <span>${line}</span>
          </div>
        </div>
      </div>
    `;
    }

    if (template === "blocks") {
        const items = [
            [days, labelDays],
            [hours, labelHours],
            [minutes, labelMinutes],
            [seconds, labelSeconds]
        ];
        return `
      <div style="display:flex;justify-content:center;gap:${gapScaled}px;${transformWrapper}">
        ${items.map(([v, label]) => `
          <div style="
            padding:${blockPadY * spacingScale}px ${blockPadX * spacingScale}px;
            border-radius:${radiusGlobal || blockRadius + 'px'};
            background:${blockBg};
            border:1px solid ${blockBorder};
            min-width:60px;
            text-align:center;
            box-shadow:${blockShadow};
          ">
            <div style="font-size:${size}px;line-height:1.1;${gradientTextStyle}text-shadow:${textShadowCombined};">
              ${String(v).padStart(2,"0")}
            </div>
            ${showLabels
            ? `<div style="margin-top:4px;font-size:${labelFontSize}px;color:#6b7280;">${label}</div>`
            : ""
        }
          </div>
        `).join("")}
      </div>
    `;
    }

    if (template === "flip") {
        const flipDigit = (value, label) => `
      <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
        <div style="
          position:relative;
          width:70px;
          height:60px;
          border-radius:${radiusGlobal || '8px'};
          background:#111827;
          color:${txt};
          box-shadow:${blockShadow};
          overflow:hidden;
        ">
          <div style="
            position:absolute;top:0;left:0;right:0;
            height:50%;display:flex;align-items:center;justify-content:center;
            border-bottom:1px solid rgba(55,65,81,0.9);
            background:#0f172a;
          ">
            <span style="font-size:${size * 0.9}px;text-shadow:${textShadowCombined};">
              ${String(value).padStart(2,"0")}
            </span>
          </div>
          <div style="
            position:absolute;bottom:0;left:0;right:0;
            height:50%;display:flex;align-items:center;justify-content:center;
            background:#020617;
          ">
            <span style="font-size:${size * 0.9}px;text-shadow:${textShadowCombined};">
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
      <div style="display:flex;gap:${gapScaled}px;align-items:flex-end;justify-content:center;${transformWrapper}">
        ${flipDigit(days, labelDays)}
        ${flipDigit(hours, labelHours)}
        ${flipDigit(minutes, labelMinutes)}
        ${flipDigit(seconds, labelSeconds)}
      </div>
    `;
    }

    if (template === "bubble") {
        const bubble = (value, label) => `
      <div style="
        padding:${(blockPadY+2) * spacingScale}px ${(blockPadX+4) * spacingScale}px;
        border-radius:${radiusGlobal || '999px'};
        background:linear-gradient(135deg, rgba(255,255,255,0.9), rgba(219,234,254,0.95));
        border:1px solid rgba(148,163,184,0.7);
        box-shadow:${blockShadow};
        min-width:64px;
        text-align:center;
      ">
        <div style="font-size:${size}px;line-height:1.1;color:#111827;text-shadow:${textShadowCombined};">
          ${String(value).padStart(2,"0")}
        </div>
        ${showLabels
            ? `<div style="margin-top:3px;font-size:${labelFontSize}px;color:#4b5563;">${label}</div>`
            : ""
        }
      </div>
    `;
        return `
      <div style="display:flex;gap:${gapScaled}px;align-items:center;justify-content:center;${transformWrapper}">
        ${bubble(days, labelDays)}
        ${bubble(hours, labelHours)}
        ${bubble(minutes, labelMinutes)}
        ${bubble(seconds, labelSeconds)}
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
      <div style="${transformWrapper}">
        <span style="font-size:${size}px;${gradientTextStyle}text-shadow:${textShadowCombined};">
          ${text}
        </span>
      </div>
    `;
    }

    if (template === "banner") {
        const bannerBg = document.getElementById("banner_bg_color")?.value || "#1d4ed8";
        const bannerTxt = document.getElementById("banner_text_color")?.value || "#ffffff";
        const text =
            `${prefix}${days} jours ${String(hours).padStart(2,"0")}h ` +
            `${String(minutes).padStart(2,"0")}m ${String(seconds).padStart(2,"0")}s`;
        return `
      <div style="width:100%;${transformWrapper}">
        <div style="
          width:100%;
          padding:${10 * spacingScale}px ${16 * spacingScale}px;
          border-radius:${radiusGlobal || '999px'};
          background:${bannerBg};
          color:${bannerTxt};
          font-size:${size * 0.6}px;
          display:flex;
          align-items:center;
          justify-content:center;
          gap:10px;
          box-shadow:${blockShadow};
        ">
          <span>🔔</span>
          <span>${text}</span>
        </div>
      </div>
    `;
    }

    if (template === "progress") {
        const maxDays = parseInt(document.getElementById("progress_max_days")?.value || "30", 10);
        const total = maxDays * 86400;
        let ratio = 1 - (totalSeconds / total);
        ratio = Math.max(0, Math.min(1, ratio));
        const barBg = document.getElementById("progress_bg_color")?.value || "#e5e7eb";
        const barFg = document.getElementById("progress_fg_color")?.value || "#3b82f6";
        const base = `${days}j ${String(hours).padStart(2,"0")}:${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;
        const percent = (ratio * 100).toFixed(0);
        const h = parseInt(document.getElementById("progress_height")?.value || "14", 10);

        return `
      <div style="width:100%;max-width:600px;${transformWrapper}">
        <div style="width:100%;height:${h}px;border-radius:${radiusGlobal || '999px'};background:${barBg};overflow:hidden;">
          <div style="width:${percent}%;height:100%;background:${barFg};transition:width 0.2s ease;"></div>
        </div>
        <div style="margin-top:${8 * spacingScale}px;font-size:${size * 0.6}px;color:#374151;">
          ${prefix}${base} • ${percent}% écoulé
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
      <div style="padding:14px 18px;${transformWrapper}">
        <div style="
          font-size:${size}px;
          font-weight:600;
          letter-spacing:0.09em;
          color:${neonGlowColor};
          text-shadow:${glow};
        ">
          ${text}
        </div>
      </div>
    `;
    }

    if (template === "glass") {
        return `
      <div style="padding:${10 * spacingScale}px;${transformWrapper}">
        <div style="
          padding:${12 * spacingScale}px ${20 * spacingScale}px;
          border-radius:${radiusGlobal || '18px'};
          border:1px solid ${glassBorder};
          background:linear-gradient(135deg, rgba(255,255,255,0.9), ${glassTint});
          box-shadow:${blockShadow};
          backdrop-filter:blur(${blurAmount}px);
          -webkit-backdrop-filter:blur(${blurAmount}px);
          font-size:${size * 0.7}px;
          color:#111827;
        ">
          ${baseText}
        </div>
      </div>
    `;
    }

    if (template === "pill") {
        const line =
            `${days}j • ${String(hours).padStart(2,"0")}h • ` +
            `${String(minutes).padStart(2,"0")}m • ${String(seconds).padStart(2,"0")}s`;
        return `
      <div style="padding:${8 * spacingScale}px;${transformWrapper}">
        <div style="
          display:inline-flex;
          align-items:center;
          justify-content:center;
          padding:${8 * spacingScale}px ${16 * spacingScale}px;
          border-radius:${radiusGlobal || '999px'};
          border:1px solid #d1d5db;
          background:#ffffff;
          box-shadow:${blockShadow};
          gap:10px;
          font-size:${size * 0.6}px;
          color:#111827;
        ">
          <span>⏳</span>
          <span>${line}</span>
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
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;${transformWrapper}">
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
          ${days}j ${String(hours).padStart(2,"0")}h ${String(minutes).padStart(2,"0")}m restants
        </div>
      </div>
    `;
    }

    if (template === "badge") {
        const text =
            `${days}j ${String(hours).padStart(2,"0")}h ${String(minutes).padStart(2,"0")}m`;
        return `
      <div style="padding:${8 * spacingScale}px;${transformWrapper}">
        <div style="
          display:inline-flex;
          flex-direction:column;
          align-items:flex-start;
          gap:4px;
          padding:${8 * spacingScale}px ${12 * spacingScale}px;
          border-radius:${radiusGlobal || '12px'};
          background:${badgeBg};
          border:1px solid ${badgeAccent};
          box-shadow:${blockShadow};
          color:#f9fafb;
          min-width:160px;
        ">
          <div style="font-size:${size * 0.45}px;color:#9ca3af;">Temps restant</div>
          <div style="font-size:${size * 0.9}px;font-weight:600;">
            ${text}
          </div>
        </div>
      </div>
    `;
    }

    return `<span style="font-size:${size}px;">${baseText}</span>`;
}

/* ---------- Update preview ---------- */

function updatePreview() {
    const template = templateSelect.value;
    const bg = document.getElementById("background_color").value;
    const txt = document.getElementById("text_color").value;
    const size = parseInt(fontSizeInput.value || "40", 10);
    const prefix = document.getElementById("message_prefix").value || "Temps restant : ";
    const dateInput = document.getElementById("target_date").value;

    fontSizeValue.textContent = size;

    // Fond du conteneur preview (généraux ou gradient géré dans renderTemplate)
    htmlPreview.style.background = "#f9fafb";
    htmlPreview.style.color = txt;

    const html = renderTemplate(template, bg, txt, size, prefix, dateInput);
    htmlPreview.innerHTML = html;
}

/* ---------- Listeners ---------- */

templateSelect.addEventListener("change", () => {
    updateTemplateSections();
    updatePreview();
});

form.addEventListener("input", () => {
    updatePreview();
});

setInterval(updatePreview, 1000);

// Initialisation
updateTemplateSections();
updatePreview();
