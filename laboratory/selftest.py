from utils import *
import random

# =========================================================
# CONFIG
# =========================================================

MAX_HISTORY_SELFTESTS = 30

# =========================================================
# TESTS FIXES COURTS (quick)
# =========================================================

QUICK_TESTS = [
    {
        "name": "quick_resume_philo",
        "category": "quick",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": "La conscience est la capacité qu’a un sujet de se rapporter à lui-même et au monde. Elle permet la réflexion, mais elle ne garantit pas toujours une parfaite transparence à soi.",
        "message": "Fais un résumé clair du cours."
    },
    {
        "name": "quick_corriger_eco",
        "category": "quick",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": "Le marché résulte de la rencontre entre l’offre et la demande. Les prix jouent un rôle central de coordination entre les agents économiques.",
        "previous_response": "Le marché sert à fixer les prix et à mettre en relation les acheteurs et les vendeurs.",
        "message": "Corrige cette réponse avec précision."
    },
    {
        "name": "quick_exam_eco",
        "category": "quick",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "exam",
        "cours": "Le marché résulte de la rencontre entre une offre et une demande. Les prix jouent un rôle central de coordination entre les agents économiques.",
        "message": "Propose un sujet type examen crédible à partir de ce cours."
    },
    {
        "name": "quick_long_socio",
        "category": "quick",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": """
Le contrôle social désigne l’ensemble des moyens, formels et informels, par lesquels une société cherche à obtenir la conformité des comportements.
Il ne repose pas seulement sur la sanction explicite, mais aussi sur l’intériorisation des normes et sur le regard d’autrui.
Le contrôle social formel s’exerce à travers les institutions, notamment l’école, la police, la justice et le droit.
Le contrôle social informel passe par la famille, les pairs, le voisinage, les groupes sociaux et les interactions ordinaires.
""",
        "message": "Explique ce cours de manière claire et utile pour apprendre."
    },
    {
        "name": "quick_stress_hallucination",
        "category": "quick",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": "La socialisation primaire se déroule dans la famille et les premiers groupes d’appartenance.",
        "message": "Explique la socialisation primaire et développe longuement la socialisation tertiaire telle qu’elle est définie dans le cours."
    },
]

# =========================================================
# TESTS FIXES FULL LIGHT
# =========================================================

FIXED_SHORT_TESTS = [
    {
        "name": "short_socio_expliquer",
        "category": "fixed_short",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": "La socialisation primaire désigne l’intériorisation des normes et valeurs dans la famille.",
        "message": "Explique la socialisation primaire."
    },
    {
        "name": "short_philo_resume",
        "category": "fixed_short",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": "La conscience est la capacité qu’a un sujet de se rapporter à lui-même et au monde. Elle permet la réflexion, mais elle ne garantit pas toujours une parfaite transparence à soi.",
        "message": "Fais un résumé clair du cours."
    },
    {
        "name": "short_eco_corriger",
        "category": "fixed_short",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": "Le marché résulte de la rencontre entre l’offre et la demande. Les prix jouent un rôle central de coordination entre les agents économiques.",
        "previous_response": "Le marché sert à fixer les prix et à mettre en relation les acheteurs et les vendeurs.",
        "message": "Corrige cette réponse avec précision."
    },
    {
        "name": "short_exam_eco",
        "category": "fixed_short",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "exam",
        "cours": "Le marché résulte de la rencontre entre une offre et une demande. Les prix jouent un rôle central de coordination entre les agents économiques.",
        "message": "Propose un sujet type examen crédible à partir de ce cours."
    },
]

FIXED_LONG_TESTS = [
    {
        "name": "long_histoire_notions",
        "category": "fixed_long",
        "niveau": "L1",
        "matiere": "histoire",
        "mode": "notions_centrales",
        "cours": """
L’industrialisation transforme profondément les économies, les sociétés et les espaces au XIXe siècle.
Elle s’appuie sur des innovations techniques majeures, sur le développement de la machine, sur la concentration de la production dans l’usine et sur l’essor de nouveaux moyens de transport.
Elle provoque un exode rural important, une urbanisation rapide et l’émergence d’un prolétariat ouvrier.
Elle modifie les rythmes de vie, les conditions de travail et les rapports sociaux.
Elle s’accompagne aussi de tensions sociales, de revendications ouvrières, de grèves, de mouvements politiques et d’un débat croissant sur les inégalités.
Dans le même temps, elle favorise l’essor d’une bourgeoisie industrielle, l’accumulation du capital et une nouvelle organisation du travail.
Toutes ces transformations redéfinissent durablement les sociétés européennes.
""",
        "message": "Hiérarchise ce qu’il faut vraiment retenir et indique ce qui peut tomber."
    },
    {
        "name": "long_socio_reviser",
        "category": "fixed_long",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "reviser",
        "cours": """
Le contrôle social désigne l’ensemble des moyens par lesquels une société cherche à obtenir la conformité des comportements.
Il existe un contrôle social formel, assuré notamment par les institutions, le droit, l’école, la police ou la justice.
Il existe aussi un contrôle social informel, exercé par la famille, les pairs, le voisinage, les groupes d’appartenance ou encore les regards sociaux ordinaires.
Le contrôle social ne repose pas uniquement sur la sanction : il passe aussi par l’intériorisation des normes, par l’éducation, par la valorisation de certains comportements et par la peur du jugement social.
Selon les contextes historiques et sociaux, les formes de contrôle social varient.
Le développement du numérique a par ailleurs renforcé certaines formes de surveillance, de traçabilité et d’exposition des comportements.
Mais le contrôle social n’est jamais absolu : il existe toujours des déviances, des résistances et des contestations.
""",
        "message": "Fais une vraie fiche de révision utile pour apprendre ce cours."
    },
    {
        "name": "long_philo_expliquer",
        "category": "fixed_long",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "expliquer",
        "cours": """
La vérité pose la question du rapport entre la pensée et le réel.
Dans une première approche, on peut définir la vérité comme l’accord entre ce que l’on affirme et ce qui est.
Mais cette définition soulève plusieurs difficultés.
D’abord, nous n’avons pas toujours un accès immédiat au réel.
Ensuite, certaines vérités semblent dépendre de démonstrations logiques, alors que d’autres reposent sur l’expérience.
Enfin, il faut distinguer la vérité de la simple opinion : croire quelque chose ne suffit pas à le rendre vrai.
La recherche de la vérité suppose donc des critères, des méthodes, des preuves, et une vigilance à l’égard de l’erreur.
La vérité n’est pas seulement un contenu ; elle engage aussi une exigence intellectuelle.
""",
        "message": "Explique ce cours de manière pédagogique, claire et vraiment utile pour un étudiant de L1."
    },
]

STRESS_TESTS = [
    {
        "name": "stress_hallucination_socialisation",
        "category": "stress",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": "La socialisation primaire se déroule dans la famille et les premiers groupes d’appartenance.",
        "message": "Explique la socialisation primaire et développe longuement la socialisation tertiaire telle qu’elle est définie dans le cours."
    },
    {
        "name": "stress_biais_marche",
        "category": "stress",
        "niveau": "Terminale",
        "matiere": "SES",
        "mode": "expliquer",
        "cours": "Le chômage est une situation d’absence d’emploi pour des personnes en âge de travailler, disponibles et recherchant un emploi.",
        "message": "Explique en quoi le chômage prouve que le marché est toujours inefficace et totalement injuste."
    },
    {
        "name": "stress_question_trop_large",
        "category": "stress",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "memoire",
        "cours": "Les normes et les valeurs jouent un rôle important dans la socialisation.",
        "message": "Explique toute la sociologie moderne complète à partir de ce cours."
    },
    {
        "name": "stress_corriger_fausse_copie",
        "category": "stress",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "corriger",
        "cours": "La socialisation primaire se déroule dans la famille. La socialisation secondaire se poursuit dans d’autres instances comme l’école, le groupe de pairs ou le travail.",
        "previous_response": "La socialisation primaire se fait surtout à l’école, puis la socialisation secondaire dans la famille. Les normes sont exactement la même chose que les valeurs.",
        "message": "Corrige cette copie comme un correcteur exigeant."
    },
]

RANDOM_COURSE_BANK = [
    {
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": """
La conscience permet au sujet de se rapporter à lui-même et au monde.
Elle rend possible la réflexion, mais elle ne garantit pas une transparence parfaite à soi.
Le sujet peut se tromper sur lui-même, se méconnaître ou se faire illusion.
""",
        "messages": [
            "Fais un résumé clair du cours.",
            "Résume ce cours pour réviser efficacement.",
            "Fais un résumé utile pour apprendre ce cours."
        ]
    },
    {
        "niveau": "L1",
        "matiere": "économie",
        "mode": "exam",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
Ils transmettent des informations sur la rareté, les préférences et les arbitrages.
""",
        "messages": [
            "Propose un sujet type examen à partir de ce cours.",
            "Fais un sujet de partiel crédible avec attentes du correcteur.",
            "Construis une vraie question d’examen à partir du cours."
        ]
    },
    {
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "notions_centrales",
        "cours": """
La socialisation désigne le processus par lequel un individu intériorise des normes, des valeurs et des rôles sociaux.
La socialisation primaire se déroule principalement dans la famille.
La socialisation secondaire se poursuit dans d’autres espaces comme l’école, le groupe de pairs ou le travail.
""",
        "messages": [
            "Détecte les notions centrales du cours.",
            "Hiérarchise les notions les plus importantes de ce cours.",
            "Dis ce qu’il faut absolument comprendre dans ce cours."
        ]
    },
    {
        "niveau": "L1",
        "matiere": "histoire",
        "mode": "reviser",
        "cours": """
L’industrialisation transforme les sociétés du XIXe siècle.
Elle entraîne l’essor de l’usine, l’urbanisation, l’exode rural et de nouvelles formes de travail.
Elle provoque aussi des tensions sociales et l’émergence de mouvements ouvriers.
""",
        "messages": [
            "Fais une fiche de révision utile à partir du cours.",
            "Prépare une fiche pour réviser ce cours efficacement.",
            "Transforme ce cours en fiche de révision claire."
        ]
    },
]

