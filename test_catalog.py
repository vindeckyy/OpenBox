from catalog import bulk_update, related_game_ids


def main():
    games = [
        {"name": "Alpha", "platform": "NES", "genre": "Action Adventure", "series": "Saga"},
        {"name": "Beta", "platform": "NES", "genre": "Action", "series": "Saga"},
        {"name": "Gamma", "platform": "PC", "genre": "Strategy"},
        {"name": "Hidden", "platform": "NES", "genre": "Action", "series": "Saga", "hidden": True},
    ]
    assert related_game_ids(games, 0) == [1]
    assert bulk_update(games, [0, 1, 1], {"progress": "Completed", "rating": 4.5, "favorite": True}) == 2
    assert games[1]["rating"] == 4.5 and games[0]["progress"] == "Completed"
    try:
        bulk_update(games, [0], {"rating": 6})
    except ValueError:
        pass
    else:
        raise AssertionError("invalid rating accepted")
    print("catalog self-test: ok")


if __name__ == "__main__":
    main()
