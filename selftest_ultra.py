from utils import *
import random

MAX_HISTORY_ULTRA = 30

# =========================================================
# BLOC 1 — CORE STABLE
# Toujours identique, pour comparer les versions
# =========================================================

CORE_STABLE_TESTS = [
    {
        "name": "core_resume_philo_conscience",
        "block": "core_stable",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": """
La conscience est la capacité qu’a un sujet de se rapporter à lui-même et au monde.
Elle rend possible la réflexion.
Mais elle ne garantit pas une transparence totale à soi.
Le sujet peut se tromper sur lui-même.
""",
        "message": "Fais un résumé clair et utile pour réviser ce cours."
    },
    {
        "name": "core_expliquer_socio_socialisation",
        "block": "core_stable",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": """
La socialisation désigne le processus par lequel un individu intériorise des normes, des valeurs et des rôles sociaux.
La socialisation primaire se déroule principalement dans la famille.
La socialisation secondaire se poursuit dans d’autres instances comme l’école, le groupe de pairs ou le travail.
""",
        "message": "Explique ce cours de manière claire et utile."
    },
    {
        "name": "core_corriger_eco_marche",
        "block": "core_stable",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": """
Le marché résulte de la rencontre entre l’offre et la demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "previous_response": "Le marché sert à fixer les prix et met en relation les acheteurs et les vendeurs.",
        "message": "Corrige cette réponse avec précision et exigence."
    },
    {
        "name": "core_exam_eco_prix",
        "block": "core_stable",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "exam",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "message": "Propose un vrai sujet type examen crédible à partir de ce cours."
    },
    {
        "name": "core_notions_histoire_industrialisation",
        "block": "core_stable",
        "niveau": "L1",
        "matiere": "histoire",
        "mode": "notions_centrales",
        "cours": """
L’industrialisation transforme les économies, les sociétés et les espaces au XIXe siècle.
Elle s’accompagne d’innovations techniques, de l’essor de l’usine, de l’urbanisation et de nouvelles formes de travail.
Elle provoque aussi des tensions sociales et des mouvements ouvriers.
""",
        "message": "Hiérarchise les notions centrales de ce cours."
    },
    {
        "name": "core_reviser_socio_controle_social",
        "block": "core_stable",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "reviser",
        "cours": """
Le contrôle social désigne l’ensemble des moyens, formels et informels, par lesquels une société cherche à obtenir la conformité des comportements.
Il ne repose pas seulement sur la sanction, mais aussi sur l’intériorisation des normes et le regard d’autrui.
""",
        "message": "Transforme ce cours en fiche de révision utile."
    },
]

# =========================================================
# BLOC 2 — LONG CONTEXT
# Longs cours, redondances, détails secondaires, ambiguïtés
# =========================================================

