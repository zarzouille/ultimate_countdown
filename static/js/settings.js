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
                // checkbox -> bool
                params.set(key, "1");
            } else if (value !== "") {
                params.set(key, value);
            }
        }

        const base = "/preview.svg";
        previewImage.src = base + "?" + params.toString() + "&t=" + Date.now();
    }

    // Init template UI
    if (hiddenTemplate && hiddenTemplate.value) {
        updateTemplateUI(hiddenTemplate.value);
    }

    // Click sur les templates
    templateButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tpl = btn.dataset.template;
            if (hiddenTemplate.value === tpl) {
                hiddenTemplate.value = "";
                updateTemplateUI("");
            } else {
                hiddenTemplate.value = tpl;
                updateTemplateUI(tpl);
            }
            buildPreviewUrl();
        });
    });

    // Live preview sur changement de champ
    if (form) {
        form.addEventListener("input", () => {
            buildPreviewUrl();
        });
    }

    // Premier rendu
    if (previewImage) {
        buildPreviewUrl();
    }
});