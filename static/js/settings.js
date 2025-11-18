const templateButtons = document.querySelectorAll(".template-btn");
const templateContainer = document.getElementById("templateOptionsContainer");
const hiddenTemplate = document.getElementById("selectedTemplate");

let openedTemplate = null;

/* ==========================================
   OPTIONS PAR TEMPLATE (ce que tu as validé)
   ========================================== */
const TEMPLATE_OPTIONS = {
    classic: ["target_date", "colors", "text", "prefix"],
    minimal: ["target_date", "colors", "text"],
    blocks: ["target_date", "colors", "text", "labels", "blocks"],
    flip: ["target_date", "colors", "text", "labels", "blocks"],
    bubble: ["target_date", "colors", "text", "labels", "bubble"],
    banner: ["target_date", "colors", "text", "banner"],
    progress: ["target_date", "colors", "text", "progress"]
};

/* GLOBAL HTML PARTS */
const HTML_PARTS = {

    target_date: `
        <label>Date cible</label>
        <input type="datetime-local" name="target_date">
    `,

    colors: `
        <label>Couleur de fond</label>
        <input type="color" name="background_color" value="#ffffff">

        <label>Couleur du texte</label>
        <input type="color" name="text_color" value="#000000">
    `,

    text: `
        <label>Taille du texte</label>
        <input type="number" name="font_size" min="10" max="120" value="40">

        <label>Préfixe</label>
        <input type="text" name="message_prefix" placeholder="ex : Temps restant : ">
    `,

    labels: `
        <div class="switch">
            <input type="checkbox" name="show_labels" checked>
            <label>Afficher les labels (J/H/M/S)</label>
        </div>

        <div class="switch">
            <input type="checkbox" name="labels_custom">
            <label>Labels personnalisés</label>
        </div>

        <div class="labels-custom-area" style="display:none;">
            <label>Label jours</label><input type="text" name="label_days" placeholder="Jours">
            <label>Label heures</label><input type="text" name="label_hours" placeholder="Heures">
            <label>Label minutes</label><input type="text" name="label_minutes" placeholder="Minutes">
            <label>Label secondes</label><input type="text" name="label_seconds" placeholder="Secondes">
        </div>

        <script>
            document.addEventListener("input", e => {
                if (e.target.name === "labels_custom") {
                    document.querySelector(".labels-custom-area").style.display =
                        e.target.checked ? "block" : "none";
                }
            });
        </script>
    `,

    /* blocks + flip */
    blocks: `
        <label>Couleur fond blocs</label>
        <input type="color" name="block_bg_color" value="#ffffff">

        <label>Couleur bordure</label>
        <input type="color" name="block_border_color" value="#000000">

        <label>Épaisseur bordure</label>
        <input type="number" name="block_border_width" min="0" value="2">

        <label>Rayon arrondi</label>
        <input type="number" name="block_radius" min="0" value="12">

        <label>Padding horizontal bloc</label>
        <input type="number" name="block_padding_x" min="0" value="16">

        <label>Padding vertical bloc</label>
        <input type="number" name="block_padding_y" min="0" value="8">

        <label>Espacement blocs</label>
        <input type="number" name="blocks_gap" min="0" value="12">
    `,

    /* bubble */
    bubble: `
        <label>Couleur fond cercle</label>
        <input type="color" name="block_bg_color" value="#ffffff">

        <label>Couleur bordure</label>
        <input type="color" name="block_border_color" value="#000000">

        <label>Épaisseur bordure cercle</label>
        <input type="number" name="block_border_width" min="0" value="2">

        <label>Diamètre du cercle (padding vertical)</label>
        <input type="number" name="block_padding_y" min="0" value="20">
    `,

    banner: `
        <label>Couleur fond bannière</label>
        <input type="color" name="banner_bg_color" value="#222222">

        <label>Couleur texte</label>
        <input type="color" name="banner_text_color" value="#ffffff">
    `,

    progress: `
        <label>Couleur fond barre</label>
        <input type="color" name="progress_bg_color" value="#eeeeee">

        <label>Couleur progression</label>
        <input type="color" name="progress_fg_color" value="#00aaff">

        <label>Hauteur de la barre</label>
        <input type="number" name="progress_height" min="4" value="16">

        <label>Durée max progression (jours)</label>
        <input type="number" name="progress_max_days" min="1" value="30">
    `
};

/* ========================================
   GÉNÈRE LES OPTIONS POUR UN TEMPLATE
   ======================================== */
function buildOptions(templateName) {
    const opts = TEMPLATE_OPTIONS[templateName];
    let html = `<div class="options-panel"><h3>Options pour ${templateName}</h3>`;

    opts.forEach(opt => {
        html += HTML_PARTS[opt];
    });

    html += `</div>`;
    return html;
}

/* ========================================
   GESTION DU CLICK TEMPLATE
   ======================================== */
templateButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        const name = btn.dataset.template;

        if (openedTemplate === name) {
            // collapse
            openedTemplate = null;
            templateButtons.forEach(b => b.classList.remove("active"));
            templateContainer.innerHTML = "";
            hiddenTemplate.value = "";
            return;
        }

        // update UI
        openedTemplate = name;
        hiddenTemplate.value = name;

        templateButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        templateContainer.innerHTML = buildOptions(name);
    });
});