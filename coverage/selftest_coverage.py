from utils import *
from coverage.coverage_matrix import COVERAGE_FAMILIES

COVERAGE_TESTS = [
    {
        "name": "coverage_francais_resume",
        "family": "francais_litterature",
        "niveau": "lycee",
        "matiere": "français",
        "mode": "resumer",
        "cours": """
Le personnage de roman permet d’explorer des conflits intérieurs, des rapports sociaux et des trajectoires individuelles.
Il ne sert pas seulement à faire avancer l’intrigue : il peut aussi révéler une vision du monde.
""",
        "message": "Résume ce cours pour réviser efficacement."
    },
    {
        "name": "coverage_philo_expliquer",
        "family": "philosophie",
        "niveau": "Terminale",
        "matiere": "philosophie",
        "mode": "expliquer",
        "cours": """
La conscience permet au sujet de se rapporter à lui-même et au monde.
Mais elle ne garantit pas une parfaite transparence à soi.
""",
        "message": "Explique ce cours de manière claire."
    },
    {
        "name": "coverage_histoire_exam",
        "family": "histoire_geographie",
        "niveau": "lycee",
        "matiere": "histoire",
        "mode": "exam",
        "cours": """
L’industrialisation transforme les sociétés du XIXe siècle.
Elle modifie les rythmes de vie, les espaces et les rapports sociaux.
""",
        "message": "Propose un sujet type examen crédible."
    },
    {
        "name": "coverage_langues_corriger",
        "family": "langues",
        "niveau": "college",
        "matiere": "anglais",
        "mode": "corriger",
        "cours": """
En anglais, le prétérit simple sert à exprimer une action passée terminée.
On l’emploie souvent avec des repères temporels passés.
""",
        "previous_response": "The simple past is for action in the future and present habits.",
        "message": "Corrige cette réponse comme un professeur."
    },
    {
        "name": "coverage_SES_expliquer",
        "family": "SES_economie_gestion",
        "niveau": "Terminale",
        "matiere": "SES",
        "mode": "expliquer",
        "cours": """
Le chômage désigne la situation des personnes sans emploi, disponibles pour travailler et recherchant un emploi.
""",
        "message": "Explique ce cours simplement mais intelligemment."
    },
    {
        "name": "coverage_socio_reviser",
        "family": "sociologie_psychologie_sciences_sociales",
        "niveau": "licence",
        "matiere": "sociologie",
        "mode": "reviser",
        "cours": """
La socialisation désigne le processus par lequel un individu intériorise des normes, des valeurs et des rôles sociaux.
""",
        "message": "Transforme ce cours en fiche de révision utile."
    },
    {
        "name": "coverage_droit_corriger",
        "family": "droit_science_politique",
        "niveau": "licence",
        "matiere": "droit",
        "mode": "corriger",
        "cours": """
La règle de droit est générale, obligatoire et sanctionnée par l’autorité publique.
""",
        "previous_response": "La règle de droit est seulement un conseil moral sans sanction.",
        "message": "Corrige cette réponse avec précision."
    },
    {
        "name": "coverage_maths_expliquer",
        "family": "mathematiques",
        "niveau": "lycee",
        "matiere": "mathématiques",
        "mode": "expliquer",
        "cours": """
Une fonction associe à chaque nombre d’un ensemble de départ au plus une valeur dans un ensemble d’arrivée.
""",
        "message": "Explique cette notion de façon claire pour un élève."
    },
    {
        "name": "coverage_physique_resume",
        "family": "physique_chimie",
        "niveau": "lycee",
        "matiere": "physique-chimie",
        "mode": "resumer",
        "cours": """
La vitesse moyenne correspond au rapport entre la distance parcourue et la durée du trajet.
""",
        "message": "Fais un résumé utile pour retenir cette notion."
    },
    {
        "name": "coverage_bio_expliquer",
        "family": "SVT_biologie",
        "niveau": "lycee",
        "matiere": "SVT",
        "mode": "expliquer",
        "cours": """
L’ADN est une molécule qui porte l’information génétique.
Cette information est organisée en gènes.
""",
        "message": "Explique ce cours de manière pédagogique."
    },
    {
        "name": "coverage_info_corriger",
        "family": "informatique_numerique",
        "niveau": "lycee",
        "matiere": "informatique",
        "mode": "corriger",
        "cours": """
Un algorithme est une suite finie d’instructions permettant de résoudre un problème.
""",
        "previous_response": "Un algorithme est seulement un langage informatique.",
        "message": "Corrige cette réponse."
    },
    {
        "name": "coverage_arts_notions",
        "family": "arts_design_communication",
        "niveau": "licence",
        "matiere": "art appliqué",
        "mode": "notions_centrales",
        "cours": """
Une composition visuelle repose sur l’organisation des formes, des couleurs, des contrastes et des équilibres.
Elle oriente le regard et construit un sens.
""",
        "message": "Détecte les notions centrales du cours."
    },
]

def aggregate_scores(items, key):
    result = {}
    for item in items:
        k = item.get(key, "inconnu")
        total = item.get("score", {}).get("total", 0)
        if k not in result:
            result[k] = {"count": 0, "sum": 0, "average": 0}
        result[k]["count"] += 1
        result[k]["sum"] += total

    for k, stats in result.items():
        stats["average"] = round(stats["sum"] / stats["count"], 2)

    return result

def run_coverage_case(test_case, mem, generate_answer_fn, judge_fn):
    ans = generate_answer_fn(
        mem=mem,
        message=test_case["message"],
        niveau=test_case["niveau"],
        matiere=test_case["matiere"],
        cours=test_case["cours"],
        mode=test_case["mode"],
        previous_response=clean(test_case.get("previous_response")),
        fast_eval=True
    )

    score = judge_fn(
        ans,
        test_case["message"],
        test_case["niveau"],
        test_case["matiere"],
        test_case["cours"]
    )

    return {
        "test": test_case["name"],
        "family": test_case["family"],
        "mode": test_case["mode"],
        "matiere": test_case["matiere"],
        "niveau": test_case["niveau"],
        "score": score,
        "preview": clean(ans)[:320]
    }

def self_test_coverage(load_memory_fn, save_memory_fn, generate_answer_fn, judge_fn):
    mem = load_memory_fn()
    results = []

    for t in COVERAGE_TESTS:
        results.append(run_coverage_case(t, mem, generate_answer_fn, judge_fn))

    diagnostics = {
        "by_family": aggregate_scores(results, "family"),
        "by_mode": aggregate_scores(results, "mode"),
        "by_subject": aggregate_scores(results, "matiere")
    }

    return {
        "results": results,
        "diagnostics": diagnostics
    }