document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("countdownForm");
    const previewImg = document.getElementById("previewImage");
    const templateBtns = Array.from(document.querySelectorAll(".template-btn"));
    const hiddenTemplate = document.getElementById("selectedTemplate");

    const optionsBasic = document.getElementById("options-basic");
    const optionsCircular = document.getElementById("options-circular");

    const dateInput = document.getElementById("target_date_only");
    const timeInput = document.getElementById("target_time_only");

    function setTemplate(tpl) {
        hiddenTemplate.value = tpl;

        templateBtns.forEach((btn) => {
            const btpl = btn.getAttribute("data-template");
            if (btpl === tpl) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        if (tpl === "basic") {
            optionsBasic.style.display = "block";
            optionsCircular.style.display = "none";
        } else if (tpl === "circular") {
            optionsBasic.style.display = "none";
            optionsCircular.style.display = "block";
        }
    }

    // Init template selection
    let initialTpl = hiddenTemplate.value || "circular";
    if (!["basic", "circular"].includes(initialTpl)) {
        initialTpl = "circular";
    }
    setTemplate(initialTpl);

    templateBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const tpl = btn.getAttribute("data-template");
            setTemplate(tpl);
            updatePreview();
        });
    });

    function buildPreviewURL() {
        const params = new URLSearchParams();

        // Template
        const tpl = hiddenTemplate.value || "circular";
        params.set("template", tpl);

        // Commun
        const bg = document.getElementById("background_color").value;
        const tc = document.getElementById("text_color").value;
        const fs = document.getElementById("font_size").value;
        const mp = document.getElementById("message_prefix").value;

        params.set("background_color", bg);
        params.set("text_color", tc);
        params.set("font_size", fs);
        params.set("message_prefix", mp);

        const showLabels = form.querySelector("input[name='show_labels']").checked;
        params.set("show_labels", showLabels ? "1" : "0");

        // Gras
        params.set(
            "font_bold",
            form.querySelector("input[name='font_bold']").checked ? "1" : "0"
        );
        params.set(
            "label_bold",
            form.querySelector("input[name='label_bold']").checked ? "1" : "0"
        );
        params.set(
            "prefix_bold",
            form.querySelector("input[name='prefix_bold']").checked ? "1" : "0"
        );

        // DATE + HEURE combinées → target_date ISO
        const dateVal = dateInput.value;
        const timeVal = timeInput.value;
        if (dateVal) {
            let iso = dateVal;
            if (timeVal) {
                iso += "T" + timeVal;
            } else {
                iso += "T00:00";
            }
            params.set("target_date", iso);
        }

        // CIRCULAR
        params.set(
            "circular_base_color",
            document.getElementById("circular_base_color").value
        );
        params.set(
            "circular_progress_color",
            document.getElementById("circular_progress_color").value
        );
        params.set(
            "circular_thickness",
            document.getElementById("circular_thickness").value
        );
        params.set(
            "circular_label_uppercase",
            form.querySelector("input[name='circular_label_uppercase']").checked
                ? "1"
                : "0"
        );
        params.set(
            "circular_label_size",
            document.getElementById("circular_label_size").value
        );
        params.set(
            "circular_label_color",
            document.getElementById("circular_label_color").value
        );
        params.set(
            "circular_spacing",
            document.getElementById("circular_spacing").value
        );
        params.set(
            "circular_inner_ratio",
            document.getElementById("circular_inner_ratio").value
        );

        // BASIC
        params.set(
            "basic_label_color",
            document.getElementById("basic_label_color").value
        );
        params.set(
            "basic_label_size",
            document.getElementById("basic_label_size").value
        );
        params.set("basic_gap", document.getElementById("basic_gap").value);

        // Cache-buster
        params.set("t", Date.now().toString());

        return "/preview.svg?" + params.toString();
    }

    function updatePreview() {
        if (!previewImg) return;
        previewImg.src = buildPreviewURL();
    }

    // Mise à jour live : changement sur n’importe quel champ du formulaire
    form.addEventListener("input", () => {
        updatePreview();
    });

    // Première mise à jour au chargement
    updatePreview();
});