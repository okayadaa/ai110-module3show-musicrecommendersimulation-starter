"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    standard_profiles = {
        "High-Energy Pop": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.90,
            "likes_acoustic": False,
        },
        "Chill Lofi": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.30,
            "likes_acoustic": True,
        },
        "Deep Intense Rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.85,
            "likes_acoustic": False,
        },
    }

    adversarial_profiles = {
        "Adversarial: Out-of-Range Energy": {
            "genre": "pop",
            "mood": "chill",
            "energy": 1.80,
            "likes_acoustic": False,
        },
        "Edge Case: Blank Genre/Mood": {
            "genre": "",
            "mood": "",
            "energy": 0.60,
            "likes_acoustic": True,
        },
    }

    all_profiles = {**standard_profiles, **adversarial_profiles}

    for profile_name, user_prefs in all_profiles.items():
        print(f"\n=== {profile_name} ===")
        try:
            recommendations = recommend_songs(user_prefs, songs, k=5)
            print("Top 5 recommendations:\n")
            for song, score, explanation in recommendations:
                print(f"{song['title']} - Score: {score:.2f}")
                print(f"Elaboration: {explanation}")
                print()
        except ValueError as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