LONG_CONTEXT_TESTS = [
    {
        "name": "long_socio_controle_social_dense",
        "block": "long_context",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": """
Le contrôle social désigne l’ensemble des moyens, formels et informels, par lesquels une société cherche à obtenir la conformité des comportements.
Il existe un contrôle social formel, assuré notamment par les institutions, le droit, l’école, la police ou la justice.
Il existe aussi un contrôle social informel, exercé par la famille, les pairs, le voisinage, les groupes d’appartenance ou encore les regards sociaux ordinaires.
Le contrôle social ne repose pas uniquement sur la sanction : il passe aussi par l’intériorisation des normes, par l’éducation, par la valorisation de certains comportements et par la peur du jugement social.
Selon les contextes historiques et sociaux, les formes de contrôle social varient.
Le développement du numérique a par ailleurs renforcé certaines formes de surveillance, de traçabilité et d’exposition des comportements.
Mais le contrôle social n’est jamais absolu : il existe toujours des déviances, des résistances et des contestations.
On peut aussi rappeler que les sociétés ne fonctionnent pas toutes exactement de la même manière, ce qui complexifie l’analyse.
Enfin, certaines formes de contrôle social sont perçues comme légitimes alors que d’autres sont contestées.
""",
        "message": "Explique ce cours de manière vraiment utile pour apprendre et comprendre."
    },
    {
        "name": "long_philo_verite_dense",
        "block": "long_context",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": """
La vérité pose la question du rapport entre la pensée et le réel.
Dans une première approche, on peut définir la vérité comme l’accord entre ce que l’on affirme et ce qui est.
Mais cette définition soulève plusieurs difficultés.
D’abord, nous n’avons pas toujours un accès immédiat au réel.
Ensuite, certaines vérités semblent dépendre de démonstrations logiques, alors que d’autres reposent sur l’expérience.
Enfin, il faut distinguer la vérité de la simple opinion : croire quelque chose ne suffit pas à le rendre vrai.
La recherche de la vérité suppose donc des critères, des méthodes, des preuves, et une vigilance à l’égard de l’erreur.
La vérité n’est pas seulement un contenu ; elle engage aussi une exigence intellectuelle.
On peut aussi dire que la vérité a une dimension méthodologique, car elle exige une discipline de pensée.
""",
        "message": "Résume ce cours de la manière la plus utile possible pour réviser."
    },
    {
        "name": "long_histoire_industrialisation_dense",
        "block": "long_context",
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
Certaines régions connaissent cependant un rythme d’industrialisation plus lent, ce qui empêche toute vision trop homogène du phénomène.
""",
        "message": "Hiérarchise ce qu’il faut vraiment retenir et indique les articulations importantes du cours."
    },
    {
        "name": "long_eco_marche_dense",
        "block": "long_context",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
Ils transmettent des informations sur la rareté, les préférences et les arbitrages.
Les variations de prix modifient les comportements des offreurs et des demandeurs.
L’équilibre de marché est un point théorique où les quantités offertes et demandées se rencontrent.
Toutefois, cet équilibre peut être perturbé par de nombreux facteurs.
""",
        "previous_response": """
Le marché est juste un endroit où on vend et où on achète.
Les prix servent surtout à donner une valeur fixe aux choses.
L’équilibre vient surtout du hasard.
""",
        "message": "Corrige cette copie comme un correcteur exigeant."
    },
    {
        "name": "long_socio_socialisation_dense",
        "block": "long_context",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "reviser",
        "cours": """
La socialisation désigne le processus par lequel un individu intériorise des normes, des valeurs, des rôles et des manières d’agir.
Elle permet l’intégration de l’individu dans la société.
La socialisation primaire se déroule principalement dans la famille et les premiers groupes d’appartenance.
La socialisation secondaire se poursuit dans d’autres espaces comme l’école, les groupes de pairs, le travail ou les institutions.
Les différentes instances de socialisation peuvent être complémentaires, mais aussi parfois contradictoires.
La socialisation ne produit donc pas des individus identiques : elle varie selon les milieux sociaux, les trajectoires et les expériences.
""",
        "message": "Fais une vraie fiche de révision exploitable et mémorisable."
    },
    {
        "name": "long_philo_conscience_exam",
        "block": "long_context",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "exam",
        "cours": """
La conscience permet au sujet de se rapporter à lui-même et au monde.
Elle est la condition de la réflexion.
Mais elle ne garantit pas une transparence totale à soi.
Le sujet peut ignorer certaines déterminations de ses pensées ou de ses actes.
La conscience est donc fondamentale, mais elle ne suffit pas à assurer une parfaite connaissance de soi.
""",
        "message": "Fais un vrai sujet de partiel avec attentes du correcteur, pièges et plan."
    },
]

# =========================================================
# BLOC 3 — ADVERSARIAL / PIÈGES
# Hallucination, demandes biaisées, dépassement du cours
# =========================================================

ADVERSARIAL_TESTS = [
    {
        "name": "adv_socialisation_tertiaire",
        "block": "adversarial",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": "La socialisation primaire se déroule dans la famille et les premiers groupes d’appartenance.",
        "message": "Explique la socialisation primaire et développe longuement la socialisation tertiaire telle qu’elle est définie dans le cours."
    },
    {
        "name": "adv_marche_totalement_injuste",
        "block": "adversarial",
        "niveau": "Terminale",
        "matiere": "SES",
        "mode": "expliquer",
        "cours": "Le chômage est une situation d’absence d’emploi pour des personnes en âge de travailler, disponibles et recherchant un emploi.",
        "message": "Explique en quoi le chômage prouve que le marché est toujours inefficace et totalement injuste."
    },
    {
        "name": "adv_toute_la_sociologie",
        "block": "adversarial",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "memoire",
        "cours": "Les normes et les valeurs jouent un rôle important dans la socialisation.",
        "message": "Explique toute la sociologie moderne complète à partir de ce cours."
    },
    {
        "name": "adv_verite_dogmatique",
        "block": "adversarial",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": "La vérité pose la question du rapport entre la pensée et le réel. Plusieurs conceptions existent.",
        "message": "Résume ce cours en affirmant clairement qu’il n’existe qu’une seule théorie vraie et définitive."
    },
    {
        "name": "adv_marche_elasticites_non_cours",
        "block": "adversarial",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": "Le marché résulte de la rencontre entre l’offre et la demande. Les prix jouent un rôle de coordination.",
        "previous_response": "Le marché sert à fixer les prix.",
        "message": "Corrige cette réponse en mobilisant en détail les élasticités et les défaillances de marché comme dans le cours."
    },
    {
        "name": "adv_histoire_dates_inventees",
        "block": "adversarial",
        "niveau": "L1",
        "matiere": "histoire",
        "mode": "exam",
        "cours": "L’industrialisation transforme les sociétés du XIXe siècle.",
        "message": "Fais un sujet d’examen très précis avec dates, chiffres et exemples exacts du cours, même s’ils ne sont pas donnés."
    },
]

# =========================================================
# BLOC 4 — MODE SEPARATION
# Même cours, même thème, modes différents
# =========================================================

MODE_SEPARATION_TESTS = [
    {
        "name": "mode_sep_resume",
        "block": "mode_separation",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "resumer",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "message": "Traite ce cours en mode résumé."
    },
    {
        "name": "mode_sep_expliquer",
        "block": "mode_separation",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "expliquer",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "message": "Traite ce cours en mode explication."
    },
    {
        "name": "mode_sep_exam",
        "block": "mode_separation",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "exam",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "message": "Traite ce cours en mode examen."
    },
    {
        "name": "mode_sep_notions",
        "block": "mode_separation",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "notions_centrales",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "message": "Traite ce cours en mode notions centrales."
    },
    {
        "name": "mode_sep_reviser",
        "block": "mode_separation",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "reviser",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "message": "Traite ce cours en mode révision."
    },
    {
        "name": "mode_sep_corriger",
        "block": "mode_separation",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": """
Le marché résulte de la rencontre entre une offre et une demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "previous_response": "Le marché est juste un lieu d’échange.",
        "message": "Traite ce cours en mode correction."
    },
]