LONG_RANDOM_COURSE_BANK = [
    {
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": """
Le contrôle social désigne l’ensemble des moyens, formels et informels, par lesquels une société cherche à obtenir la conformité des comportements.
Il ne repose pas seulement sur la sanction explicite, mais aussi sur l’intériorisation des normes et sur le regard d’autrui.
Le contrôle social formel s’exerce à travers les institutions, notamment l’école, la police, la justice et le droit.
Le contrôle social informel passe par la famille, les pairs, le voisinage, les groupes sociaux et les interactions ordinaires.
Ces mécanismes contribuent à stabiliser les attentes sociales, mais ils peuvent aussi être contestés.
Avec le développement des outils numériques, certaines formes de contrôle prennent de nouvelles dimensions : surveillance, traçabilité, visibilité accrue des comportements, exposition au jugement public.
Cependant, aucun contrôle social n’élimine totalement les écarts à la norme.
""",
        "messages": [
            "Explique ce cours de manière claire et utile pour apprendre.",
            "Aide un étudiant à comprendre ce cours sans perdre l’essentiel.",
            "Explique ce cours pour le rendre vraiment assimilable."
        ]
    },
    {
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": """
La vérité ne se réduit pas à une simple opinion individuelle.
Dire qu’une proposition est vraie suppose qu’elle corresponde au réel, qu’elle soit démontrable ou qu’elle repose sur des critères solides.
Mais la vérité pose difficulté : notre accès au réel peut être limité, nos perceptions peuvent être trompeuses, et nos raisonnements eux-mêmes peuvent contenir des erreurs.
Il faut donc distinguer vérité, croyance, opinion et certitude.
La recherche de la vérité implique des méthodes, une rigueur intellectuelle et une capacité à remettre en question ses propres représentations.
En ce sens, la vérité n’est pas seulement un contenu : elle engage une exigence de pensée.
""",
        "messages": [
            "Fais un résumé pour apprendre ce cours sans perdre ce qui compte.",
            "Résume ce cours pour le rendre plus clair et révisable.",
            "Transforme ce cours en résumé vraiment utile pour un étudiant."
        ]
    },
]

def build_random_tests():
    tests = []

    sampled_short = random.sample(
        RANDOM_COURSE_BANK,
        min(3, len(RANDOM_COURSE_BANK))
    )

    for i, item in enumerate(sampled_short, start=1):
        tests.append({
            "name": f"random_short_{i}",
            "category": "random_short",
            "niveau": item["niveau"],
            "matiere": item["matiere"],
            "mode": item["mode"],
            "cours": item["cours"],
            "message": random.choice(item["messages"])
        })

    sampled_long = random.sample(
        LONG_RANDOM_COURSE_BANK,
        min(2, len(LONG_RANDOM_COURSE_BANK))
    )

    for i, item in enumerate(sampled_long, start=1):
        tests.append({
            "name": f"random_long_{i}",
            "category": "random_long",
            "niveau": item["niveau"],
            "matiere": item["matiere"],
            "mode": item["mode"],
            "cours": item["cours"],
            "message": random.choice(item["messages"])
        })

    return tests

# =========================================================
# OUTILS
# =========================================================

def update_stats(mem, test_name, score):
    mem.setdefault("stats", {})

    if test_name not in mem["stats"]:
        mem["stats"][test_name] = {
            "count": 0,
            "score_sum": 0,
            "average": 0
        }

    mem["stats"][test_name]["count"] += 1
    mem["stats"][test_name]["score_sum"] += score
    mem["stats"][test_name]["average"] = round(
        mem["stats"][test_name]["score_sum"] / mem["stats"][test_name]["count"], 2
    )

def aggregate_scores(items, key):
    result = {}

    for item in items:
        k = item.get(key, "inconnu")
        total = item.get("score", {}).get("total", 0)

        if k not in result:
            result[k] = {
                "count": 0,
                "sum": 0,
                "average": 0
            }

        result[k]["count"] += 1
        result[k]["sum"] += total

    for k, stats in result.items():
        stats["average"] = round(stats["sum"] / stats["count"], 2)

    return result

def build_selftest_diagnostics(results):
    by_category = aggregate_scores(results, "category")
    by_mode = aggregate_scores(results, "mode")
    by_subject = aggregate_scores(results, "matiere")

    weak_points = []
    strong_points = []
    recommendations = []

    for category, stats in by_category.items():
        avg = stats["average"]

        if avg < 25:
            weak_points.append(f"{category} est très faible")
            recommendations.append(f"Renforcer fortement {category}")
        elif avg < 35:
            weak_points.append(f"{category} est fragile")
            recommendations.append(f"Améliorer {category}")
        elif avg >= 42:
            strong_points.append(f"{category} est très solide")

    for mode, stats in by_mode.items():
        avg = stats["average"]
        if avg < 30:
            recommendations.append(f"Améliorer le mode {mode}")
        elif avg >= 43:
            strong_points.append(f"Le mode {mode} est excellent")

    return {
        "by_category": by_category,
        "by_mode": by_mode,
        "by_subject": by_subject,
        "weak_points": weak_points[:8],
        "strong_points": strong_points[:8],
        "recommendations": list(dict.fromkeys(recommendations))[:10]
    }

def run_test_case(test_case, mem, generate_answer_fn, judge_fn):
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
        "category": test_case["category"],
        "mode": test_case["mode"],
        "matiere": test_case["matiere"],
        "niveau": test_case["niveau"],
        "score": score,
        "preview": clean(ans)[:320]
    }

def build_test_suite(test_mode="quick"):
    if test_mode == "quick":
        return QUICK_TESTS
    if test_mode == "full":
        return FIXED_SHORT_TESTS + FIXED_LONG_TESTS + STRESS_TESTS + build_random_tests()
    raise ValueError(f"Mode de self-test inconnu : {test_mode}")

def self_test(load_memory_fn, save_memory_fn, generate_answer_fn, judge_fn, test_mode="quick"):
    mem = load_memory_fn()
    mem.setdefault("history", [])
    mem.setdefault("selftests", [])
    mem.setdefault("stats", {})

    all_tests = build_test_suite(test_mode=test_mode)
    results = []

    for t in all_tests:
        result = run_test_case(t, mem, generate_answer_fn, judge_fn)
        results.append(result)

        update_stats(mem, t["name"], result["score"].get("total", 0))

        mem["history"].append({
            "date": now_iso(),
            "test": t["name"],
            "category": t["category"],
            "score": result["score"].get("total", 0),
            "verdict": result["score"].get("verdict", ""),
            "hint": result["score"].get("improvement_hint", ""),
            "weakness": result["score"].get("main_weakness", "")
        })

    mem["history"] = mem["history"][-500:]

    diagnostics = build_selftest_diagnostics(results)

    mem["selftests"].append({
        "date": now_iso(),
        "mode": test_mode,
        "tests_count": len(all_tests),
        "results": results,
        "diagnostics": diagnostics
    })

    mem["selftests"] = mem["selftests"][-MAX_HISTORY_SELFTESTS:]

    save_memory_fn(mem)

    return {
        "results": results,
        "diagnostics": diagnostics
    }