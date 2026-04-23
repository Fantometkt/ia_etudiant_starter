from utils import *
from prompts import *
from memory_manager import *
from course_analyzer import analyze_course, format_course_analysis
from judge import judge
from llm import call_ollama


FAST_MODES = {"expliquer", "resumer", "a_retenir", "quiz"}

MODE_TEMPS = {
    "expliquer": [0.12, 0.22, 0.32],
    "resumer": [0.08, 0.16, 0.24],
    "a_retenir": [0.08, 0.16],
    "quiz": [0.15, 0.25, 0.35],
    "corriger": [0.12, 0.20, 0.28],
    "exam": [0.12, 0.20, 0.28],
    "notions_centrales": [0.12, 0.20, 0.28],
    "memoire": [0.18, 0.28, 0.36],
    "reviser": [0.12, 0.20, 0.28],
}


# ========================
# 🧠 DIAGNOSTIC PÉDAGOGIQUE
# ========================

def infer_real_need(message, mode, previous_response="", learning_goal="comprendre"):
    text = clean(message).lower()
    prev = clean(previous_response).lower()

    if mode == "corriger" or prev:
        return "correction_progression"

    if mode == "exam":
        return "preparation_examen"

    if mode == "quiz":
        return "entrainement_actif"

    if mode == "a_retenir":
        return "condensation_memorisation"

    if mode == "reviser":
        return "revision_memorisation"

    if mode == "notions_centrales":
        return "structuration_ossature"

    if "je n'ai pas compris" in text or "réexplique" in text or "réexpliquer" in text:
        return "deblocage_incomprehension"

    if "différence" in text or "confond" in text or "confusion" in text:
        return "clarification_confusion"

    if "résume" in text or mode == "resumer":
        return "synthese_essentiel"

    if "explique" in text or mode == "expliquer":
        return "comprehension_profonde"

    if learning_goal:
        return learning_goal

    return "comprehension_profonde"


def infer_difficulty_level(cours, message, niveau):
    cours_len = len(clean(cours))
    msg = clean(message).lower()
    niv = clean(niveau).lower()

    difficulty_score = 0

    if cours_len > 1500:
        difficulty_score += 2
    elif cours_len > 600:
        difficulty_score += 1

    hard_markers = [
        "pourquoi", "mécanisme", "enjeu", "logique", "différence",
        "compare", "démontre", "analyse", "implication"
    ]
    if any(m in msg for m in hard_markers):
        difficulty_score += 1

    if "l3" in niv or "master" in niv or "licence 3" in niv:
        difficulty_score += 1

    if difficulty_score >= 3:
        return "difficile"
    if difficulty_score >= 1:
        return "intermediaire"
    return "simple"


def infer_blocking_risks(message, cours, mode, previous_response=""):
    text = clean(message).lower()
    risks = []

    if not clean(cours):
        risks.append("absence_de_cours")

    if previous_response:
        risks.append("copie_etudiante_a_corriger")

    if mode == "expliquer":
        risks.append("reformulation_sans_mecanisme")

    if mode == "resumer":
        risks.append("condensation_trop_superficielle")

    if mode == "reviser":
        risks.append("memorisation_sans_hierarchisation")

    if mode == "exam":
        risks.append("cadre_trop_scolaire_ou_bavard")

    if mode == "corriger":
        risks.append("jugement_flou_ou_peu_formateur")

    confusion_markers = ["différence", "confond", "confusion", "nuance"]
    if any(m in text for m in confusion_markers):
        risks.append("confusion_probable")

    if "aussi" in text and "cours" in text:
        risks.append("tentation_de_sortir_du_cours")

    return risks[:6]


def choose_pedagogical_strategy(real_need, mode, help_level="equilibre"):
    strategy_map = {
        "deblocage_incomprehension": "expliquer_dabord_le_noeud_de_blocage",
        "clarification_confusion": "distinguer_netement_les_notions",
        "correction_progression": "diagnostiquer_puis_corriger_pour_faire_progresser",
        "preparation_examen": "produire_un_cadre_compact_et_exploitable",
        "entrainement_actif": "tester_la_comprehension_utile",
        "condensation_memorisation": "garder_le_noyau_memorisable",
        "revision_memorisation": "structurer_pour_retenir_et_revoir",
        "structuration_ossature": "faire_apparaitre_la_charpente_du_cours",
        "synthese_essentiel": "eliminer_tout_sauf_lessentiel",
        "comprehension_profonde": "mettre_au_centre_le_mecanisme_et_la_logique",
    }

    strategy = strategy_map.get(real_need, "mettre_au_centre_le_mecanisme_et_la_logique")

    if help_level == "fort":
        strategy += "_avec_plus_de_guidage"
    elif help_level == "leger":
        strategy += "_avec_plus_de_concision"

    return strategy


