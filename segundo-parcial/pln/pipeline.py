import re
import unicodedata
from multilingual import traductor_global

SUPPORTED_INTENTS = {
    # Intents solicitados
    "find_games_with_crossplay": "sparql_crossplay",
    "find_openworld_mission_based": "sparql_openworld_mission",
    "find_local_coop_games": "sparql_local_coop",
    "find_simulation_pc_online_coop": "sparql_sim_pc_online_coop",
    "find_by_genre": "sparql_by_genre",
    "find_multiplayer_games": "sparql_multiplayer",
    "find_by_developer": "sparql_by_developer",
    "find_child_friendly": "sparql_child_friendly",
    "find_goty_by_release_year": "sparql_goty_by_year",
    "find_best_soundtrack_recent": "sparql_best_soundtrack_5y",
    "find_physical_and_digital_on_nextgen": "sparql_physical_digital_nextgen",
    "find_advanced_customization_non_linear": "sparql_customization_non_linear",
    "find_proprietary_engine_games": "sparql_proprietary_engine",
    "find_vr_ar_core": "sparql_vr_ar_core",
    "find_international_awards_recent": "sparql_international_awards_recent",
    "find_adaptive_ai_difficulty": "sparql_adaptive_ai",
    "find_educational_by_age": "sparql_educational_age",
    "find_sports_with_rpg_career_mode": "sparql_sports_rpg_career",
    "find_monetization_models": "sparql_monetization",
    "find_mod_support": "sparql_mod_support",
    "find_games_with_realistic_physics": "sparql_realistic_physics",
    "find_expansions_with_major_story_impact": "sparql_expansions_major_story",
    # Fallback genérico
    "find_games": "sparql_generic"
}

# Diccionarios de sinónimos -> claves de ontología
PLATFORM_MAP = {
    "pc": "vg:PC", "steam": "vg:PC", "windows": "vg:PC",
    "ps5": "vg:PS5", "ps4": "vg:PS4", "ps3": "vg:PS3", "playstation": "vg:PlayStation",
    "xbox": "vg:Xbox", "xboxone": "vg:XboxOne", "xboxseries": "vg:XboxSeries",
    "switch": "vg:Switch", "nintendo": "vg:Switch",
    "mobile": "vg:Mobile", "android": "vg:Mobile", "ios": "vg:Mobile"
}
GENRE_MAP = {
    "accion": "vg:Accion", "acción": "vg:Accion", "action": "vg:Accion",
    "aventura": "vg:Aventura", "rpg": "vg:RPG", "rol": "vg:RPG",
    "estrategia": "vg:Estrategia", "simulacion": "vg:Simulacion", "simulación": "vg:Simulacion",
    "deportes": "vg:Deportes", "educativo": "vg:Educativo"
}
MODE_MAP = {
    "multiplayer": "vg:Multiplayer", "multijugador": "vg:Multiplayer",
    "coop": "vg:CoopOnline", "cooperativo": "vg:CoopOnline",
    "cooponline": "vg:CoopOnline", "en linea": "vg:CoopOnline", "en línea": "vg:CoopOnline",
    "local": "vg:CoopLocal", "pantalla dividida": "vg:CoopLocal", "split": "vg:SplitScreen",
    "single": "vg:SinglePlayer", "un jugador": "vg:SinglePlayer"
}
AWARD_MAP = {
    "goty": "award:GOTY", "game of the year": "award:GOTY",
    "bso": "award:BestSoundtrack", "mejor banda sonora": "award:BestSoundtrack",
    "soundtrack": "award:BestSoundtrack",
    "narrativa": "award:Narrative", "direccion artistica": "award:ArtDirection",
    "dirección artística": "award:ArtDirection"
}
AGE_MAP = {
    "pegi3": "PEGI3", "pegi7": "PEGI7", "pegi12": "PEGI12", "pegi16": "PEGI16", "pegi18": "PEGI18",
    "e": "E", "e10": "E10+", "e10+": "E10+", "t": "T", "m": "M", "ao": "AO"
}

