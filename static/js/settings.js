const htmlPreview = document.getElementById("htmlPreview");
const fontSizeInput = document.getElementById("font_size");
const fontSizeValue = document.getElementById("fontSizeValue");
const form = document.getElementById("configForm");
const templateInput = document.getElementById("templateInput");
const designSection = document.getElementById("designSection");

const templateCards = document.querySelectorAll(".uc-template-card");

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

function updateTemplateSections(selectedTemplate) {
    document.querySelectorAll(".uc-template-section").forEach(sec => {
        const list = (sec.getAttribute("data-templates") || "")
            .split(",")
            .map(t => t.trim())
            .filter(Boolean);
        if (list.includes(selectedTemplate)) {
            sec.classList.add("uc-template-visible");
        } else {
            sec.classList.remove("uc-template-visible");
        }
    });
}

/* ========= Sélection des cartes de template ========= */

function selectTemplate(template) {
    templateInput.value = template;

    templateCards.forEach(card => {
        if (card.getAttribute("data-template") === template) {
            card.classList.add("uc-template-selected");
        } else {
            card.classList.remove("uc-template-selected");
        }
    });

    // Afficher la section design dès qu’un template est choisi
    if (designSection) {
        designSection.style.display = "block";
    }

    updateTemplateSections(template);
    updatePreview();
}

templateCards.forEach(card => {
    card.addEventListener("click", () => {
        const tpl = card.getAttribute("data-template");
        if (!tpl) return;
        selectTemplate(tpl);
    });
});

/* ========= Rendu templates HTML (preview) ========= */

