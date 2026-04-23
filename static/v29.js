(function () {
    const THEMES = [
        { key: "default", label: "Nuit Premium", xp: 0, tier: "base" },
        { key: "violet", label: "Violet doux", xp: 120, tier: "premium" },
        { key: "emerald", label: "Émeraude légère", xp: 280, tier: "premium" },
        { key: "sunset", label: "Sunset soft", xp: 500, tier: "premium" },
        { key: "royal", label: "Cour Royale", xp: 900, tier: "prestige" },
        { key: "kyoto", label: "Jade Kyoto", xp: 1300, tier: "prestige" },
        { key: "coast", label: "Sunset Coast", xp: 1800, tier: "prestige" },
        { key: "imperial", label: "Cour Impériale", xp: 2600, tier: "elite" },
        { key: "feudal", label: "Japon féodal", xp: 3400, tier: "elite" },
        { key: "sunlight", label: "Sunlight", xp: 4300, tier: "elite" }
    ];

    const ELITE_THEMES = new Set(["imperial", "feudal", "sunlight"]);

    function getShell() {
        return document.getElementById("appShell");
    }

    function getStats() {
        try {
            return JSON.parse(localStorage.getItem("assistant_app_stats_v2") || "{}");
        } catch (_) {
            return {};
        }
    }

    function saveStats(stats) {
        localStorage.setItem("assistant_app_stats_v2", JSON.stringify(stats));
    }

    function findTheme(key) {
        return THEMES.find(t => t.key === key);
    }

    function isUnlocked(themeKey, xp, devMode) {
        if (devMode) return true;
        const theme = findTheme(themeKey);
        if (!theme) return false;
        return xp >= theme.xp;
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

    function ensureEliteButtons() {
        const groups = Array.from(document.querySelectorAll(".theme-group"));
        const eliteGroup = groups.find(group => {
            const title = group.querySelector(".theme-group-title");
            return title && title.textContent.trim() === "Élite";
        });

        if (!eliteGroup) return;

        const grid = eliteGroup.querySelector(".theme-grid");
        if (!grid) return;

        const wanted = [
            ["imperial", "Cour Impériale"],
            ["feudal", "Japon féodal"],
            ["sunlight", "Sunlight"]
        ];

        for (const [key, label] of wanted) {
            if (!grid.querySelector(`[data-theme="${key}"]`)) {
                const btn = document.createElement("button");
                btn.className = "theme-tile locked-theme elite-theme";
                btn.dataset.theme = key;
                btn.textContent = label;
                grid.appendChild(btn);
            }
        }
    }

    function syncThemeButtons() {
        const stats = getStats();
        const xp = Number(stats.xp || 0);
        const devMode = !!stats.devMode;
        const currentTheme = stats.theme || "default";

        document.querySelectorAll(".theme-tile").forEach(btn => {
            const key = btn.dataset.theme;
            const unlocked = isUnlocked(key, xp, devMode);

            btn.classList.remove("active-theme", "locked-theme");

            if (!unlocked) {
                btn.classList.add("locked-theme");
            }

            if (currentTheme === key && unlocked) {
                btn.classList.add("active-theme");
            }

            if (!btn.dataset.boundTheme) {
                btn.addEventListener("click", () => {
                    const fresh = getStats();
                    if (!isUnlocked(key, Number(fresh.xp || 0), !!fresh.devMode)) return;
                    applyTheme(key);
                });
                btn.dataset.boundTheme = "1";
            }
        });
    }

    function ensureXpCards() {
        const progressPanel = Array.from(document.querySelectorAll(".panel")).find(el => {
            const h2 = el.querySelector("h2");
            return h2 && h2.textContent.trim() === "Progression";
        });

        if (!progressPanel) return;

        let wrapper = progressPanel.querySelector(".progression-extended");
        if (!wrapper) {
            wrapper = document.createElement("div");
            wrapper.className = "progression-extended";
            wrapper.innerHTML = `
                <div class="xp-next-card">
                    <strong>Prochain déblocage</strong>
                    <p id="xpNextText">Chargement...</p>
                    <div class="xp-mini-bar">
                        <div id="xpMiniFill" class="xp-mini-fill"></div>
                    </div>
                </div>
                <div class="xp-help-card">
                    <strong>Comment gagner de l’XP</strong>
                    <p id="xpHelpText">Tu gagnes de l’XP en envoyant des demandes, en utilisant les quiz, les corrections, les fiches de révision et les modes avancés.</p>
                    <div class="dev-pill">Progression liée à ton activité</div>
                </div>
            `;
            progressPanel.appendChild(wrapper);
        }
    }

    function renderXpInfo() {
        const shell = getShell();
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

        const theme = stats.theme || currentThemeKey(shell);
        shell.classList.remove("elite-live");
        if (ELITE_THEMES.has(theme)) {
            shell.classList.add("elite-live");
        }
    }

    function ensureDepthLayer(shell) {
        let layer = shell.querySelector(".theme-depth-layer");
        if (!layer) {
            layer = document.createElement("div");
            layer.className = "theme-depth-layer";
            layer.innerHTML = '<span class="d1"></span><span class="d2"></span><span class="d3"></span>';
            shell.appendChild(layer);
        }
    }

    function applyTheme(themeKey) {
        const shell = getShell();
        if (!shell) return;

        const stats = getStats();
        stats.theme = themeKey;
        saveStats(stats);

        const currentClasses = Array.from(shell.classList).filter(c => !c.startsWith("theme-") && c !== "elite-live");
        shell.className = [...currentClasses, `theme-${themeKey}`].join(" ");

        if (ELITE_THEMES.has(themeKey)) {
            shell.classList.add("elite-live");
        }

        const themeBadge = document.getElementById("themeBadge");
        if (themeBadge) {
            const theme = findTheme(themeKey);
            themeBadge.textContent = theme ? theme.label : "Nuit Premium";
        }

        syncThemeButtons();
        renderXpInfo();
    }

    function attachEliteMotion() {
        const shell = getShell();
        if (!shell) return;

        ensureDepthLayer(shell);

        const targetSelectors = [".hero-card", ".brand-card", ".rewards-card", ".memory-card"];
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
                    const cards = shell.querySelectorAll(targetSelectors.join(","));
                    cards.forEach((card, idx) => {
                        const factor = idx === 0 ? 2.8 : idx === 1 ? 2.2 : 1.6;
                        const rx = (-ty * factor).toFixed(2);
                        const ry = (tx * factor).toFixed(2);
                        card.style.transform = `perspective(1200px) rotateX(${rx}deg) rotateY(${ry}deg) translateZ(0)`;
                    });
                }

                raf = null;
            });
        });

        window.addEventListener("mouseleave", () => {
            shell.style.setProperty("--mx", 0);
            shell.style.setProperty("--my", 0);
            shell.querySelectorAll(".hero-card, .brand-card, .rewards-card, .memory-card").forEach(card => {
                card.style.transform = "";
            });
        });
    }

    function hijackThemeCycleButton() {
        const oldBtn = document.getElementById("themeBtn");
        if (!oldBtn || oldBtn.dataset.v29Hijacked) return;

        const newBtn = oldBtn.cloneNode(true);
        newBtn.dataset.v29Hijacked = "1";
        oldBtn.parentNode.replaceChild(newBtn, oldBtn);

        newBtn.addEventListener("click", () => {
            const stats = getStats();
            const xp = Number(stats.xp || 0);
            const devMode = !!stats.devMode;
            const unlocked = THEMES.filter(t => isUnlocked(t.key, xp, devMode)).map(t => t.key);
            const current = stats.theme || "default";
            const idx = unlocked.indexOf(current);
            const next = unlocked[(idx + 1) % unlocked.length] || "default";
            applyTheme(next);
        });
    }

    function boot() {
        const shell = getShell();
        if (!shell) return;

        ensureEliteButtons();
        ensureXpCards();
        ensureDepthLayer(shell);
        syncThemeButtons();
        renderXpInfo();
        attachEliteMotion();
        hijackThemeCycleButton();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
