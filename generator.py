from utils import *
from prompts import *
from memory_manager import build_student_memory_context
from course_analyzer import analyze_course, format_course_analysis
from judge import judge
from llm import call_ollama
from learning_eval import build_eval_summary
from progress_engine import build_learning_plan, recommend_mode
from safety import output_quality_flags


MODE_TEMPS = {
    "expliquer": [0.10, 0.18],
    "resumer": [0.06, 0.12],
    "a_retenir": [0.05, 0.10],
    "quiz": [0.12, 0.20],
    "corriger": [0.08, 0.16],
    "exam": [0.10, 0.18],
    "notions_centrales": [0.08, 0.14],
    "memoire": [0.14, 0.22],
    "socratic": [0.10, 0.18],
    "diagnostic": [0.06, 0.12],
    "progression": [0.12, 0.20],
    "reviser": [0.08, 0.16],
}


# =========================================================
# DIAGNOSTIC
# =========================================================

def infer_real_need(message, mode, previous_response="", learning_goal="comprendre"):
    text = clean(message).lower()

    if mode == "diagnostic":
        return "diagnostiquer_le_niveau_reel"
    if mode == "progression":
        return "construire_une_progression"
    if mode == "socratic":
        return "guider_sans_remplacer"
    if mode == "corriger" or clean(previous_response):
        return "corriger_pour_faire_progresser"
    if mode == "exam":
        return "preparer_une_evaluation"
    if mode == "quiz":
        return "entrainer_la_comprehension"
    if mode == "a_retenir":
        return "fixer_le_noyau_minimal"
    if mode == "reviser":
        return "rendre_le_cours_revisable"
    if mode == "notions_centrales":
        return "extraire_l_ossature_du_cours"
    if "pas compris" in text or "perdu" in text or "bloqué" in text:
        return "debloquer_une_incomprehension"
    if "différence" in text or "confond" in text or "confusion" in text:
        return "clarifier_une_confusion"
    if mode == "resumer":
        return "synthetiser_l_essentiel"

    return learning_goal or "comprendre_reellement"


def infer_difficulty(cours, message, niveau):
    score = 0

    if len(clean(cours)) > 2500:
        score += 2
    elif len(clean(cours)) > 800:
        score += 1

    msg = clean(message).lower()
    hard_markers = [
        "analyse",
        "mécanisme",
        "logique",
        "implication",
        "comparer",
        "démontrer",
        "problématiser",
        "enjeu"
    ]

    if any(m in msg for m in hard_markers):
        score += 1

    niv = clean(niveau).lower()
    if any(x in niv for x in ["l3", "m1", "m2", "master"]):
        score += 1

    if score >= 3:
        return "difficile"
    if score >= 1:
        return "intermediaire"
    return "simple"

def compute_enrichment_level(cours, mode):
    wc = word_count(cours)

    if mode in {"resumer", "a_retenir"}:
        return "minimal"

    if not clean(cours):
        return "general"

    if wc < 35:
        return "high"

    if wc < 120:
        return "medium"

    return "low"


def build_enrichment_block(cours, mode):
    level = compute_enrichment_level(cours, mode)

    if level == "general":
        return """
ENRICHISSEMENT
- Aucun cours réel n’est fourni.
- Tu peux utiliser des connaissances générales fiables.
- Reste pédagogique, clair et adapté au niveau.
- Ne prétends pas t’appuyer sur un cours absent.
""".strip()

    if level == "high":
        return """
ENRICHISSEMENT CONTRÔLÉ
- Le cours est très court.
- Tu dois partir strictement de l’idée donnée.
- Tu peux enrichir pour permettre une vraie compréhension.
- Ajoute seulement des compléments utiles : mécanisme, exemple, notion proche, lien logique.
- Ne présente jamais ces compléments comme explicitement présents dans le cours.
- Signale naturellement l’apport avec : "Pour mieux comprendre", "En complément utile", ou "Dans la logique du cours".
""".strip()

    if level == "medium":
        return """
ENRICHISSEMENT CONTRÔLÉ
- Le cours est partiel.
- Tu peux compléter modérément pour aider la progression.
- Priorité : expliquer la logique et combler les implicites utiles.
- Évite les développements trop longs.
- Distingue clairement le cours et l’apport pédagogique.
""".strip()

    if level == "minimal":
        return """
ENRICHISSEMENT LIMITÉ
- Le mode demandé exige de condenser.
- N’ajoute presque aucun contenu externe.
- Garde seulement ce qui aide directement à retenir.
""".strip()

    return """
ENRICHISSEMENT LIMITÉ
- Le cours est assez développé.
- Priorité : structurer, hiérarchiser, clarifier.
- N’ajoute un complément que s’il débloque vraiment la compréhension.
""".strip()