def build_pedagogical_diagnostic_block(
    message,
    cours,
    niveau,
    mode,
    previous_response="",
    learning_goal="comprendre",
    help_level="equilibre"
):
    real_need = infer_real_need(message, mode, previous_response, learning_goal)
    difficulty = infer_difficulty_level(cours, message, niveau)
    risks = infer_blocking_risks(message, cours, mode, previous_response)
    strategy = choose_pedagogical_strategy(real_need, mode, help_level)

    risk_lines = "\n".join(f"- {r}" for r in risks) if risks else "- aucun risque majeur identifié"

    return f"""
DIAGNOSTIC PÉDAGOGIQUE IMPLICITE
- Besoin réel détecté : {real_need}
- Difficulté estimée : {difficulty}
- Stratégie pédagogique à privilégier : {strategy}

RISQUES À SURVEILLER
{risk_lines}

RÈGLES DE DÉCISION
- Identifie d’abord ce qui aide le plus l’étudiant ici
- Traite en priorité le point le plus important, le plus difficile ou le plus bloquant
- Choisis la forme la plus utile, pas la plus scolaire
- Si une confusion est probable, clarifie-la explicitement
- Si un mécanisme structure la compréhension, mets-le au centre
- Si un détail n’aide pas à comprendre ou réussir, réduis-le fortement
"""
    

# ========================
# 🧠 BLOCS CONTEXTUELS
# ========================

def build_evolution_block(mem):
    if not mem.get("selftests"):
        return ""

    last = mem["selftests"][-1].get("diagnostics", {})
    recos = last.get("recommendations", [])
    weak = last.get("weak_points", [])

    bloc = []

    for r in recos[:3]:
        bloc.append(f"- {r}")

    for w in weak[:2]:
        bloc.append(f"- Corriger : {w}")

    if not bloc:
        return ""

    return f"""
AMÉLIORATION CONTINUE
{chr(10).join(bloc)}

RÈGLES D'ÉVOLUTION
- Corrige activement ces faiblesses
- Ne reproduis pas les erreurs passées
- Évite la paraphrase descriptive
- Hiérarchise davantage
- Augmente la valeur pédagogique réelle
"""


def build_mode_behavior(mode):
    if mode == "resumer":
        return """
COMPORTEMENT ATTENDU
- très peu de structure
- pas de sous-parties décoratives
- pas de redondance
- priorité à la densité utile
- garder uniquement ce qui mérite d’être retenu
"""
    if mode == "corriger":
        return """
COMPORTEMENT ATTENDU
- jugement net
- hiérarchisation des erreurs
- expliquer le mécanisme, pas seulement le constat
- vraie amélioration de copie
- correction tournée vers la progression
"""
    if mode == "exam":
        return """
COMPORTEMENT ATTENDU
- sujet crédible
- attentes du correcteur utiles
- plan efficace
- pas de développement scolaire inutile
- compacité maximale sans perte d’utilité
"""
    if mode == "expliquer":
        return """
COMPORTEMENT ATTENDU
- rendre le cours compréhensible
- aller au mécanisme
- éviter la simple reformulation
- traiter d’abord le point difficile ou central
"""
    if mode == "notions_centrales":
        return """
COMPORTEMENT ATTENDU
- extraction forte de l’essentiel
- hiérarchisation claire
- pas d’explication décorative
- donner une vraie ossature intellectuelle
"""
    if mode == "reviser":
        return """
COMPORTEMENT ATTENDU
- support de révision mémorisable
- liens importants mis en évidence
- pas de bavardage
- aide directe à la mémorisation et à la compréhension
"""
    if mode == "quiz":
        return """
COMPORTEMENT ATTENDU
- questions utiles
- pas de trivialité
- tester la compréhension réelle
- faire apparaître les pièges utiles
"""
    if mode == "a_retenir":
        return """
COMPORTEMENT ATTENDU
- ultra-condensation
- impact maximal
- aucun mot inutile
- formulation nette et mémorisable
"""
    if mode == "memoire":
        return """
COMPORTEMENT ATTENDU
- stratégie concrète
- priorisation forte
- actionnable
- adaptée aux blocages réels
"""
    return """
COMPORTEMENT ATTENDU
- réponse utile
- claire
- hiérarchisée
- centrée sur la progression
"""


