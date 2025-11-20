document.addEventListener("DOMContentLoaded", () => {
    const templateButtons = document.querySelectorAll(".template-btn");
    const hiddenTemplate = document.getElementById("selectedTemplate");
    const optionsBasic = document.getElementById("options-basic");
    const optionsCircular = document.getElementById("options-circular");
    const form = document.getElementById("countdownForm");
    const previewImage = document.getElementById("previewImage");

    function updateTemplateUI(template) {
        templateButtons.forEach(btn => {
            btn.classList.toggle("selected", btn.dataset.template === template);
        });

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

    function buildPreviewUrl() {
        if (!previewImage || !form) return;

        const formData = new FormData(form);
        const params = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
            if (key === "show_labels" || key === "circular_label_uppercase") {
                params.set(key, "1");
            } else if (value !== "") {
                params.set(key, value);
            }
        }

        const base = "/preview.svg";
        previewImage.src = base + "?" + params.toString() + "&t=" + Date.now();
    }

    // Initialisation du template sélectionné
    if (hiddenTemplate && hiddenTemplate.value) {
        updateTemplateUI(hiddenTemplate.value);
    } else {
        // Par défaut : circular
        hiddenTemplate.value = "circular";
        updateTemplateUI("circular");
    }

    // Click sur un template
    templateButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tpl = btn.dataset.template;
            if (hiddenTemplate.value === tpl) {
                // re-cliquer sur le même -> désélection possible si tu veux
                // pour l'instant on le garde sélectionné
                hiddenTemplate.value = tpl;
            } else {
                hiddenTemplate.value = tpl;
            }
            updateTemplateUI(tpl);
            buildPreviewUrl();
        });
    });

    // Mise à jour live
    if (form) {
        form.addEventListener("input", () => {
            buildPreviewUrl();
        });
    }

    // Premier rendu
    buildPreviewUrl();
});