def build_pedagogical_diagnostic_block(
    message,
    cours,
    niveau,
    mode,
    previous_response,
    learning_goal,
    help_level,
    student_eval=None
):
    need = infer_real_need(message, mode, previous_response, learning_goal)
    difficulty = infer_difficulty(cours, message, niveau)

    risks = []

    if not clean(cours):
        risks.append("absence_de_cours")
    if clean(previous_response):
        risks.append("réponse_étudiante_à_exploiter")
    if mode == "expliquer":
        risks.append("paraphrase_sans_mécanisme")
    if mode == "resumer":
        risks.append("résumé_trop_long_ou_trop_descriptif")
    if mode == "corriger":
        risks.append("correction_vague_ou_peu_formatrice")
    if mode == "exam":
        risks.append("sujet_trop_générique")
    if mode == "socratic":
        risks.append("donner_la_réponse_trop_vite")
    if "invente" in clean(message).lower() or "même si" in clean(message).lower():
        risks.append("demande_d_invention_ou_dépassement_du_cours")

    eval_block = ""
    if student_eval:
        eval_block = f"""
ÉVALUATION DE LA RÉPONSE ÉTUDIANTE
{build_eval_summary(student_eval)}
"""

    return f"""
DIAGNOSTIC PÉDAGOGIQUE INTERNE
- Besoin réel : {need}
- Difficulté estimée : {difficulty}
- Niveau d’aide : {help_level}

RISQUES À SURVEILLER
{chr(10).join("- " + r for r in risks) if risks else "- aucun risque majeur"}

{eval_block}

DÉCISION
- Prioriser ce qui fait progresser réellement l’étudiant.
- Ne pas faire illusion avec une réponse jolie mais peu utile.
- Expliciter le mécanisme si c’est central.
- Refuser clairement d’inventer ce que le cours ne donne pas.
- Si une erreur étudiante est disponible, l’utiliser pour personnaliser l’aide.
""".strip()


# =========================================================
# BLOCKS
# =========================================================

def build_goal_block(learning_goal):
    goal = clean(learning_goal).lower()

    if "retenir" in goal or "mémoris" in goal:
        return """
OBJECTIF PÉDAGOGIQUE
- Priorité : mémorisation.
- La réponse doit être facilement révisable.
- Formulations courtes, nettes, fixables.
""".strip()

    if "examen" in goal or "partiel" in goal or "bac" in goal:
        return """
OBJECTIF PÉDAGOGIQUE
- Priorité : réussite en évaluation.
- Mettre en avant les attentes du correcteur, les pièges et la méthode.
""".strip()

    if "autonomie" in goal or "seul" in goal:
        return """
OBJECTIF PÉDAGOGIQUE
- Priorité : autonomie.
- Guider sans remplacer.
- Faire réfléchir l’étudiant au lieu de produire à sa place.
""".strip()

    return """
OBJECTIF PÉDAGOGIQUE
- Priorité : compréhension réelle.
- Faire apparaître la logique, le mécanisme et les confusions possibles.
""".strip()


def build_help_level_block(help_level):
    if help_level == "fort":
        return """
NIVEAU D’AIDE
- Guidage fort.
- Explications plus progressives.
- Sécuriser les blocages.
- Découper les raisonnements difficiles.
""".strip()

    if help_level == "leger":
        return """
NIVEAU D’AIDE
- Guidage léger.
- Réponse compacte.
- Aller directement au plus utile.
""".strip()

    return """
NIVEAU D’AIDE
- Équilibre entre clarté, densité et autonomie.
""".strip()


