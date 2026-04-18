import copy
import random
import uuid

import generator


def _append_rule(text, rule_block):
    text = text.rstrip()
    return text + "\n\n" + rule_block.strip() + "\n"


def mutate_resume(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["resumer"] = _append_rule(
        mi["resumer"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Maximum 4 points utiles
- Pas de section redondante
- Pas de mini-fiche déguisée
- Coupe tout ce qui n’aide pas directement à réviser
"""
    )
    return mi


def mutate_explain(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["expliquer"] = _append_rule(
        mi["expliquer"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Fais ressortir le mécanisme central
- Évite la simple reformulation du cours
- Si le cours est court, ne gonfle pas artificiellement
"""
    )
    return mi


def mutate_correction(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["corriger"] = _append_rule(
        mi["corriger"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Distingue très nettement juste / faux / incomplet
- Donne une réponse améliorée plus dense
- Évite les commentaires vagues
"""
    )
    return mi


def mutate_exam(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["exam"] = _append_rule(
        mi["exam"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Évite les consignes trop longues
- Sujet crédible, compact et directement exploitable
- Réduis les répétitions entre attentes, notions et pièges
"""
    )
    return mi


def mutate_notions(mode_instructions):
    mi = copy.deepcopy(mode_instructions)
    mi["notions_centrales"] = _append_rule(
        mi["notions_centrales"],
        """
RÈGLES STRICTES SUPPLÉMENTAIRES :
- Classe les notions par ordre d’importance
- Maximum 5 notions
- Pas d’explication décorative
- Donne une ossature, pas un mini-cours
"""
    )
    return mi


def mutate_base_prompt(base_system_prompt):
    return _append_rule(
        base_system_prompt,
        """
RÈGLES D'AUTO-AMÉLIORATION :
- Récompense la densité utile
- Réduis la structure décorative
- Sur les questions piégeuses, pose une limite claire et recentre sur le cours
- En matière créative ou visuelle, privilégie la hiérarchisation des concepts plutôt que la paraphrase
"""
    )


MUTATORS = [
    ("resumer", "mode_resumer", mutate_resume, 3),
    ("expliquer", "mode_expliquer", mutate_explain, 4),
    ("corriger", "mode_corriger", mutate_correction, 2),
    ("exam", "mode_exam", mutate_exam, 4),
    ("notions_centrales", "mode_notions", mutate_notions, 5),
    ("base_system", "base_prompt", mutate_base_prompt, 1),
]


def generate_candidate():
    choices = MUTATORS
    weights = [item[3] for item in choices]
    mutation_label, target, mutator, _weight = random.choices(choices, weights=weights, k=1)[0]

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