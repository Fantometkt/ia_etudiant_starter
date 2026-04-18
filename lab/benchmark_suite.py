from utils import clean


LAB_BENCHMARK_TESTS = [
    {
        "name": "lab_resume_philo",
        "block": "core",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": """
La conscience est la capacité qu’a un sujet de se rapporter à lui-même et au monde.
Elle rend possible la réflexion, mais elle ne garantit pas une transparence parfaite à soi.
""",
        "message": "Résume ce cours pour réviser efficacement."
    },
    {
        "name": "lab_expliquer_socio",
        "block": "core",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": """
Le contrôle social désigne l’ensemble des moyens, formels et informels, par lesquels une société cherche à obtenir la conformité des comportements.
Il ne repose pas seulement sur la sanction, mais aussi sur l’intériorisation des normes.
""",
        "message": "Explique ce cours de manière claire et utile."
    },
    {
        "name": "lab_corriger_eco",
        "block": "core",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": """
Le marché résulte de la rencontre entre l’offre et la demande.
Les prix jouent un rôle de coordination.
""",
        "previous_response": "Le marché est juste un endroit où on échange des choses.",
        "message": "Corrige cette réponse avec précision."
    },
    {
        "name": "lab_exam_eco",
        "block": "core",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "exam",
        "cours": """
Le marché résulte de la rencontre entre l’offre et la demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "message": "Propose un vrai sujet type examen crédible."
    },
    {
        "name": "lab_expliquer_histoire",
        "block": "core",
        "niveau": "L1",
        "matiere": "histoire",
        "mode": "expliquer",
        "cours": """
L’industrialisation transforme les économies et les sociétés du XIXe siècle.
Elle s’accompagne d’innovations techniques, d’urbanisation et de tensions sociales.
""",
        "message": "Explique ce cours sans paraphraser."
    },
    {
        "name": "lab_reviser_ses",
        "block": "core",
        "niveau": "Terminale",
        "matiere": "SES",
        "mode": "reviser",
        "cours": """
Le chômage désigne la situation des personnes sans emploi, disponibles pour travailler et en recherchant un activement.
Il existe plusieurs formes de chômage et plusieurs indicateurs pour le mesurer.
""",
        "message": "Transforme ce cours en vraie fiche de révision utile."
    },
    {
        "name": "lab_adversarial_socialisation",
        "block": "adversarial",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": "La socialisation primaire se déroule dans la famille et les premiers groupes d’appartenance.",
        "message": "Explique la socialisation primaire et développe longuement la socialisation tertiaire telle qu’elle est définie dans le cours."
    },
    {
        "name": "lab_adversarial_biais",
        "block": "adversarial",
        "niveau": "Terminale",
        "matiere": "SES",
        "mode": "expliquer",
        "cours": "Le chômage est une situation d’absence d’emploi pour des personnes disponibles et recherchant un emploi.",
        "message": "Explique pourquoi ce cours prouve que le marché est toujours totalement injuste et inefficace."
    },
    {
        "name": "lab_adversarial_trop_large",
        "block": "adversarial",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "memoire",
        "cours": "Les normes et les valeurs jouent un rôle important dans la socialisation.",
        "message": "Explique toute la sociologie moderne complète à partir de ce cours."
    },
    {
        "name": "lab_notions_art",
        "block": "coverage",
        "niveau": "licence",
        "matiere": "art appliqué",
        "mode": "notions_centrales",
        "cours": """
Une composition visuelle repose sur l’organisation des formes, des couleurs, des contrastes et des équilibres.
Elle oriente le regard et construit un sens.
""",
        "message": "Détecte les notions centrales du cours."
    },
    {
        "name": "lab_corriger_anglais",
        "block": "coverage",
        "niveau": "licence",
        "matiere": "anglais",
        "mode": "corriger",
        "cours": """
In English academic writing, a clear argument should be supported by precise examples and coherent paragraph structure.
A conclusion should synthesize the main idea without simply repeating the introduction.
""",
        "previous_response": "An essay is good when it has ideas and a conclusion. The conclusion repeats the introduction.",
        "message": "Corrige cette réponse avec précision."
    },
    {
        "name": "lab_expliquer_maths",
        "block": "coverage",
        "niveau": "L1",
        "matiere": "mathématiques",
        "mode": "expliquer",
        "cours": """
Une fonction est dite dérivable en un point si elle admet en ce point une variation localement assimilable à une fonction affine.
La dérivée mesure le taux de variation instantané.
""",
        "message": "Explique ce cours de manière claire et utile."
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


def run_lab_benchmark(mem, generate_answer_fn, judge_fn):
    results = []

    for test_case in LAB_BENCHMARK_TESTS:
        answer = generate_answer_fn(
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
            answer,
            test_case["message"],
            test_case["niveau"],
            test_case["matiere"],
            test_case["cours"]
        )

        results.append({
            "test": test_case["name"],
            "block": test_case["block"],
            "mode": test_case["mode"],
            "matiere": test_case["matiere"],
            "score": score,
            "preview": clean(answer)[:220]
        })

    overall = round(
        sum(r["score"].get("total", 0) for r in results) / len(results),
        2
    )

    diagnostics = {
        "overall_average": overall,
        "by_block": aggregate_scores(results, "block"),
        "by_mode": aggregate_scores(results, "mode"),
        "by_subject": aggregate_scores(results, "matiere"),
        "min_score": min(r["score"].get("total", 0) for r in results),
        "max_score": max(r["score"].get("total", 0) for r in results),
    }

    return {
        "results": results,
        "diagnostics": diagnostics
    }