def build_help_level_block(help_level):
    if help_level == "fort":
        return """
NIVEAU D’AIDE
- explique davantage les points difficiles
- explicite plus clairement les liens
- sécurise davantage la compréhension
- privilégie la pédagogie sur la concision brute
"""
    if help_level == "leger":
        return """
NIVEAU D’AIDE
- va droit à l’essentiel
- garde seulement ce qui apporte le plus de valeur
- privilégie une réponse compacte
"""
    return """
NIVEAU D’AIDE
- équilibre entre compréhension, clarté et concision
- assez de guidage pour aider, sans alourdir inutilement
"""


def build_learning_goal_block(learning_goal):
    goal = clean(learning_goal).lower()

    if "comprendre" in goal:
        return """
OBJECTIF PÉDAGOGIQUE PRIORITAIRE
- viser avant tout la compréhension réelle
- faire apparaître la logique et le mécanisme
"""
    if "retenir" in goal or "mémoris" in goal:
        return """
OBJECTIF PÉDAGOGIQUE PRIORITAIRE
- viser avant tout la mémorisation efficace
- rendre la réponse facilement révisable
"""
    if "examen" in goal or "partiel" in goal:
        return """
OBJECTIF PÉDAGOGIQUE PRIORITAIRE
- viser avant tout la réussite en évaluation
- privilégier l’exploitable, le cadré, le rentable
"""
    return """
OBJECTIF PÉDAGOGIQUE PRIORITAIRE
- aider à comprendre et progresser réellement
"""


def build_weaknesses_block(weaknesses):
    w = clean(weaknesses)
    if not w:
        return ""
    return f"""
FAIBLESSES OU POINTS DE VIGILANCE ÉTUDIANT
{w}

RÈGLES
- adapte implicitement ton aide à ces fragilités
- renforce ce qui risque de bloquer l’apprentissage
"""


def build_previous_response_block(previous_response):
    prev = clean(previous_response)
    if not prev:
        return "Aucune"

    return f"""{prev}

RÈGLES
- tiens compte de cette réponse pour identifier erreurs, imprécisions ou blocages
- si elle révèle une confusion, traite-la explicitement
"""


# ========================
# 🧱 CONSTRUCTION DU PROMPT
# ========================

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
    help_level="equilibre"
):
    student_context = build_student_memory_context(mem, student_id)
    course_analysis = analyze_course(cours, niveau, matiere, force=False)
    analysis_text = format_course_analysis(course_analysis)
    evolution_block = build_evolution_block(mem)
    mode_behavior = build_mode_behavior(mode)
    help_block = build_help_level_block(help_level)
    goal_block = build_learning_goal_block(learning_goal)
    weaknesses_block = build_weaknesses_block(weaknesses)
    pedagogical_diagnostic = build_pedagogical_diagnostic_block(
        message=message,
        cours=cours,
        niveau=niveau,
        mode=mode,
        previous_response=previous_response,
        learning_goal=learning_goal,
        help_level=help_level
    )

    learning_style_block = ""
    if clean(learning_style):
        learning_style_block = f"""
STYLE D’APPRENTISSAGE INDIQUÉ
{clean(learning_style)}

RÈGLES
- adapte légèrement la forme si cela aide vraiment
- ne caricature jamais le style d’apprentissage
- garde la priorité sur la fidélité, la compréhension et l’utilité
"""

    return f"""
CONTEXTE
- Niveau : {niveau}
- Matière : {matiere}
- Mode : {mode}

{goal_block}

{help_block}

PROFIL ÉTUDIANT
{student_context if clean(student_context) else "Aucun contexte étudiant spécifique."}

{learning_style_block}

{weaknesses_block}

ANALYSE DU COURS
{analysis_text}

{pedagogical_diagnostic}

{evolution_block}

{mode_behavior}

RÈGLES DE PRODUCTION
- Base principale = le cours
- Réponse dense, utile et pédagogiquement ciblée
- Évite la paraphrase mécanique
- Hiérarchise clairement
- Supprime les répétitions
- Si le cours est insuffisant, dis-le clairement
- Si aucun cours n’est fourni, utilise seulement des connaissances générales fiables, sobres et pédagogiquement utiles
- N’alourdis pas la structure si elle n’apporte rien
- Cherche à aider réellement l’étudiant, pas seulement à produire une réponse propre
- Si un blocage probable existe, traite-le avant le reste
- Si une confusion classique est probable, signale-la
- Si une partie n’aide ni à comprendre, ni à retenir, ni à réussir, coupe-la

COURS
{cours if cours else "Aucun cours fourni."}

RÉPONSE ÉTUDIANTE OU BASE À ANALYSER
{build_previous_response_block(previous_response)}

DEMANDE
{message}
"""


