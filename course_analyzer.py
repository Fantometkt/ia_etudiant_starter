from utils import *
from prompts import COURSE_ANALYSIS_PROMPT
from llm import call_ollama
from memory_manager import extract_focus_topics


COURSE_CACHE_FILE = "data/course_cache.json"

EMPTY_ANALYSIS = {
    "notions_centrales": [],
    "mots_cles": [],
    "liens_importants": [],
    "points_a_retenir": [],
    "angles_probables_examen": [],
    "erreurs_classiques": [],
    "zones_floues_ou_manquantes": [],
    "niveau_complexite": "",
    "structure_logique": [],
    "pre_requis": [],
    "questions_diagnostic": [],
    "besoin_enrichissement": "",
    "type_enrichissement_recommande": [],
    "limites_a_respecter": []
}


def load_course_cache():
    return load_json_file(COURSE_CACHE_FILE, {})


def save_course_cache(cache):
    save_json_file(COURSE_CACHE_FILE, cache)


def fallback_course_analysis(cours):
    text = clean(cours)

    if not text:
        return dict(EMPTY_ANALYSIS)

    topics = extract_focus_topics(text)

    return {
        **dict(EMPTY_ANALYSIS),
        "notions_centrales": topics[:5],
        "mots_cles": topics[:8],
        "points_a_retenir": topics[:5],
        "zones_floues_ou_manquantes": ["Analyse limitée : cours court ou modèle indisponible."],
        "niveau_complexite": "simple",
        "questions_diagnostic": [
            "Quelle est l’idée centrale du cours ?",
            "Quelle confusion faut-il éviter ?"
        ]
    }


def normalize_analysis(parsed):
    result = dict(EMPTY_ANALYSIS)

    if not isinstance(parsed, dict):
        return result

    for key in result:
        if key == "niveau_complexite":
            result[key] = clean(parsed.get(key))
        else:
            result[key] = [clean(x) for x in safe_list(parsed.get(key)) if clean(x)][:10]

    return result


def enrich_analysis_with_fallback(analysis, cours):
    if not analysis.get("notions_centrales"):
        topics = extract_focus_topics(cours)
        analysis["notions_centrales"] = topics[:5]
        analysis["mots_cles"] = topics[:8]

    if not analysis.get("questions_diagnostic"):
        notions = analysis.get("notions_centrales", [])[:3]
        analysis["questions_diagnostic"] = [
            f"Peux-tu expliquer la notion : {n} ?" for n in notions
        ] or ["Peux-tu reformuler l’idée principale du cours ?"]

    return analysis


def analyze_course(cours, niveau, matiere, force=False):
    cours_clean = clean(cours)

    if not cours_clean:
        return dict(EMPTY_ANALYSIS)

    key = sha_text(f"{niveau}|{matiere}|{cours_clean}")
    cache = load_course_cache()

    if not force and key in cache:
        return cache[key]

    prompt = f"""
Niveau : {niveau}
Matière : {matiere}

Cours :
{cours_clean}

Tu dois produire une analyse pédagogique complète.
Ajoute si possible :
- niveau_complexite : simple / intermediaire / difficile
- structure_logique
- pre_requis
- questions_diagnostic
""".strip()

    raw = call_ollama([
        {"role": "system", "content": COURSE_ANALYSIS_PROMPT},
        {"role": "user", "content": prompt}
    ], temp=0.0, max_tokens=1600)

    parsed = extract_json(raw)
    analysis = normalize_analysis(parsed)

    if not any(v for v in analysis.values() if v):
        analysis = fallback_course_analysis(cours_clean)

    analysis = enrich_analysis_with_fallback(analysis, cours_clean)

    cache[key] = analysis
    save_course_cache(cache)

    return analysis


def format_course_analysis(analysis):
    analysis = safe_dict(analysis)

    if not analysis:
        return "Aucune analyse de cours disponible."

    mapping = [
        ("niveau_complexite", "Niveau de complexité"),
        ("notions_centrales", "Notions centrales"),
        ("mots_cles", "Mots-clés"),
        ("structure_logique", "Structure logique"),
        ("liens_importants", "Liens importants"),
        ("pre_requis", "Pré-requis"),
        ("points_a_retenir", "Points à retenir"),
        ("angles_probables_examen", "Angles probables d’examen"),
        ("erreurs_classiques", "Erreurs classiques"),
        ("zones_floues_ou_manquantes", "Zones floues ou manquantes"),
        ("questions_diagnostic", "Questions diagnostic")
    ]

    lines = []

    for key, title in mapping:
        value = analysis.get(key)

        if not value:
            continue

        lines.append(f"{title} :")

        if isinstance(value, list):
            for item in value[:7]:
                lines.append(f"- {item}")
        else:
            lines.append(f"- {value}")

        lines.append("")

    return "\n".join(lines).strip()