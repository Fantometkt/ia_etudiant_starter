MUTATION_RULES = [

    # ========================
    # 🔴 COMPRESSION / DENSITÉ
    # ========================

    {
        "id": "compress_summary",
        "target": "prompts.resumer",
        "category": "compression",
        "operation": "strengthen",
        "focus": ["brevity", "anti_fluff"],
        "description": "Réduire encore la longueur et supprimer toute redondance.",
        "intensity": "medium"
    },
    {
        "id": "compress_exam",
        "target": "prompts.exam",
        "category": "compression",
        "operation": "strengthen",
        "focus": ["brevity", "no_redundancy"],
        "description": "Réduire les sections inutiles et compacter les attentes.",
        "intensity": "medium"
    },
    {
        "id": "compress_explain",
        "target": "prompts.expliquer",
        "category": "compression",
        "operation": "strengthen",
        "focus": ["anti_paraphrase"],
        "description": "Supprimer toute reformulation inutile.",
        "intensity": "medium"
    },

    # ========================
    # 🧠 MÉCANISMES / PROFONDEUR
    # ========================

    {
        "id": "boost_mechanisms_explain",
        "target": "prompts.expliquer",
        "category": "depth",
        "operation": "strengthen",
        "focus": ["mechanism", "causality"],
        "description": "Renforcer l’explication des mécanismes et du pourquoi.",
        "intensity": "high"
    },
    {
        "id": "boost_logic_correction",
        "target": "prompts.corriger",
        "category": "depth",
        "operation": "strengthen",
        "focus": ["reasoning", "justification"],
        "description": "Renforcer l’explication du raisonnement correct.",
        "intensity": "high"
    },

    # ========================
    # 🏗️ HIÉRARCHISATION
    # ========================

    {
        "id": "boost_hierarchy_notions",
        "target": "prompts.notions_centrales",
        "category": "hierarchy",
        "operation": "strengthen",
        "focus": ["essential_vs_secondary"],
        "description": "Renforcer la distinction essentiel / important / secondaire.",
        "intensity": "high"
    },
    {
        "id": "limit_notions_count",
        "target": "prompts.notions_centrales",
        "category": "constraint",
        "operation": "restrict",
        "focus": ["max_items"],
        "description": "Limiter strictement à 5 notions maximum.",
        "intensity": "medium"
    },

    # ========================
    # ⚖️ ALIGNEMENT MODE
    # ========================

    {
        "id": "mode_alignment_summary",
        "target": "prompts.resumer",
        "category": "alignment",
        "operation": "strengthen",
        "focus": ["mode_purity"],
        "description": "Éviter toute dérive vers une fiche ou explication.",
        "intensity": "high"
    },
    {
        "id": "mode_alignment_exam",
        "target": "prompts.exam",
        "category": "alignment",
        "operation": "strengthen",
        "focus": ["exam_realism"],
        "description": "Renforcer la crédibilité académique réelle.",
        "intensity": "high"
    },

    # ========================
    # 🚫 ANTI-FLUFF / ANTI-REDONDANCE
    # ========================

    {
        "id": "anti_fluff_global",
        "target": "base_system",
        "category": "cleanup",
        "operation": "strengthen",
        "focus": ["remove_filler"],
        "description": "Supprimer toute phrase inutile ou décorative.",
        "intensity": "high"
    },
    {
        "id": "remove_redundancy_base",
        "target": "base_system",
        "category": "cleanup",
        "operation": "compress",
        "focus": ["deduplicate_rules"],
        "description": "Supprimer les règles redondantes ou équivalentes.",
        "intensity": "medium"
    },

    # ========================
    # 🛡️ ANTI-HALLUCINATION
    # ========================

    {
        "id": "anti_hallucination_guard",
        "target": "base_system",
        "category": "safety",
        "operation": "strengthen",
        "focus": ["uncertainty_handling"],
        "description": "Renforcer la gestion des informations absentes du cours.",
        "intensity": "high"
    },
    {
        "id": "strict_source_dependency",
        "target": "base_system",
        "category": "safety",
        "operation": "enforce",
        "focus": ["course_dependency"],
        "description": "Renforcer la dépendance stricte au cours fourni.",
        "intensity": "high"
    },

    # ========================
    # 🧱 STRUCTURE / FORMAT
    # ========================

    {
        "id": "harden_correction_format",
        "target": "prompts.corriger",
        "category": "structure",
        "operation": "enforce",
        "focus": ["format_strictness"],
        "description": "Rendre le format de correction strict et non contournable.",
        "intensity": "high"
    },
    {
        "id": "soften_structure_explain",
        "target": "prompts.expliquer",
        "category": "structure",
        "operation": "relax",
        "focus": ["avoid_rigidity"],
        "description": "Réduire la rigidité de la structure si inutile.",
        "intensity": "medium"
    },

    # ========================
    # 🎯 UTILITÉ / PERFORMANCE
    # ========================

    {
        "id": "boost_revision_efficiency",
        "target": "prompts.reviser",
        "category": "performance",
        "operation": "strengthen",
        "focus": ["memorability", "clarity"],
        "description": "Renforcer la mémorisation et l’utilité directe.",
        "intensity": "high"
    },
    {
        "id": "boost_exam_focus",
        "target": "prompts.exam",
        "category": "performance",
        "operation": "strengthen",
        "focus": ["exam_success"],
        "description": "Renforcer l’orientation réussite examen.",
        "intensity": "high"
    },

    # ========================
    # 🧪 DIVERSIFICATION
    # ========================

    {
        "id": "inject_variation_structure",
        "target": "global",
        "category": "exploration",
        "operation": "modify",
        "focus": ["structure_variation"],
        "description": "Modifier légèrement la structure pour éviter convergence.",
        "intensity": "low"
    },
    {
        "id": "inject_variation_tone",
        "target": "global",
        "category": "exploration",
        "operation": "modify",
        "focus": ["tone_adjustment"],
        "description": "Varier légèrement le ton sans casser la rigueur.",
        "intensity": "low"
    }

]