# ========================
# 🚨 QUALITÉ DE SORTIE
# ========================

def answer_is_bad(ans: str) -> bool:
    a = clean(ans).lower()
    if not a:
        return True

    bad_markers = [
        "erreur ia",
        "erreur de génération",
        "traceback",
        "importerror",
        "syntaxerror",
    ]
    return any(marker in a for marker in bad_markers)


def score_variant(ans, message, niveau, matiere, cours):
    if answer_is_bad(ans):
        return -999, {"total": -999}
    raw = judge(ans, message, niveau, matiere, cours)
    return raw.get("total", 0), raw


def choose_best_variant(variants, message, niveau, matiere, cours):
    best_answer = variants[0]
    best_score = -10**9
    best_meta = None

    for ans in variants:
        total, raw = score_variant(ans, message, niveau, matiere, cours)

        if total > best_score:
            best_score = total
            best_answer = ans
            best_meta = raw
        elif total == best_score:
            # à score égal : préfère le plus court seulement s'il reste suffisamment dense
            if len(clean(ans)) < len(clean(best_answer)):
                best_answer = ans
                best_meta = raw

    return best_answer, best_score, best_meta


# ========================
# 🧪 VARIANTES STRATÉGIQUES
# ========================

def build_strategy_variants(mode, prompt):
    """
    Au lieu de varier seulement la température,
    on varie légèrement l’angle pédagogique.
    """
    variants = []

    base_suffix = """
CONTRÔLE FINAL
- supprime toute redondance
- vérifie que chaque phrase apporte une vraie valeur
- garde seulement ce qui aide à comprendre, retenir ou réussir
"""

    variants.append(prompt + "\n\n" + base_suffix)

    if mode in {"expliquer", "reviser", "corriger"}:
        variants.append(prompt + """

FOCUS SUPPLÉMENTAIRE
- traite d’abord le point le plus bloquant ou le plus difficile
- aide explicitement l’étudiant à dépasser la confusion principale
""")

    if mode in {"resumer", "a_retenir", "notions_centrales"}:
        variants.append(prompt + """

FOCUS SUPPLÉMENTAIRE
- coupe encore davantage le secondaire
- garde uniquement la charpente utile
""")

    if mode == "exam":
        variants.append(prompt + """

FOCUS SUPPLÉMENTAIRE
- privilégie un cadre immédiatement exploitable en partiel
- évite toute lourdeur inutile
""")

    if mode == "quiz":
        variants.append(prompt + """

FOCUS SUPPLÉMENTAIRE
- privilégie des questions révélant la compréhension réelle
- évite les formulations triviales
""")

    return variants[:3]


# ========================
# 🚀 GÉNÉRATION PRINCIPALE
# ========================

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
    fast_eval=False
):
    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["expliquer"])

    prompt = build_prompt(
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
        learning_goal,
        help_level
    )

    if fast_eval:
        messages = [
            {"role": "system", "content": BASE_SYSTEM_PROMPT},
            {"role": "system", "content": mode_instruction},
            {"role": "user", "content": prompt}
        ]
        return call_ollama(messages, temp=0.18)

    prompt_variants = build_strategy_variants(mode, prompt)
    temps = MODE_TEMPS.get(mode, [0.12, 0.22])
    variants = []

    for p in prompt_variants:
        for t in temps:
            messages = [
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "system", "content": mode_instruction},
                {"role": "user", "content": p}
            ]

            ans = call_ollama(messages, temp=t)
            if ans and not answer_is_bad(ans):
                variants.append(ans)

    if not variants:
        return "Erreur de génération."

    best_answer, best_score, best_meta = choose_best_variant(
        variants, message, niveau, matiere, cours
    )

    mem.setdefault("best_patterns", []).append({
        "mode": mode,
        "score": best_score,
        "length": len(best_answer),
        "verdict": (best_meta or {}).get("verdict", ""),
        "main_weakness": (best_meta or {}).get("main_weakness", ""),
    })
    mem["best_patterns"] = mem["best_patterns"][-50:]

    return best_answer