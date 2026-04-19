import copy
import random
import uuid

import generator


def _append_rule(text, rule_block):
    text = text.rstrip()
    return text + "\n\n" + rule_block.strip() + "\n"


def _replace_section(text, old, new):
    if old in text:
        return text.replace(old, new)
    return _append_rule(text, new)


def _compress_text(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    seen = set()
    cleaned = []
    for line in lines:
        if line not in seen:
            cleaned.append(line)
            seen.add(line)
    return "\n".join(cleaned)


# ========================
# 🔴 MUTATIONS MODES
# ========================

def mutate_resume(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["resumer"] = _append_rule(
        mi["resumer"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Maximum 4 points
- Chaque point doit apporter une idée différente
- Supprime toute redondance
- Refuse toute dérive vers une fiche
"""
    )
    return mi


def mutate_explain(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["expliquer"] = _append_rule(
        mi["expliquer"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Identifie le mécanisme central avant d’expliquer
- Si le cours est flou, clarifie sans inventer
- Priorise compréhension > exhaustivité
"""
    )
    return mi


def mutate_correction(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["corriger"] = _append_rule(
        mi["corriger"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Sépare clairement juste / faux / incomplet
- Chaque critique doit être justifiée
- La réponse améliorée doit être supérieure, pas juste corrigée
"""
    )
    return mi


def mutate_exam(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["exam"] = _append_rule(
        mi["exam"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Teste la compréhension, pas la récitation
- Évite toute redondance entre sections
- Sujet compact et crédible
"""
    )
    return mi


def mutate_notions(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["notions_centrales"] = _append_rule(
        mi["notions_centrales"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Classe strictement du plus important au moins important
- Maximum 5 notions
- Refuse toute explication inutile
"""
    )
    return mi


def mutate_reviser(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["reviser"] = _append_rule(
        mi["reviser"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Favorise mémorisation rapide
- Supprime toute phrase inutile
- Structure uniquement si utile
"""
    )
    return mi


# ========================
# 🧠 MUTATIONS BASE SYSTEM
# ========================

def mutate_base_density(base_prompt):
    return _append_rule(
        base_prompt,
        """
RÈGLE CRITIQUE :
- Toute phrase doit apporter une information utile
- Supprime toute redondance implicite
"""
    )


def mutate_base_strategy(base_prompt):
    return _append_rule(
        base_prompt,
        """
AVANT DE RÉPONDRE :
- Identifie l’objectif réel de la demande
- Priorise ce qui aide à comprendre ou réussir
"""
    )


def mutate_base_safety(base_prompt):
    return _append_rule(
        base_prompt,
        """
SÉCURITÉ RENFORCÉE :
- Si une information est absente du cours, ne la complète pas
- Signale toute incertitude clairement
"""
    )


def mutate_base_cleanup(base_prompt):
    return _compress_text(base_prompt)


# ========================
# 🎲 MUTATEURS
# ========================

MUTATORS = [
    ("resumer", "mode_resumer", mutate_resume, 3),
    ("expliquer", "mode_expliquer", mutate_explain, 4),
    ("corriger", "mode_corriger", mutate_correction, 3),
    ("exam", "mode_exam", mutate_exam, 4),
    ("notions_centrales", "mode_notions", mutate_notions, 5),
    ("reviser", "mode_reviser", mutate_reviser, 3),

    ("base_density", "base_prompt", mutate_base_density, 2),
    ("base_strategy", "base_prompt", mutate_base_strategy, 3),
    ("base_safety", "base_prompt", mutate_base_safety, 2),
    ("base_cleanup", "base_prompt", mutate_base_cleanup, 1),
]


# ========================
# 🧬 GÉNÉRATION
# ========================

def generate_candidate():
    weights = [item[3] for item in MUTATORS]
    mutation_label, target, mutator, _ = random.choices(MUTATORS, weights=weights, k=1)[0]

    base_prompt = generator.BASE_SYSTEM_PROMPT
    mode_instructions = copy.deepcopy(generator.MODE_INSTRUCTIONS)

    if target == "base_prompt":
        new_base_prompt = mutator(base_prompt)
        new_mode_instructions = mode_instructions
    else:
        new_base_prompt = base_prompt
        new_mode_instructions = mutator(mode_instructions)

    return {
        "id": str(uuid.uuid4()),
        "type": "prompt_candidate",
        "status": "new",
        "mutation_label": mutation_label,
        "target": target,
        "base_system_prompt": new_base_prompt,
        "mode_instructions": new_mode_instructions,
        "notes": f"Mutation appliquée : {mutation_label}"
    }