def build_previous_response_block(previous_response):
    previous_response = clean(previous_response)

    if not previous_response:
        return "Aucune réponse étudiante fournie."

    return f"""
RÉPONSE ÉTUDIANTE
{previous_response}

UTILISATION ATTENDUE
- Repérer ce qui est juste.
- Repérer ce qui est faux.
- Repérer ce qui est incomplet.
- Expliquer pourquoi.
- Transformer l’erreur en progression.
""".strip()


def build_learning_plan_block(mem, student_id):
    student = safe_dict(mem.get("students")).get(clean(student_id))

    if not student:
        return """
PLAN D’APPRENTISSAGE
- Aucun profil suffisamment avancé.
- Commencer par diagnostic court.
""".strip()

    plan = build_learning_plan(student, horizon="court")
    recommended = recommend_mode(student)

    return f"""
PLAN D’APPRENTISSAGE PERSONNALISÉ
- Objectif : {plan.get("goal")}
- Mode recommandé par le système : {recommended}

Étapes conseillées :
{chr(10).join("- " + s for s in plan.get("steps", []))}
""".strip()


# =========================================================
# PROMPT
# =========================================================

def build_prompt(
    mem,
    message,
    niveau,
    matiere,
    cours,
    student_id,
    learning_style,
    weaknesses,
    previous_response,
    mode,
    learning_goal="comprendre",
    help_level="equilibre",
    student_eval=None
):
    student_context = build_student_memory_context(mem, student_id)
    course_analysis = analyze_course(cours, niveau, matiere)
    analysis_text = format_course_analysis(course_analysis)
    enrichment_block = build_enrichment_block(cours, mode)

    return f"""
CONTEXTE GÉNÉRAL
- Niveau : {niveau}
- Matière : {matiere}
- Mode demandé : {mode}

{build_goal_block(learning_goal)}

{build_help_level_block(help_level)}

MÉMOIRE ET PROFIL ÉTUDIANT
{student_context}

PLAN PERSONNALISÉ
{build_learning_plan_block(mem, student_id)}

STYLE D’APPRENTISSAGE INDIQUÉ
{clean(learning_style) or "Non précisé."}

FAIBLESSES OU LACUNES DÉCLARÉES
{clean(weaknesses) or "Non précisées."}

ANALYSE PÉDAGOGIQUE DU COURS
{analysis_text}

STRATÉGIE D’ENRICHISSEMENT
{enrichment_block}

{build_pedagogical_diagnostic_block(
    message=message,
    cours=cours,
    niveau=niveau,
    mode=mode,
    previous_response=previous_response,
    learning_goal=learning_goal,
    help_level=help_level,
    student_eval=student_eval
)}

RÈGLES DE PRODUCTION
- Base principale = le cours fourni.
- Ne jamais inventer une information absente du cours comme si elle était certaine.
- Si le cours est insuffisant, le dire uniquement si cela bloque la réponse.
- Si le cours est court mais exploitable, enrichir intelligemment pour faire progresser.
- Toujours distinguer ce qui vient du cours et ce qui est un complément pédagogique utile.
- La réponse doit faire progresser l’étudiant.
- Ne pas confondre longueur et profondeur.
- Hiérarchiser essentiel / important / secondaire.
- Éviter la paraphrase mécanique.
- Éviter le ton robotique.
- En cas d’erreur étudiante, corriger précisément et utilement.
- En cas de mode socratic, guider sans donner immédiatement toute la réponse.
- En cas de mode progression, donner un plan pédagogique concret.
- Terminer par une micro-action seulement si elle apporte une vraie valeur.

COURS
{cours if clean(cours) else "Aucun cours fourni."}

RÉPONSE ÉTUDIANTE OU BASE À ANALYSER
{build_previous_response_block(previous_response)}

DEMANDE
{message}
""".strip()


# =========================================================
# VARIANTS
# =========================================================

def answer_is_bad(answer):
    flags = output_quality_flags(answer)
    return "empty_output" in flags or "technical_error_output" in flags


