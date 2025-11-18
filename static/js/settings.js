const templateButtons = document.querySelectorAll(".uc-template-btn");
const templateContainer = document.getElementById("templateOptionsContainer");
const hiddenTemplate = document.getElementById("selectedTemplate");
const designSection = document.getElementById("designSection");
const titleInput = document.getElementById("title");

let openedTemplate = null;

// --------- options par template ----------
const TEMPLATE_OPTIONS = {
    classic: ["target_date", "colors", "text"],
    minimal: ["target_date", "colors", "text"],
    blocks: ["target_date", "colors", "text", "labels", "blocks"],
    flip: ["target_date", "colors", "text", "labels", "blocks"],
    bubble: ["target_date", "colors", "text", "labels", "bubble"],
    banner: ["target_date", "colors", "text", "banner"],
    progress: ["target_date", "colors", "text", "progress"]
};

const HTML_PARTS = {
    target_date: `
    <div class="uc-field">
      <label>Date cible</label>
      <input type="datetime-local" name="target_date">
    </div>
  `,
    colors: `
    <div class="uc-field">
      <label>Couleur de fond</label>
      <input type="color" name="background_color" value="#ffffff">
    </div>
    <div class="uc-field">
      <label>Couleur du texte</label>
      <input type="color" name="text_color" value="#000000">
    </div>
  `,
    text: `
    <div class="uc-field">
      <label>Taille du texte</label>
      <input type="number" name="font_size" min="10" max="120" value="40">
    </div>
    <div class="uc-field">
      <label>Préfixe</label>
      <input type="text" name="message_prefix" placeholder="ex : Temps restant : ">
    </div>
  `,
    labels: `
    <div class="uc-field">
      <label>
        <input type="checkbox" name="show_labels" checked>
        Afficher les labels (J/H/M/S)
      </label>
    </div>
    <div class="uc-field">
      <label>
        <input type="checkbox" name="labels_custom">
        Utiliser des labels personnalisés
      </label>
    </div>
    <div class="uc-field labels-custom" style="display:none;">
      <label>Label jours</label>
      <input type="text" name="label_days" placeholder="Jours">
      <label>Label heures</label>
      <input type="text" name="label_hours" placeholder="Heures">
      <label>Label minutes</label>
      <input type="text" name="label_minutes" placeholder="Minutes">
      <label>Label secondes</label>
      <input type="text" name="label_seconds" placeholder="Secondes">
    </div>
  `,
    blocks: `
    <div class="uc-field">
      <label>Couleur fond blocs</label>
      <input type="color" name="block_bg_color" value="#ffffff">
    </div>
    <div class="uc-field">
      <label>Couleur bordure</label>
      <input type="color" name="block_border_color" value="#000000">
    </div>
    <div class="uc-field">
      <label>Épaisseur bordure</label>
      <input type="number" name="block_border_width" value="2" min="0">
    </div>
    <div class="uc-field">
      <label>Rayon arrondi</label>
      <input type="number" name="block_radius" value="12" min="0">
    </div>
    <div class="uc-field">
      <label>Padding horizontal bloc</label>
      <input type="number" name="block_padding_x" value="16" min="0">
    </div>
    <div class="uc-field">
      <label>Padding vertical bloc</label>
      <input type="number" name="block_padding_y" value="8" min="0">
    </div>
    <div class="uc-field">
      <label>Espacement blocs</label>
      <input type="number" name="blocks_gap" value="12" min="0">
    </div>
  `,
    bubble: `
    <div class="uc-field">
      <label>Couleur fond cercle</label>
      <input type="color" name="block_bg_color" value="#ffffff">
    </div>
    <div class="uc-field">
      <label>Couleur bordure</label>
      <input type="color" name="block_border_color" value="#000000">
    </div>
    <div class="uc-field">
      <label>Épaisseur bordure cercle</label>
      <input type="number" name="block_border_width" value="2" min="0">
    </div>
    <div class="uc-field">
      <label>Diamètre du cercle (padding vertical)</label>
      <input type="number" name="block_padding_y" value="20" min="0">
    </div>
  `,
    banner: `
    <div class="uc-field">
      <label>Couleur fond bannière</label>
      <input type="color" name="banner_bg_color" value="#222222">
    </div>
    <div class="uc-field">
      <label>Couleur texte</label>
      <input type="color" name="banner_text_color" value="#ffffff">
    </div>
  `,
    progress: `
    <div class="uc-field">
      <label>Couleur fond barre</label>
      <input type="color" name="progress_bg_color" value="#eeeeee">
    </div>
    <div class="uc-field">
      <label>Couleur progression</label>
      <input type="color" name="progress_fg_color" value="#00aaff">
    </div>
    <div class="uc-field">
      <label>Hauteur de la barre</label>
      <input type="number" name="progress_height" value="16" min="4">
    </div>
    <div class="uc-field">
      <label>Durée max progression (jours)</label>
      <input type="number" name="progress_max_days" value="30" min="1">
    </div>
  `
};

function buildOptions(templateName) {
    const parts = TEMPLATE_OPTIONS[templateName] || [];
    let html = "";
    parts.forEach(key => {
        html += HTML_PARTS[key] || "";
    });
    return html;
}

// Clic sur un template = toggle
templateButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        const tpl = btn.dataset.template;

        if (openedTemplate === tpl) {
            // fermer
            openedTemplate = null;
            hiddenTemplate.value = "";
            templateButtons.forEach(b => b.classList.remove("uc-selected"));
            templateContainer.innerHTML = "";
            if (designSection) designSection.style.display = "none";
            return;
        }

        // ouvrir ce template
        openedTemplate = tpl;
        hiddenTemplate.value = tpl;

        templateButtons.forEach(b => b.classList.remove("uc-selected"));
        btn.classList.add("uc-selected");

        templateContainer.innerHTML = buildOptions(tpl);
        if (designSection) designSection.style.display = "block";

        // gestion labels_custom (si présent)
        const labelsCheckbox = templateContainer.querySelector('input[name="labels_custom"]');
        const labelsCustomBlock = templateContainer.querySelector(".labels-custom");
        if (labelsCheckbox && labelsCustomBlock) {
            labelsCheckbox.addEventListener("change", () => {
                labelsCustomBlock.style.display = labelsCheckbox.checked ? "block" : "none";
            });
        }
    });
});

// titre de l’onglet mis à jour en live
if (titleInput) {
    const updateTitle = () => {
        const t = titleInput.value.trim();
        document.title = t || "Ultimate Countdown";
    };
    titleInput.addEventListener("input", updateTitle);
    updateTitle();
}
