document.addEventListener("DOMContentLoaded", () => {
    const templateButtons = document.querySelectorAll(".template-btn");
    const hiddenTemplate = document.getElementById("selectedTemplate");
    const optionsBasic = document.getElementById("options-basic");
    const optionsCircular = document.getElementById("options-circular");
    const form = document.getElementById("countdownForm");
    const gifPreview = document.getElementById("gifPreview");

    function updateTemplateUI(template) {
        // boutons
        templateButtons.forEach(btn => {
            btn.classList.toggle("selected", btn.dataset.template === template);
        });

        // options spécifiques
        if (template === "basic") {
            optionsBasic.classList.add("active");
            optionsCircular.classList.remove("active");
        } else if (template === "circular") {
            optionsBasic.classList.remove("active");
            optionsCircular.classList.add("active");
        } else {
            optionsBasic.classList.remove("active");
            optionsCircular.classList.remove("active");
        }
    }

    // init à partir de la config côté serveur
    if (hiddenTemplate && hiddenTemplate.value) {
        updateTemplateUI(hiddenTemplate.value);
    }

    // click sur template
    templateButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tpl = btn.dataset.template;

            // toggle : si on reclique sur le même -> on désélectionne
            if (hiddenTemplate.value === tpl) {
                hiddenTemplate.value = "";
                updateTemplateUI("");
            } else {
                hiddenTemplate.value = tpl;
                updateTemplateUI(tpl);
            }

            // si GIF déjà généré, rafraîchir l'aperçu
            if (gifPreview && gifPreview.dataset.base) {
                gifPreview.src = gifPreview.dataset.base + "?t=" + Date.now();
            }
        });
    });

    // rafraîchissement du GIF quand on change un champ
    if (form && gifPreview && gifPreview.dataset.base) {
        form.addEventListener("input", () => {
            const base = gifPreview.dataset.base;
            gifPreview.src = base + "?t=" + Date.now();
        });
    }
});