def build_strategy_variants(mode, prompt):
    variants = []

    variants.append(prompt + """

CONTRÔLE FINAL
- Supprime les répétitions.
- Garde la structure seulement si elle aide.
- Chaque phrase doit avoir une valeur pédagogique.
""")

    if mode in {"expliquer", "reviser"}:
        variants.append(prompt + """

FOCUS VARIANTE
- Commence par le mécanisme central.
- Explique pourquoi la notion est importante.
- Termine par ce qu’il faut vraiment retenir.
""")

    if mode in {"corriger", "diagnostic"}:
        variants.append(prompt + """

FOCUS VARIANTE
- Sois plus exigeant.
- Distingue clairement juste / faux / incomplet.
- Donne une prochaine action concrète.
""")

    if mode in {"resumer", "a_retenir", "notions_centrales"}:
        variants.append(prompt + """

FOCUS VARIANTE
- Coupe tout le secondaire.
- Garde l’ossature intellectuelle.
- Privilégie la densité mémorisable.
""")

    if mode == "socratic":
        variants.append(prompt + """

FOCUS VARIANTE
- Pose une question guidée.
- Donne un indice.
- Ne donne pas toute la réponse d’un coup.
""")

    if mode == "exam":
        variants.append(prompt + """

FOCUS VARIANTE
- Fais un sujet crédible.
- Donne les attentes du correcteur.
- Évite le faux formalisme.
""")

    if mode == "progression":
        variants.append(prompt + """

FOCUS VARIANTE
- Construis une progression par étapes.
- Relie chaque étape à une compétence.
- Prévois un moyen de vérifier la progression.
""")

    return variants[:3]


def choose_best_variant(variants, message, niveau, matiere, cours, mode):
    best_answer = variants[0]
    best_score = -10**9
    best_meta = {}

    for ans in variants:
        if answer_is_bad(ans):
            continue

        meta = judge(
            answer=ans,
            message=message,
            niveau=niveau,
            matiere=matiere,
            cours=cours,
            mode=mode
        )

        score = meta.get("total", 0)

        if score > best_score:
            best_answer = ans
            best_score = score
            best_meta = meta
        elif score == best_score and len(clean(ans)) < len(clean(best_answer)):
            best_answer = ans
            best_meta = meta

    return best_answer, best_score, best_meta


# =========================================================
# MAIN
# =========================================================

def generate_answer(
    mem,
    message,
    niveau,
    matiere,
    cours,
    mode,
    student_id="",
    learning_style="",
    weaknesses="",
    previous_response="",
    learning_goal="comprendre",
    help_level="equilibre",
    student_eval=None,
    fast_eval=False
):
    if mode not in MODE_INSTRUCTIONS:
        mode = "expliquer"

    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["expliquer"])

    prompt = build_prompt(
        mem=mem,
        message=message,
        niveau=niveau,
        matiere=matiere,
        cours=cours,
        student_id=student_id,
        learning_style=learning_style,
        weaknesses=weaknesses,
        previous_response=previous_response,
        mode=mode,
        learning_goal=learning_goal,
        help_level=help_level,
        student_eval=student_eval
    )

    if fast_eval:
        return call_ollama([
            {"role": "system", "content": BASE_SYSTEM_PROMPT},
            {"role": "system", "content": mode_instruction},
            {"role": "user", "content": prompt}
        ], temp=0.14, max_tokens=1600)

    generated = []

    for variant_prompt in build_strategy_variants(mode, prompt):
        for temp in MODE_TEMPS.get(mode, [0.10, 0.18]):
            answer = call_ollama([
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "system", "content": mode_instruction},
                {"role": "user", "content": variant_prompt}
            ], temp=temp, max_tokens=2200)

            if answer and not answer_is_bad(answer):
                generated.append(answer)

    if not generated:
        return "Erreur de génération."

    best_answer, best_score, best_meta = choose_best_variant(
        generated,
        message,
        niveau,
        matiere,
        cours,
        mode
    )

    mem.setdefault("best_patterns", [])
    mem["best_patterns"].append({
        "timestamp": now_iso(),
        "mode": mode,
        "score": best_score,
        "verdict": best_meta.get("verdict", ""),
        "main_weakness": best_meta.get("main_weakness", ""),
        "risk_flags": best_meta.get("risk_flags", []),
        "length": len(best_answer)
    })
    mem["best_patterns"] = mem["best_patterns"][-120:]

    return best_answer