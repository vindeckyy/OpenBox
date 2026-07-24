"""Library-level operations shared by the OpenBox interfaces."""

import re

PROGRESS = {"", "Playing", "Paused", "Beaten", "Completed", "Mastered", "Abandoned"}


def related_game_ids(games, selected, limit=8):
    """Return the strongest local-library relationships without an online service."""
    base = games[selected]
    base_genres = set(re.findall(r"\w+", str(base.get("genre", "")).lower()))
    ranked = []
    for index, game in enumerate(games):
        if index == selected or game.get("hidden"):
            continue
        genres = set(re.findall(r"\w+", str(game.get("genre", "")).lower()))
        score = 2 * len(base_genres & genres)
        score += 8 * bool(base.get("series") and base.get("series") == game.get("series"))
        score += 5 * bool(base.get("collection") and base.get("collection") == game.get("collection"))
        score += 3 * bool(base.get("developer") and base.get("developer") == game.get("developer"))
        score += 2 * bool(base.get("platform") and base.get("platform") == game.get("platform"))
        score += bool(base.get("publisher") and base.get("publisher") == game.get("publisher"))
        if score:
            ranked.append((-score, str(game.get("sort_title") or game.get("name", "")).casefold(), index))
    return [index for _, _, index in sorted(ranked)[:limit]]


def bulk_update(games, ids, changes):
    allowed = {"platform", "genre", "progress", "rating", "favorite", "hidden"}
    if not isinstance(ids, list) or not ids:
        raise ValueError("Select at least one game.")
    if not isinstance(changes, dict) or not changes or not set(changes) <= allowed:
        raise ValueError("No valid bulk changes were supplied.")
    clean = {}
    for field, value in changes.items():
        if field in {"favorite", "hidden"}:
            if not isinstance(value, bool):
                raise ValueError(f"{field.title()} must be true or false.")
            clean[field] = value
        elif field == "progress":
            if str(value) not in PROGRESS:
                raise ValueError("Unknown progress value.")
            clean[field] = str(value)
        elif field == "rating":
            rating = float(value)
            if not 0 <= rating <= 5:
                raise ValueError("Rating must be between 0 and 5.")
            clean[field] = rating
        else:
            clean[field] = str(value).strip()
    selected = sorted(set(int(index) for index in ids))
    if selected[0] < 0 or selected[-1] >= len(games):
        raise IndexError("A selected game no longer exists.")
    for index in selected:
        games[index].update(clean)
    return len(selected)
