"""
Command line runner for the Music Recommender Simulation.
"""

from recommender import load_songs, recommend_songs


USER_PREFS = {
    "favorite_genre":      "indie pop",
    "favorite_mood":       "chill",
    "target_energy":       0.55,
    "target_valence":      0.72,
    "target_danceability": 0.65,
    "target_acousticness": 0.50,
    "target_tempo_bpm":    95.0,
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    recommendations = recommend_songs(USER_PREFS, songs, k=5)

    print("\n" + "=" * 52)
    print("  Top 5 Recommendations")
    print("=" * 52)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  ({song['artist']})")
        print(f"    Score : {score:.2f} / 7.9")
        print(f"    Genre : {song['genre']}   Mood : {song['mood']}")
        print("    Why   :")
        for reason in explanation.split(", "):
            print(f"      - {reason}")

    print("\n" + "=" * 52 + "\n")


if __name__ == "__main__":
    main()