def _strip_accents(txt: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn")

def preprocess(text: str):
    original = text or ""
    clean = " ".join(original.strip().split())
    lowered = _strip_accents(clean.lower())
    idioma = traductor_global.detectar_idioma(original) if hasattr(traductor_global, "detectar_idioma") else "es"
    tokens = re.findall(r"[a-zA-Z0-9áéíóúüñÁÉÍÓÚÜÑ]+", clean)
    lemmas = [_strip_accents(t.lower()) for t in tokens]
    return {
        "original": original,
        "clean": clean,
        "lower": lowered,
        "tokens": tokens,
        "lemmas": lemmas,
        "idioma": idioma
    }

def classify_intent(pre):
    txt = pre["lower"]
    # Patrones específicos en orden de prioridad
    rules = [
        ("find_games_with_crossplay", [r"cross[- ]?play"]),
        ("find_openworld_mission_based", [r"mundo abierto", r"misiones"]),
        ("find_local_coop_games", [r"coop( local)?", r"pantalla dividida"]),
        ("find_simulation_pc_online_coop", [r"simul", r"\bpc\b", r"online", r"coop"]),
        ("find_by_genre", [r"genero", r"género", r"accion|acción|action|aventura|rpg|rol|estrategia|simul"]),
        ("find_multiplayer_games", [r"multijugador|multiplayer"]),
        ("find_by_developer", [r"desarrollador|studio|estudio|por "]),
        ("find_child_friendly", [r"niñ|infantil|pegi ?(3|7)|esrb ?e"]),
        ("find_goty_by_release_year", [r"goty|juego del anio|juego del año|game of the year"]),
        ("find_best_soundtrack_recent", [r"banda sonora|soundtrack"]),
        ("find_physical_and_digital_on_nextgen", [r"digital", r"fisic|físic", r"ps5|xbox series|switch"]),
        ("find_advanced_customization_non_linear", [r"personalizacion|personalización", r"no lineal|hub|sandbox"]),
        ("find_proprietary_engine_games", [r"motor propio|engine propietario|propietario"]),
        ("find_vr_ar_core", [r"\bvr\b|realidad virtual|\bar\b|realidad aumentada"]),
        ("find_international_awards_recent", [r"premio|award", r"narrativa|direccion artistica|dirección artística"]),
        ("find_adaptive_ai_difficulty", [r"ia adaptativa|ai adaptativa|dificultad dinamica|dinámica"]),
        ("find_educational_by_age", [r"educativo", r"edad"]),
        ("find_sports_with_rpg_career_mode", [r"deporte|futbol|fútbol|baloncesto|basket", r"carrera", r"rpg"]),
        ("find_monetization_models", [r"microtrans|dlc|season pass|pase de temporada"]),
        ("find_mod_support", [r"mods?|modding"]),
        ("find_games_with_realistic_physics", [r"fisica realista|física realista|physics"]),
        ("find_expansions_with_major_story_impact", [r"expansion|expansión|dlc", r"historia|trama|story"]),
    ]
    for intent, patterns in rules:
        if all(re.search(p, txt) for p in patterns):
            return intent, 0.85
        if any(re.search(p, txt) for p in patterns):
            # If partial match, keep but lower score
            return intent, 0.7
    # Fallbacks
    if "accion" in txt or "acción" in txt or "action" in txt:
        return "find_by_genre", 0.65
    if "multiplayer" in txt or "multijugador" in txt:
        return "find_multiplayer_games", 0.65
    return "find_games", 0.4

def extract_slots(pre):
    lemmas = pre["lemmas"]
    slots = {
        "platforms": [],
        "genres": [],
        "modes": [],
        "awards": [],
        "age_ratings": [],
        "year_range": None,
        "developer": None,
        "game_title": None,
        "bool_flags": set(),  # flags like openWorld, missionProgression, crossPlay, adaptiveAI
    }

    # Platforms
    for l in lemmas:
        if l in PLATFORM_MAP and PLATFORM_MAP[l] not in slots["platforms"]:
            slots["platforms"].append(PLATFORM_MAP[l])

    # Genres
    for l in lemmas:
        if l in GENRE_MAP and GENRE_MAP[l] not in slots["genres"]:
            slots["genres"].append(GENRE_MAP[l])

    # Modes
    for l in lemmas:
        if l in MODE_MAP and MODE_MAP[l] not in slots["modes"]:
            slots["modes"].append(MODE_MAP[l])

    # Awards / ratings
    for l in lemmas:
        if l in AWARD_MAP and AWARD_MAP[l] not in slots["awards"]:
            slots["awards"].append(AWARD_MAP[l])
        if l in AGE_MAP and AGE_MAP[l] not in slots["age_ratings"]:
            slots["age_ratings"].append(AGE_MAP[l])

    # Years (range)
    years = re.findall(r"\b(19|20)\d{2}\b", pre["lower"])
    if years:
        ys = [int(y) for y in years]
        slots["year_range"] = (min(ys), max(ys))

    # Developer (heurística: “por X”)
    m = re.search(r"por ([\w\s\.-]{2,50})", pre["clean"], flags=re.IGNORECASE)
    if m:
        slots["developer"] = m.group(1).strip()

    # Flags by keywords
    if "crossplay" in pre["lower"] or "cross-play" in pre["lower"]:
        slots["bool_flags"].add("supportsCrossPlay")
    if "mundo abierto" in pre["lower"] or "open world" in pre["lower"]:
        slots["bool_flags"].add("openWorld")
    if "mision" in pre["lower"] or "misión" in pre["lower"]:
        slots["bool_flags"].add("missionBased")
    if "personalizacion" in pre["lower"] or "personalización" in pre["lower"]:
        slots["bool_flags"].add("advancedCustomization")
    if "no lineal" in pre["lower"] or "non linear" in pre["lower"] or "hub" in pre["lower"]:
        slots["bool_flags"].add("nonLinearProgression")
    if "motor propio" in pre["lower"] or "engine propietario" in pre["lower"] or "propietario" in pre["lower"]:
        slots["bool_flags"].add("proprietaryEngine")
    if "vr" in pre["lower"] or "realidad virtual" in pre["lower"]:
        slots["bool_flags"].add("vrCore")
    if "ar" in pre["lower"] or "realidad aumentada" in pre["lower"]:
        slots["bool_flags"].add("arCore")
    if "ia adaptativa" in pre["lower"] or "ai adaptativa" in pre["lower"] or "dificultad dinamica" in pre["lower"] or "dinámica" in pre["lower"]:
        slots["bool_flags"].add("adaptiveAI")
    if "mods" in pre["lower"] or "modding" in pre["lower"]:
        slots["bool_flags"].add("modSupport")
    if "microtrans" in pre["lower"] or "dlc" in pre["lower"] or "season pass" in pre["lower"] or "pase de temporada" in pre["lower"]:
        slots["bool_flags"].add("monetization")

    # Game title heuristic: after "de " or quoted
    mtitle = re.search(r"\"(.+?)\"", pre["clean"])
    if mtitle:
        slots["game_title"] = mtitle.group(1)
    elif "de " in pre["clean"].lower():
        cand = pre["clean"].split("de ", 1)[-1].strip()
        if len(cand.split()) <= 6:
            slots["game_title"] = cand

    # Force Nintendo developer if mentioned
    if "nintendo" in pre["lower"]:
        slots["developer"] = "Nintendo"

    # Child friendly
    if any(x in pre["lower"] for x in ["niños", "ninos", "infantil", "pegi 3", "pegi 7", "e10", "e 10", "esrb e"]):
        slots["age_ratings"].extend([r for r in ["PEGI3", "PEGI7", "E", "E10+"] if r not in slots["age_ratings"]])

    return slots

def build_query_spec(intent, slots):
    """
    Retorna un dict con: intent, template, filters, idioma, needs_fallback(bool)
    """
    template = SUPPORTED_INTENTS.get(intent, "sparql_generic")
    filters = {
        "platforms": slots.get("platforms", []),
        "genres": slots.get("genres", []),
        "modes": slots.get("modes", []),
        "awards": slots.get("awards", []),
        "age_ratings": slots.get("age_ratings", []),
        "year_range": slots.get("year_range"),
        "developer": slots.get("developer"),
        "game_title": slots.get("game_title"),
        "bool_flags": list(slots.get("bool_flags", []))
    }

    # Intent-specific guardrails: ensure required filters
    if intent == "find_simulation_pc_online_coop":
        # enforce PC + genre Simulation + CoopOnline
        if "vg:PC" not in filters["platforms"]:
            filters["platforms"].append("vg:PC")
        if "vg:Simulacion" not in filters["genres"]:
            filters["genres"].append("vg:Simulacion")
        if "vg:CoopOnline" not in filters["modes"]:
            filters["modes"].append("vg:CoopOnline")

    if intent == "find_local_coop_games":
        if "vg:CoopLocal" not in filters["modes"]:
            filters["modes"].append("vg:CoopLocal")

    if intent == "find_multiplayer_games":
        if not filters["modes"]:
            filters["modes"] = ["vg:Multiplayer", "vg:CoopOnline", "vg:CoopLocal"]

    if intent == "find_by_genre" and not filters["genres"]:
        # default to Action if user asked generic “acción”
        filters["genres"].append("vg:Accion")

    # Mark fallback when critical slots missing for templates that need them
    needs_fallback = False
    critical = {
        "find_by_developer": ["developer"],
        "find_by_genre": ["genres"],
        "find_platforms_for_game": ["game_title"],
        "find_goty_by_release_year": [],  # optional, can run generic GOTY
    }
    required = critical.get(intent, [])
    for r in required:
        val = filters.get(r)
        if not val:
            needs_fallback = True
            break

    return {
        "intent": intent,
        "template": template,
        "filters": filters,
        "needs_fallback": needs_fallback
    }

def run_nlp(text: str):
    """
    Pipeline completo:
      1) preprocesa
      2) detecta intención
      3) extrae slots
      4) arma query spec
    """
    pre = preprocess(text)
    intent, score = classify_intent(pre)
    slots = extract_slots(pre)
    spec = build_query_spec(intent, slots)
    spec["confidence"] = score
    spec["lang"] = pre["idioma"]
    spec["original"] = pre["original"]
    return spec