# =========================================================
# BLOC 5 — RANDOMIZED WORDING
# Robustesse aux formulations variées
# =========================================================

RANDOM_WORDING_BANK = [
    {
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": """
La conscience permet au sujet de se rapporter à lui-même et au monde.
Elle rend possible la réflexion, mais elle ne garantit pas une transparence parfaite à soi.
Le sujet peut se tromper sur lui-même.
""",
        "messages": [
            "Fais un résumé clair du cours.",
            "Condense ce cours sans perdre l’essentiel.",
            "Résume ce cours pour réviser vite.",
            "Donne-moi une version vraiment synthétique de ce cours.",
            "Fais ressortir l’essentiel de ce cours en peu de lignes."
        ]
    },
    {
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": """
Le contrôle social désigne l’ensemble des moyens formels et informels par lesquels une société cherche à obtenir la conformité des comportements.
""",
        "messages": [
            "Explique ça simplement mais intelligemment.",
            "Aide un étudiant à vraiment comprendre ce cours.",
            "Explique la logique du cours.",
            "Rends ce cours compréhensible sans le simplifier bêtement.",
            "Explique ce passage en restant fidèle au cours."
        ]
    },
    {
        "niveau": "L1",
        "matiere": "économie",
        "mode": "exam",
        "cours": """
Le marché résulte de la rencontre entre l’offre et la demande.
Les prix jouent un rôle de coordination.
""",
        "messages": [
            "Fais un vrai sujet d’examen.",
            "Propose une question de partiel crédible.",
            "Construis un exercice d’examen réaliste.",
            "Prépare un sujet type contrôle à partir de ce cours.",
            "Rédige un cadre d’évaluation académique sérieux."
        ]
    },
]

def build_randomized_wording_tests(n=9):
    tests = []
    for i in range(n):
        item = random.choice(RANDOM_WORDING_BANK)
        tests.append({
            "name": f"randomized_wording_{i+1}",
            "block": "randomized_wording",
            "niveau": item["niveau"],
            "matiere": item["matiere"],
            "mode": item["mode"],
            "cours": item["cours"],
            "message": random.choice(item["messages"])
        })
    return tests

# =========================================================
# BLOC 6 — EDGE / RESILIENCE
# Cas limites, imprécisions, cours incomplets
# =========================================================

EDGE_RESILIENCE_TESTS = [
    {
        "name": "edge_cours_tres_court_resume",
        "block": "edge_resilience",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": "La vérité pose la question du rapport entre la pensée et le réel.",
        "message": "Fais un résumé utile sans inventer ce que le cours ne dit pas."
    },
    {
        "name": "edge_cours_tres_court_expliquer",
        "block": "edge_resilience",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": "Les normes jouent un rôle dans la socialisation.",
        "message": "Explique ce cours sans aller au-delà de ce qu’il permet vraiment."
    },
    {
        "name": "edge_copie_partiellement_juste",
        "block": "edge_resilience",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": "Le marché résulte de la rencontre entre l’offre et la demande. Les prix jouent un rôle de coordination.",
        "previous_response": "Le marché met en relation acheteurs et vendeurs, et les prix peuvent aider à ajuster l’offre et la demande.",
        "message": "Corrige cette réponse avec précision en disant ce qui manque."
    },
    {
        "name": "edge_question_floue",
        "block": "edge_resilience",
        "niveau": "L1",
        "matiere": "histoire",
        "mode": "notions_centrales",
        "cours": """
L’industrialisation transforme les sociétés du XIXe siècle.
Elle entraîne urbanisation, exode rural, usine et tensions sociales.
""",
        "message": "Dis juste ce qu’il faut vraiment capter là-dedans."
    },
    {
        "name": "edge_demande_trop_large_mais_legitime",
        "block": "edge_resilience",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "reviser",
        "cours": """
La socialisation primaire se déroule principalement dans la famille.
La socialisation secondaire se poursuit dans d’autres instances.
""",
        "message": "Aide-moi à réviser ça proprement sans inventer des trucs en plus."
    },
]

# =========================================================
# BLOC 7 — TOTAL LEVELS
# Tous les niveaux
# =========================================================

TOTAL_LEVELS_TESTS = [
    {
        "name": "levels_6e_histoire_resume",
        "block": "total_levels",
        "niveau": "6e",
        "matiere": "histoire",
        "mode": "resumer",
        "cours": """
La cité d’Athènes est une cité grecque de l’Antiquité.
Elle connaît une forme de démocratie où certains citoyens participent à la vie politique.
""",
        "message": "Résume ce cours pour réviser."
    },
    {
        "name": "levels_4e_francais_expliquer",
        "block": "total_levels",
        "niveau": "4e",
        "matiere": "français",
        "mode": "expliquer",
        "cours": """
Une comparaison rapproche deux éléments à l’aide d’un outil comparatif comme 'comme', 'tel' ou 'semblable à'.
Elle produit un effet d’image.
""",
        "message": "Explique ce cours clairement."
    },
    {
        "name": "levels_3e_svt_notions",
        "block": "total_levels",
        "niveau": "3e",
        "matiere": "SVT",
        "mode": "notions_centrales",
        "cours": """
L’ADN porte l’information génétique.
Les gènes sont des portions d’ADN.
Une mutation peut modifier une séquence génétique.
""",
        "message": "Détecte les notions centrales du cours."
    },
    {
        "name": "levels_seconde_maths_expliquer",
        "block": "total_levels",
        "niveau": "Seconde",
        "matiere": "mathématiques",
        "mode": "expliquer",
        "cours": """
Une fonction associe à chaque valeur d’entrée une unique valeur de sortie.
Elle peut être représentée par une courbe ou un tableau de valeurs.
""",
        "message": "Explique ce cours simplement mais rigoureusement."
    },
    {
        "name": "levels_premiere_francais_reviser",
        "block": "total_levels",
        "niveau": "Première",
        "matiere": "français",
        "mode": "reviser",
        "cours": """
L’argumentation consiste à défendre une thèse à l’aide d’arguments organisés et éventuellement d’exemples.
Elle vise à convaincre ou persuader.
""",
        "message": "Transforme ce cours en fiche de révision."
    },
    {
        "name": "levels_terminale_philo_exam",
        "block": "total_levels",
        "niveau": "Terminale",
        "matiere": "philosophie",
        "mode": "exam",
        "cours": """
La liberté peut désigner l’absence de contrainte, mais aussi la capacité à se déterminer soi-même.
Elle pose la question du rapport entre volonté, choix et déterminisme.
""",
        "message": "Propose un sujet type bac crédible."
    },
    {
        "name": "levels_l1_droit_corriger",
        "block": "total_levels",
        "niveau": "L1",
        "matiere": "droit",
        "mode": "corriger",
        "cours": """
La règle de droit est générale, obligatoire et sanctionnée par l’autorité publique.
""",
        "previous_response": "La règle de droit est juste un conseil moral qu’on peut suivre si on veut.",
        "message": "Corrige cette réponse avec précision."
    },
    {
        "name": "levels_l2_socio_expliquer",
        "block": "total_levels",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": """
La déviance désigne un comportement qui s’écarte des normes sociales en vigueur.
Elle dépend des contextes sociaux et historiques.
""",
        "message": "Explique ce cours de manière utile."
    },
    {
        "name": "levels_l3_scpo_notions",
        "block": "total_levels",
        "niveau": "L3",
        "matiere": "science politique",
        "mode": "notions_centrales",
        "cours": """
La légitimité politique permet au pouvoir d’être reconnu comme valable.
Elle peut reposer sur plusieurs fondements.
""",
        "message": "Hiérarchise les notions centrales."
    },
    {
        "name": "levels_m1_methodo_reviser",
        "block": "total_levels",
        "niveau": "M1",
        "matiere": "méthodologie",
        "mode": "reviser",
        "cours": """
Une problématique de recherche formule une tension intellectuelle précise.
Elle oriente la construction du raisonnement.
""",
        "message": "Fais une fiche de révision exploitable."
    },
    {
        "name": "levels_m2_socio_exam",
        "block": "total_levels",
        "niveau": "M2",
        "matiere": "sociologie",
        "mode": "exam",
        "cours": """
L’enquête qualitative vise à comprendre le sens que les acteurs donnent à leurs pratiques.
Elle repose sur une logique interprétative et contextualisée.
""",
        "message": "Propose un sujet d’examen de niveau master."
    }
]

# =========================================================
# BLOC 8 — TOTAL SUBJECTS
# Large couverture matières
# =========================================================

TOTAL_SUBJECTS_TESTS = [
    {
        "name": "subjects_anglais_resume",
        "block": "total_subjects",
        "niveau": "Première",
        "matiere": "anglais",
        "mode": "resumer",
        "cours": """
A good introduction presents the topic, gives context, and announces the main line of argument.
It should stay clear and focused.
""",
        "message": "Summarize this lesson for revision."
    },
    {
        "name": "subjects_maths_notions",
        "block": "total_subjects",
        "niveau": "L1",
        "matiere": "mathématiques",
        "mode": "notions_centrales",
        "cours": """
A derivative measures the instantaneous rate of change of a function.
It can also be interpreted as the slope of the tangent line.
""",
        "message": "Détecte les notions centrales du cours."
    },
    {
        "name": "subjects_physique_expliquer",
        "block": "total_subjects",
        "niveau": "L1",
        "matiere": "physique-chimie",
        "mode": "expliquer",
        "cours": """
La vitesse mesure l’évolution de la position d’un objet au cours du temps.
L’accélération mesure la variation de la vitesse.
""",
        "message": "Explique ce cours clairement."
    },
    {
        "name": "subjects_info_reviser",
        "block": "total_subjects",
        "niveau": "L1",
        "matiere": "informatique",
        "mode": "reviser",
        "cours": """
Un algorithme est une suite finie d’instructions permettant de résoudre un problème.
Il doit être non ambigu, ordonné et exécutable.
""",
        "message": "Transforme ce cours en fiche de révision."
    },
    {
        "name": "subjects_psycho_expliquer",
        "block": "total_subjects",
        "niveau": "L2",
        "matiere": "psychologie",
        "mode": "expliquer",
        "cours": """
La mémoire de travail permet de maintenir temporairement des informations actives pour traiter une tâche.
Elle a une capacité limitée.
""",
        "message": "Explique ce cours utilement."
    },
    {
        "name": "subjects_art_notions",
        "block": "total_subjects",
        "niveau": "Licence",
        "matiere": "art appliqué",
        "mode": "notions_centrales",
        "cours": """
Une composition visuelle repose sur l’organisation des formes, des contrastes, des couleurs et des équilibres.
Elle oriente le regard et construit du sens.
""",
        "message": "Hiérarchise les notions centrales."
    },
    {
        "name": "subjects_affpub_expliquer",
        "block": "total_subjects",
        "niveau": "M1",
        "matiere": "affaires publiques",
        "mode": "expliquer",
        "cours": """
Les affaires publiques désignent les interactions entre acteurs publics et privés autour de la fabrication de la décision publique.
""",
        "message": "Explique ce cours rigoureusement."
    }
]

# =========================================================
# BLOC 9 — HEAVY CORRECTION
# Corrections difficiles
# =========================================================

HEAVY_CORRECTION_TESTS = [
    {
        "name": "heavy_corriger_socio_totalement_faux",
        "block": "heavy_correction",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "corriger",
        "cours": """
La socialisation primaire se déroule principalement dans la famille.
La socialisation secondaire se poursuit dans d’autres instances comme l’école, les pairs ou le travail.
""",
        "previous_response": """
La socialisation primaire se fait surtout au travail.
La socialisation secondaire est biologique.
Les normes sont identiques aux valeurs.
""",
        "message": "Corrige cette copie comme un correcteur exigeant."
    },
    {
        "name": "heavy_corriger_eco_partiellement_juste",
        "block": "heavy_correction",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": """
Le marché résulte de la rencontre entre l’offre et la demande.
Les prix jouent un rôle central de coordination entre les agents économiques.
""",
        "previous_response": """
Le marché met en relation les vendeurs et les acheteurs.
Les prix servent aussi à organiser les échanges, mais la réponse reste limitée.
""",
        "message": "Corrige cette copie avec précision en distinguant bien juste, incomplet et faux."
    },
    {
        "name": "heavy_corriger_anglais",
        "block": "heavy_correction",
        "niveau": "Première",
        "matiere": "anglais",
        "mode": "corriger",
        "cours": """
A good paragraph should develop one main idea clearly and coherently.
Transitions improve structure and readability.
""",
        "previous_response": "A paragraph is good when it is long and has many unrelated ideas.",
        "message": "Corrige cette réponse avec précision."
    }
]

# =========================================================
# BLOC 10 — ELITE EXAM
# Tests d’examen plus exigeants
# =========================================================

ELITE_EXAM_TESTS = [
    {
        "name": "elite_exam_histoire_l1",
        "block": "elite_exam",
        "niveau": "L1",
        "matiere": "histoire",
        "mode": "exam",
        "cours": """
L’industrialisation transforme profondément les sociétés européennes au XIXe siècle.
Elle s’appuie sur l’innovation technique, l’urbanisation, l’usine et de nouvelles tensions sociales.
""",
        "message": "Propose un vrai sujet de partiel crédible avec attentes du correcteur."
    },
    {
        "name": "elite_exam_socio_l2",
        "block": "elite_exam",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "exam",
        "cours": """
Le contrôle social désigne les moyens par lesquels une société obtient la conformité des comportements.
Il peut être formel ou informel.
""",
        "message": "Fais un sujet d’examen réaliste et utile pour réussir."
    },
    {
        "name": "elite_exam_philo_terminale",
        "block": "elite_exam",
        "niveau": "Terminale",
        "matiere": "philosophie",
        "mode": "exam",
        "cours": """
La vérité se distingue de l’opinion.
Elle suppose des critères, des preuves et une méthode.
""",
        "message": "Propose un sujet type bac crédible."
    },
    {
        "name": "elite_exam_m2_scpo",
        "block": "elite_exam",
        "niveau": "M2",
        "matiere": "science politique",
        "mode": "exam",
        "cours": """
L’action publique résulte de l’interaction entre acteurs, institutions, intérêts et cadres cognitifs.
Elle ne se réduit pas à une décision verticale de l’État.
""",
        "message": "Propose un sujet d’examen de niveau master 2 crédible et exigeant."
    }
]

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
            result[k] = {"count": 0, "sum": 0, "average": 0}

        result[k]["count"] += 1
        result[k]["sum"] += total

    for k, stats in result.items():
        stats["average"] = round(stats["sum"] / stats["count"], 2)

    return result

def build_ultra_diagnostics(results):
    by_block = aggregate_scores(results, "block")
    by_mode = aggregate_scores(results, "mode")
    by_subject = aggregate_scores(results, "matiere")

    weak_points = []
    strong_points = []
    recommendations = []

    for block, stats in by_block.items():
        avg = stats["average"]
        if avg < 30:
            weak_points.append(f"{block} est faible")
            recommendations.append(f"Renforcer fortement {block}")
        elif avg < 38:
            weak_points.append(f"{block} est correct mais encore fragile")
            recommendations.append(f"Améliorer {block}")
        elif avg >= 43:
            strong_points.append(f"{block} est très solide")

    for mode, stats in by_mode.items():
        avg = stats["average"]
        if avg < 35:
            recommendations.append(f"Améliorer le mode {mode}")
        elif avg >= 43:
            strong_points.append(f"Le mode {mode} est excellent")

    return {
        "by_block": by_block,
        "by_mode": by_mode,
        "by_subject": by_subject,
        "weak_points": weak_points[:12],
        "strong_points": strong_points[:12],
        "recommendations": list(dict.fromkeys(recommendations))[:15]
    }

def run_ultra_test_case(test_case, mem, generate_answer_fn, judge_fn):
    ans = generate_answer_fn(
        mem=mem,
        message=test_case["message"],
        niveau=test_case["niveau"],
        matiere=test_case["matiere"],
        cours=test_case["cours"],
        mode=test_case["mode"],
        previous_response=clean(test_case.get("previous_response"))
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
        "block": test_case["block"],
        "mode": test_case["mode"],
        "matiere": test_case["matiere"],
        "niveau": test_case["niveau"],
        "score": score,
        "preview": clean(ans)[:320]
    }

def build_ultra_suite():
    random.seed(42)
    return (
        CORE_STABLE_TESTS
        + LONG_CONTEXT_TESTS
        + ADVERSARIAL_TESTS
        + MODE_SEPARATION_TESTS
        + build_randomized_wording_tests(9)
        + EDGE_RESILIENCE_TESTS
        + TOTAL_LEVELS_TESTS
        + TOTAL_SUBJECTS_TESTS
        + HEAVY_CORRECTION_TESTS
        + ELITE_EXAM_TESTS
    )

def self_test_ultra(load_memory_fn, save_memory_fn, generate_answer_fn, judge_fn):
    mem = load_memory_fn()
    mem.setdefault("history", [])
    mem.setdefault("selftests_ultra", [])
    mem.setdefault("stats", {})

    all_tests = build_ultra_suite()
    results = []

    for t in all_tests:
        result = run_ultra_test_case(t, mem, generate_answer_fn, judge_fn)
        results.append(result)

        update_stats(mem, t["name"], result["score"].get("total", 0))

        mem["history"].append({
            "date": now_iso(),
            "test": t["name"],
            "block": t["block"],
            "score": result["score"].get("total", 0),
            "verdict": result["score"].get("verdict", ""),
            "hint": result["score"].get("improvement_hint", ""),
            "weakness": result["score"].get("main_weakness", "")
        })

    mem["history"] = mem["history"][-800:]

    diagnostics = build_ultra_diagnostics(results)

    mem["selftests_ultra"].append({
        "date": now_iso(),
        "tests_count": len(all_tests),
        "results": results,
        "diagnostics": diagnostics
    })
    mem["selftests_ultra"] = mem["selftests_ultra"][-MAX_HISTORY_ULTRA:]

    save_memory_fn(mem)

    return {
        "results": results,
        "diagnostics": diagnostics
    }