function renderTemplate(template, config) {
    const {
        bg,
        txt,
        size,
        prefix,
        dateValue,
        padding,
        icon
    } = config;

    if (!template) {
        return "Choisis un template pour commencer.";
    }

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

    const labelDays = (document.getElementById("label_days")?.value || "J");
    const labelHours = (document.getElementById("label_hours")?.value || "H");
    const labelMinutes = (document.getElementById("label_minutes")?.value || "M");
    const labelSeconds = (document.getElementById("label_seconds")?.value || "S");

    const showLabels = document.getElementById("show_labels")?.checked;
    const labelColor = document.getElementById("label_color")?.value || "#6b7280";

    const blockBg = document.getElementById("block_bg_color")?.value || "#f9fafb";
    const blockBorder = document.getElementById("block_border_color")?.value || "#d1d5db";
    const blockBorderWidth = parseInt(document.getElementById("block_border_width")?.value || "1", 10);
    const blockRadius = parseInt(document.getElementById("block_radius")?.value || "12", 10);
    const blocksGap = parseInt(document.getElementById("blocks_gap")?.value || "10", 10);

    const bannerBg = document.getElementById("banner_bg_color")?.value || "#111827";
    const bannerTxt = document.getElementById("banner_text_color")?.value || "#f9fafb";

    const progressBg = document.getElementById("progress_bg_color")?.value || "#e5e7eb";
    const progressFg = document.getElementById("progress_fg_color")?.value || "#3b82f6";
    const progressHeight = parseInt(document.getElementById("progress_height")?.value || "16", 10);
    const progressMaxDays = parseInt(document.getElementById("progress_max_days")?.value || "30", 10);

    const circleStrokeBubble = parseInt(document.getElementById("circle_stroke_width")?.value || "4", 10);
    const circleStrokeWidth = parseInt(document.getElementById("circle_stroke_width")?.value || "8", 10);
    const circleBgColor = document.getElementById("circle_bg_color")?.value || "#e5e7eb";
    const circleFgColor = document.getElementById("circle_fg_color")?.value || "#3b82f6";

    const pillBg = document.getElementById("pill_bg_color")?.value || "#ffffff";
    const pillRadius = parseInt(document.getElementById("pill_radius")?.value || "999", 10);
    const pillPadX = parseInt(document.getElementById("pill_padding_x")?.value || "16", 10);
    const pillPadY = parseInt(document.getElementById("pill_padding_y")?.value || "8", 10);

    const badgeBg = document.getElementById("badge_bg_color")?.value || "#111827";
    const badgeBorderColor = document.getElementById("badge_border_color")?.value || "#3b82f6";
    const badgeBorderWidth = parseInt(document.getElementById("badge_border_width")?.value || "1", 10);
    const badgeRadius = parseInt(document.getElementById("badge_radius")?.value || "10", 10);

    const baseTimeText =
        `${days}j ${String(hours).padStart(2,"0")}:` +
        `${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;

    const labelFontSize = size * 0.45;

    // Templates

    if (template === "classic") {
        const line = `${prefix}${baseTimeText}`;
        return `
      <div>
        <div style="
          display:inline-flex;
          align-items:center;
          gap:8px;
          padding:10px 16px;
          border-radius:999px;
          background:${bg};
          color:${txt};
          font-size:${size}px;
        ">
          ${icon ? `<span>${icon}</span>` : ""}
          <span>${line}</span>
        </div>
      </div>
    `;
    }

    if (template === "blocks" || template === "flip" || template === "bubble") {
        const items = [
            [days, labelDays],
            [hours, labelHours],
            [minutes, labelMinutes],
            [seconds, labelSeconds],
        ];

        const isFlip = (template === "flip");
        const isBubble = (template === "bubble");

        return `
      <div>
        <div style="display:inline-flex;gap:${blocksGap}px;align-items:flex-end;">
          ${items.map(([v, label]) => {
            const value = String(v).padStart(2,"0");
            if (isBubble) {
                return `
                <div style="
                  position:relative;
                  width:auto;
                  padding:${pillPadY || 8}px ${pillPadX || 16}px;
                  border-radius:999px;
                  background:${blockBg};
                  border:${blockBorderWidth}px solid ${blockBorder};
                  box-shadow:none;
                ">
                  <div style="font-size:${size}px;color:${txt};">
                    ${value}
                  </div>
                  ${showLabels ? `
                    <div style="margin-top:2px;font-size:${labelFontSize}px;color:${labelColor};text-align:center;">
                      ${label}
                    </div>` : ""}
                  <div style="
                    position:absolute;
                    inset:2px;
                    border-radius:999px;
                    border:${circleStrokeBubble}px solid rgba(255,255,255,0.35);
                    pointer-events:none;
                  "></div>
                </div>
              `;
            } else {
                return `
                <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
                  <div style="
                    position:relative;
                    min-width:60px;
                    padding:8px 12px;
                    border-radius:${blockRadius}px;
                    background:${blockBg};
                    border:${blockBorderWidth}px solid ${blockBorder};
                    overflow:hidden;
                  ">
                    ${isFlip ? `
                      <div style="
                        position:absolute;
                        left:0;right:0;
                        top:50%;
                        height:0;
                        border-top:1px solid rgba(0,0,0,0.2);
                      "></div>` : ""}
                    <div style="
                      font-size:${size}px;
                      color:${txt};
                      text-align:center;
                    ">
                      ${value}
                    </div>
                  </div>
                  ${showLabels ? `
                    <div style="font-size:${labelFontSize}px;color:${labelColor};">
                      ${label}
                    </div>` : ""}
                </div>
              `;
            }
        }).join("")}
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
      <div>
        <span style="font-size:${size}px;color:${txt};">
          ${prefix}${text}
        </span>
      </div>
    `;
    }

    if (template === "banner") {
        const text = `${prefix}${baseTimeText}`;
        return `
      <div>
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
        ">
          <span>🔔</span>
          <span>${text}</span>
        </div>
      </div>
    `;
    }

    if (template === "progress") {
        const maxSecs = progressMaxDays * 86400;
        let ratio = 1 - (totalSeconds / maxSecs);
        ratio = Math.max(0, Math.min(1, ratio));
        const percent = (ratio * 100).toFixed(0);
        return `
      <div>
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

    if (template === "pill") {
        const line =
            `${days}j • ${String(hours).padStart(2,"0")}h • ` +
            `${String(minutes).padStart(2,"0")}m • ${String(seconds).padStart(2,"0")}s`;
        return `
      <div>
        <div style="
          display:inline-flex;
          align-items:center;
          gap:8px;
          padding:${pillPadY}px ${pillPadX}px;
          border-radius:${pillRadius}px;
          background:${pillBg};
          border:1px solid #e5e7eb;
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
      <div>
        <div style="display:inline-flex;flex-direction:column;align-items:center;gap:8px;">
          <div style="
            width:140px;
            height:140px;
            border-radius:50%;
            border:${circleStrokeWidth}px solid ${circleBgColor};
            position:relative;
          ">
            <div style="
              position:absolute;
              inset:${circleStrokeWidth}px;
              border-radius:50%;
              background:conic-gradient(${circleFgColor} ${percent}%, ${circleBgColor} ${percent}%);
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
      <div>
        <div style="
          display:inline-flex;
          flex-direction:column;
          align-items:flex-start;
          gap:4px;
          padding:8px 12px;
          border-radius:${badgeRadius}px;
          background:${badgeBg};
          border:${badgeBorderWidth}px solid ${badgeBorderColor};
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

    // Fallback
    return `
    <span style="font-size:${size}px;color:${txt};">
      ${prefix}${baseTimeText}
    </span>
  `;
}

/* ========= Update preview ========= */

function updatePreview() {
    if (!htmlPreview) return;

    const template = templateInput.value;
    const bg = document.getElementById("background_color")?.value || "#ffffff";
    const txt = document.getElementById("text_color")?.value || "#000000";
    const size = parseInt(fontSizeInput?.value || "40", 10);
    const prefix = document.getElementById("message_prefix")?.value || "Temps restant : ";
    const dateValue = document.getElementById("target_date")?.value || "";
    const padding = parseInt(document.getElementById("padding")?.value || "0", 10);
    const icon = document.getElementById("icon")?.value || "";

    if (fontSizeValue) {
        fontSizeValue.textContent = size;
    }

    // Styles du conteneur preview
    htmlPreview.style.backgroundColor = bg;
    htmlPreview.style.color = txt;
    htmlPreview.style.padding = padding + "px";

    const innerHtml = renderTemplate(template, {
        bg,
        txt,
        size,
        prefix,
        dateValue,
        padding,
        icon,
    });

    htmlPreview.innerHTML = `
    <div style="display:inline-block;">
      ${innerHtml}
    </div>
  `;
}

/* ========= Listeners ========= */

if (form) {
    form.addEventListener("input", () => {
        updatePreview();
    });
}

// Mise à jour toutes les secondes pour l’aspect "compte à rebours"
setInterval(updatePreview, 1000);

/* ========= Initialisation ========= */

(function init() {
    const hasCountdown = form?.getAttribute("data-has-countdown") === "1";
    const currentTemplate = templateInput?.value || "";

    if (currentTemplate) {
        // Pré-sélectionner la carte correspondante
        templateCards.forEach(card => {
            if (card.getAttribute("data-template") === currentTemplate) {
                card.classList.add("uc-template-selected");
            }
        });
        updateTemplateSections(currentTemplate);

        // Si on a déjà créé un countdown (img_link présent), on montre le panneau design
        if (hasCountdown && designSection) {
            designSection.style.display = "block";
        }
    }

    updatePreview();
})();