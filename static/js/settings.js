const htmlPreview = document.getElementById("htmlPreview");
const miniPreview = document.getElementById("miniPreview");
const fontSizeInput = document.getElementById("font_size");
const fontSizeValue = document.getElementById("fontSizeValue");

function renderTemplate(template, bg, txt, size, prefix, dateInput) {
    if (!dateInput) {
        return {
            largeHTML: "Choisis une date pour voir l’aperçu.",
            miniHTML: "Choisis une date pour voir l’aperçu."
        };
    }

    const target = new Date(dateInput);
    const now = new Date();
    const diff = target - now;

    if (isNaN(diff)) {
        return {
            largeHTML: "Date invalide",
            miniHTML: "Date invalide"
        };
    }

    if (diff <= 0) {
        return {
            largeHTML: "⏰ Terminé !",
            miniHTML: "⏰ Terminé !"
        };
    }

    const totalSeconds = Math.floor(diff / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    const labelDays = document.getElementById("label_days").value || "J";
    const labelHours = document.getElementById("label_hours").value || "H";
    const labelMinutes = document.getElementById("label_minutes").value || "M";
    const labelSeconds = document.getElementById("label_seconds").value || "S";
    const showLabels = document.getElementById("show_labels").checked;
    const blockBg = document.getElementById("block_bg_color").value;
    const blockBorder = document.getElementById("block_border_color").value;
    const labelFactor = parseFloat(document.getElementById("label_size_factor").value || "0.5");
    const labelFontSize = size * Math.max(0.3, Math.min(1, labelFactor));

    // CLASSIC
    if (template === "classic") {
        const icon = document.getElementById("icon").value || "";
        const textBase =
            `${prefix}${days}j ${String(hours).padStart(2,"0")}:` +
            `${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;
        const largeHTML = `
      <div style="font-size:${size}px; display:flex; align-items:center; justify-content:center; gap:8px;">
        ${icon ? `<span>${icon}</span>` : ""}
        <span>${textBase}</span>
      </div>
    `;
        const miniHTML = `<span style="font-size:${size * 0.6}px;">${textBase}</span>`;
        return { largeHTML, miniHTML };
    }

    // BLOCKS
    if (template === "blocks") {
        const largeHTML = `
      <div style="display:flex;gap:10px;align-items:flex-end;justify-content:center;">
        ${[["days", days, labelDays],["hours",hours,labelHours],["minutes",minutes,labelMinutes],["seconds",seconds,labelSeconds]]
            .map(([_, val, label]) => `
            <div style="
              padding:10px 14px;
              border-radius:12px;
              background:${blockBg};
              border:1px solid ${blockBorder};
              min-width:60px;
              text-align:center;
              box-shadow:0 10px 25px rgba(15,23,42,0.55);
            ">
              <div style="font-size:${size}px;line-height:1.1;">${String(val).padStart(2,"0")}</div>
              ${showLabels ? `<div style="margin-top:4px;font-size:${labelFontSize}px;color:#9ca3af;">${label}</div>` : ""}
            </div>
          `).join("")}
      </div>
    `;
        const miniHTML = `
      <div style="display:flex;gap:6px;justify-content:center;font-size:${size * 0.5}px;">
        <span>${String(days).padStart(2,"0")}${showLabels ? " " + labelDays : ""}</span>
        <span>${String(hours).padStart(2,"0")}${showLabels ? " " + labelHours : ""}</span>
        <span>${String(minutes).padStart(2,"0")}${showLabels ? " " + labelMinutes : ""}</span>
        <span>${String(seconds).padStart(2,"0")}${showLabels ? " " + labelSeconds : ""}</span>
      </div>
    `;
        return { largeHTML, miniHTML };
    }

    // FLIP
    if (template === "flip") {
        const flipDigit = (value, label) => `
      <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
        <div style="
          position:relative;
          width:70px;
          height:60px;
          border-radius:8px;
          background:#111827;
          color:${txt};
          box-shadow:0 12px 25px rgba(0,0,0,0.7);
          overflow:hidden;
        ">
          <div style="
            position:absolute;top:0;left:0;right:0;
            height:50%;display:flex;align-items:center;justify-content:center;
            border-bottom:1px solid rgba(55,65,81,0.9);
            background:#111827;
          ">
            <span style="font-size:${size * 0.9}px;">${String(value).padStart(2,"0")}</span>
          </div>
          <div style="
            position:absolute;bottom:0;left:0;right:0;
            height:50%;display:flex;align-items:center;justify-content:center;
            background:#020617;
          ">
            <span style="font-size:${size * 0.9}px;">${String(value).padStart(2,"0")}</span>
          </div>
        </div>
        ${showLabels ? `<div style="font-size:${labelFontSize}px;color:#9ca3af;">${label}</div>` : ""}
      </div>
    `;

        const largeHTML = `
      <div style="display:flex;gap:10px;align-items:flex-end;justify-content:center;">
        ${flipDigit(days, labelDays)}
        ${flipDigit(hours, labelHours)}
        ${flipDigit(minutes, labelMinutes)}
        ${flipDigit(seconds, labelSeconds)}
      </div>
    `;
        const miniHTML = `
      <div style="display:flex;gap:4px;justify-content:center;font-size:${size * 0.5}px;">
        <span>${String(days).padStart(2,"0")}j</span>
        <span>${String(hours).padStart(2,"0")}h</span>
        <span>${String(minutes).padStart(2,"0")}m</span>
        <span>${String(seconds).padStart(2,"0")}s</span>
      </div>
    `;
        return { largeHTML, miniHTML };
    }

    // BUBBLE
    if (template === "bubble") {
        const bubble = (value, label) => `
      <div style="
        padding:10px 16px;
        border-radius:999px;
        background:linear-gradient(135deg, rgba(255,255,255,0.12), rgba(148,163,184,0.12));
        border:1px solid rgba(148,163,184,0.45);
        box-shadow:0 12px 30px rgba(15,23,42,0.8);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        text-align:center;
        min-width:64px;
      ">
        <div style="font-size:${size}px;line-height:1.1;">${String(value).padStart(2,"0")}</div>
        ${showLabels ? `<div style="margin-top:3px;font-size:${labelFontSize}px;color:#e5e7eb;">${label}</div>` : ""}
      </div>
    `;

        const largeHTML = `
      <div style="display:flex;gap:12px;align-items:center;justify-content:center;">
        ${bubble(days, labelDays)}
        ${bubble(hours, labelHours)}
        ${bubble(minutes, labelMinutes)}
        ${bubble(seconds, labelSeconds)}
      </div>
    `;
        const miniHTML = `
      <div style="display:flex;gap:6px;justify-content:center;font-size:${size * 0.5}px;">
        <span style="padding:3px 8px;border-radius:999px;border:1px solid rgba(148,163,184,0.6);">
          ${String(days).padStart(2,"0")}
        </span>
        <span style="padding:3px 8px;border-radius:999px;border:1px solid rgba(148,163,184,0.4);">
          ${String(hours).padStart(2,"0")}
        </span>
        <span style="padding:3px 8px;border-radius:999px;border:1px solid rgba(148,163,184,0.4);">
          ${String(minutes).padStart(2,"0")}
        </span>
        <span style="padding:3px 8px;border-radius:999px;border:1px solid rgba(148,163,184,0.4);">
          ${String(seconds).padStart(2,"0")}
        </span>
      </div>
    `;
        return { largeHTML, miniHTML };
    }

    // MINIMAL
    if (template === "minimal") {
        const largeText =
            `${String(days).padStart(2,"0")}:` +
            `${String(hours).padStart(2,"0")}:` +
            `${String(minutes).padStart(2,"0")}:` +
            `${String(seconds).padStart(2,"0")}`;
        return {
            largeHTML: `<span style="font-size:${size}px;">${largeText}</span>`,
            miniHTML: `<span style="font-size:${size * 0.6}px;">${largeText}</span>`
        };
    }

    // BANNER
    if (template === "banner") {
        const bannerBg = document.getElementById("banner_bg_color").value;
        const bannerTxt = document.getElementById("banner_text_color").value;
        const text =
            `${prefix}${days} jours ${String(hours).padStart(2,"0")}h ` +
            `${String(minutes).padStart(2,"0")}m ${String(seconds).padStart(2,"0")}s`;

        const largeHTML = `
      <div style="
        width:100%;
        padding:12px 18px;
        border-radius:999px;
        background:${bannerBg};
        color:${bannerTxt};
        font-size:${size * 0.6}px;
        display:flex;
        align-items:center;
        justify-content:center;
        gap:8px;
      ">
        <span>🔔</span><span>${text}</span>
      </div>
    `;
        const miniHTML = `
      <div style="font-size:${size * 0.5}px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        ${text}
      </div>
    `;
        return { largeHTML, miniHTML };
    }

    // PROGRESS
    if (template === "progress") {
        const maxDays = parseInt(document.getElementById("progress_max_days").value || "30", 10);
        const total = maxDays * 86400;
        let ratio = 1 - (totalSeconds / total);
        ratio = Math.max(0, Math.min(1, ratio));
        const barBg = document.getElementById("progress_bg_color").value;
        const barFg = document.getElementById("progress_fg_color").value;

        const baseText =
            `${prefix}${days}j ${String(hours).padStart(2,"0")}:` +
            `${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;

        const largeHTML = `
      <div style="width:100%;max-width:600px;">
        <div style="width:100%;height:16px;border-radius:999px;background:${barBg};overflow:hidden;">
          <div style="width:${(ratio*100).toFixed(1)}%;height:100%;background:${barFg};"></div>
        </div>
        <div style="margin-top:10px;font-size:${size * 0.6}px;">
          ${baseText}
        </div>
      </div>
    `;
        const miniHTML = `
      <div style="width:100%;">
        <div style="width:100%;height:8px;border-radius:999px;background:${barBg};overflow:hidden;">
          <div style="width:${(ratio*100).toFixed(1)}%;height:100%;background:${barFg};"></div>
        </div>
      </div>
    `;
        return { largeHTML, miniHTML };
    }

    const fallback = `${prefix}${days}j ${String(hours).padStart(2,"0")}:${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;
    return {
        largeHTML: `<span style="font-size:${size}px;">${fallback}</span>`,
        miniHTML: `<span style="font-size:${size * 0.5}px;">${fallback}</span>`
    };
}

function updatePreview() {
    const template = document.getElementById("template").value;
    const bg = document.getElementById("background_color").value;
    const txt = document.getElementById("text_color").value;
    const size = parseInt(fontSizeInput.value || "40", 10);
    const prefix = document.getElementById("message_prefix").value || "Temps restant : ";
    const dateInput = document.getElementById("target_date").value;

    fontSizeValue.textContent = size;

    htmlPreview.style.background = bg;
    htmlPreview.style.color = txt;
    miniPreview.style.background = "radial-gradient(circle at top left,#020617 0,#020617 40%,#020617 100%)";
    miniPreview.style.color = txt;

    const { largeHTML, miniHTML } = renderTemplate(template, bg, txt, size, prefix, dateInput);

    htmlPreview.innerHTML = largeHTML;
    miniPreview.innerHTML = miniHTML;
}

setInterval(updatePreview, 1000);
document.getElementById("configForm").addEventListener("input", updatePreview);
updatePreview();