(function () {
    const THEMES = [
        { key: "default", label: "Nuit Premium", xp: 0, tier: "base" },
        { key: "violet", label: "Violet doux", xp: 120, tier: "early" },
        { key: "emerald", label: "Émeraude légère", xp: 280, tier: "early" },
        { key: "sunset", label: "Sunset soft", xp: 500, tier: "early" },
        { key: "royal", label: "Cour Royale", xp: 900, tier: "transition" },
        { key: "kyoto", label: "Jade Kyoto", xp: 1300, tier: "transition" },
        { key: "coast", label: "Sunset Coast", xp: 1800, tier: "transition" },
        { key: "imperial", label: "Cour Impériale", xp: 2600, tier: "elite" },
        { key: "feudal", label: "Japon féodal", xp: 3400, tier: "elite" },
        { key: "sunlight", label: "Sunlight", xp: 4300, tier: "elite" }
    ];

    const ELITE_THEMES = new Set(["imperial", "feudal", "sunlight"]);

    function getStats() {
        try {
            return JSON.parse(localStorage.getItem("assistant_app_stats_v2") || "{}");
        } catch (_) {
            return {};
        }
    }

    function findNextUnlock(xp) {
        return THEMES.find(t => xp < t.xp) || null;
    }

    function previousThreshold(xp) {
        let prev = 0;
        for (const t of THEMES) {
            if (t.xp <= xp) prev = t.xp;
        }
        return prev;
    }

    function currentThemeKey(shell) {
        for (const t of THEMES) {
            if (shell.classList.contains(`theme-${t.key}`)) return t.key;
        }
        return "default";
    }

    function ensureDepthLayer(shell) {
        let layer = shell.querySelector(".theme-depth-layer");
        if (!layer) {
            layer = document.createElement("div");
            layer.className = "theme-depth-layer";
            layer.innerHTML = '<span class="d1"></span><span class="d2"></span><span class="d3"></span>';
            shell.appendChild(layer);
        }
        return layer;
    }

    function ensureXpCards() {
        const progressPanel = Array.from(document.querySelectorAll(".panel")).find(el => {
            const h2 = el.querySelector("h2");
            return h2 && h2.textContent.trim() === "Progression";
        });

        if (!progressPanel) return null;

        let wrapper = progressPanel.querySelector(".progression-extended");
        if (!wrapper) {
            wrapper = document.createElement("div");
            wrapper.className = "progression-extended";
            wrapper.innerHTML = `
                <div class="xp-next-card">
                    <strong>Prochain déblocage</strong>
                    <p id="xpNextText">Chargement...</p>
                    <div class="xp-mini-bar"><div id="xpMiniFill" class="xp-mini-fill"></div></div>
                </div>
                <div class="xp-help-card">
                    <strong>Comment gagner de l’XP</strong>
                    <p id="xpHelpText">Tu gagnes de l’XP en utilisant les modes de travail, en révisant, en lançant des quiz, des corrections et des sessions régulières.</p>
                    <div class="dev-pill">Progression liée à l’activité sur la plateforme</div>
                </div>
            `;
            progressPanel.appendChild(wrapper);
        }
        return wrapper;
    }

    function renderXpInfo() {
        const shell = document.getElementById("appShell");
        if (!shell) return;

        const stats = getStats();
        const xp = Number(stats.xp || 0);
        const next = findNextUnlock(xp);
        const nextText = document.getElementById("xpNextText");
        const miniFill = document.getElementById("xpMiniFill");

        if (nextText && miniFill) {
            if (!next) {
                nextText.innerHTML = `Tous les thèmes actuels sont débloqués.`;
                miniFill.style.width = "100%";
            } else {
                const prev = previousThreshold(xp);
                const span = Math.max(1, next.xp - prev);
                const progress = Math.max(0, Math.min(100, ((xp - prev) / span) * 100));
                const remain = Math.max(0, next.xp - xp);
                nextText.innerHTML = `Encore <span class="unlock-theme-name">${remain} XP</span> avant <span class="unlock-theme-name">${next.label}</span>.`;
                miniFill.style.width = `${progress}%`;
            }
        }

        const theme = currentThemeKey(shell);
        shell.classList.remove("elite-live");
        if (ELITE_THEMES.has(theme)) {
            shell.classList.add("elite-live");
        }
    }

    function attachEliteMotion() {
        const shell = document.getElementById("appShell");
        if (!shell) return;
        ensureDepthLayer(shell);

        let raf = null;
        let tx = 0;
        let ty = 0;

        window.addEventListener("mousemove", (e) => {
            const rect = shell.getBoundingClientRect();
            const cx = rect.left + rect.width / 2;
            const cy = rect.top + rect.height / 2;

            tx = (e.clientX - cx) / Math.max(1, rect.width / 2);
            ty = (e.clientY - cy) / Math.max(1, rect.height / 2);

            if (raf) return;
            raf = requestAnimationFrame(() => {
                shell.style.setProperty("--mx", tx.toFixed(3));
                shell.style.setProperty("--my", ty.toFixed(3));

                if (shell.classList.contains("elite-live")) {
                    shell.querySelectorAll(".glass").forEach((card, idx) => {
                        const factor = idx % 3 === 0 ? 4 : idx % 3 === 1 ? 3 : 2;
                        const rx = (-ty * factor).toFixed(2);
                        const ry = (tx * factor).toFixed(2);
                        card.style.transform = `perspective(1200px) rotateX(${rx}deg) rotateY(${ry}deg) translateZ(0)`;
                    });
                } else {
                    shell.querySelectorAll(".glass").forEach(card => {
                        card.style.transform = "";
                    });
                }

                raf = null;
            });
        });

        window.addEventListener("mouseleave", () => {
            shell.style.setProperty("--mx", 0);
            shell.style.setProperty("--my", 0);
            shell.querySelectorAll(".glass").forEach(card => {
                card.style.transform = "";
            });
        });
    }

    function boot() {
        ensureXpCards();
        renderXpInfo();
        attachEliteMotion();
        setInterval(renderXpInfo, 1000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
