MUTATION_RULES = [
    {
        "id": "tighten_summary",
        "target": "prompts.resumer",
        "description": "Réduire la structure du mode résumé et renforcer la condensation.",
        "intensity": "low"
    },
    {
        "id": "tighten_exam",
        "target": "prompts.exam",
        "description": "Réduire la longueur du mode examen et renforcer la crédibilité académique.",
        "intensity": "low"
    },
    {
        "id": "tighten_explain",
        "target": "prompts.expliquer",
        "description": "Réduire la paraphrase et renforcer l’explication des mécanismes.",
        "intensity": "medium"
    },
    {
        "id": "tighten_correction",
        "target": "prompts.corriger",
        "description": "Renforcer l’exigence analytique et la distinction juste/faux/incomplet.",
        "intensity": "medium"
    },
    {
        "id": "anti_hallucination_guard",
        "target": "base_system",
        "description": "Renforcer la retenue si le cours est insuffisant.",
        "intensity": "medium"
    },
]