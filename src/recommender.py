from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to int/float."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user_prefs using weighted proximity; return (score, reasons)."""
    score = 0.0
    reasons = []

    # --- Categorical matches (flat points) ---
    if song["genre"] == user_prefs.get("favorite_genre", ""):
        score += 2.0
        reasons.append(f"genre match (+2.0)")

    if song["mood"] == user_prefs.get("favorite_mood", ""):
        score += 1.5
        reasons.append(f"mood match (+1.5)")

    # --- Numeric proximity scores ---
    # proximity = 1.0 - abs(song_value - target_value), clamped to [0, 1]

    energy_prox = max(0.0, 1.0 - abs(song["energy"] - user_prefs.get("target_energy", 0.5)))
    energy_pts = round(energy_prox * 1.5, 2)
    score += energy_pts
    reasons.append(f"energy {song['energy']} vs target {user_prefs.get('target_energy', 0.5)} (+{energy_pts})")

    acousticness_prox = max(0.0, 1.0 - abs(song["acousticness"] - user_prefs.get("target_acousticness", 0.5)))
    acousticness_pts = round(acousticness_prox * 1.2, 2)
    score += acousticness_pts
    reasons.append(f"acousticness {song['acousticness']} vs target {user_prefs.get('target_acousticness', 0.5)} (+{acousticness_pts})")

    # Tempo uses a wider scale: divide gap by 100 to normalise
    tempo_prox = max(0.0, 1.0 - abs(song["tempo_bpm"] - user_prefs.get("target_tempo_bpm", 100.0)) / 100.0)
    tempo_pts = round(tempo_prox * 0.8, 2)
    score += tempo_pts
    reasons.append(f"tempo {song['tempo_bpm']} BPM vs target {user_prefs.get('target_tempo_bpm', 100.0)} (+{tempo_pts})")

    valence_prox = max(0.0, 1.0 - abs(song["valence"] - user_prefs.get("target_valence", 0.5)))
    valence_pts = round(valence_prox * 0.5, 2)
    score += valence_pts
    reasons.append(f"valence {song['valence']} vs target {user_prefs.get('target_valence', 0.5)} (+{valence_pts})")

    danceability_prox = max(0.0, 1.0 - abs(song["danceability"] - user_prefs.get("target_danceability", 0.5)))
    danceability_pts = round(danceability_prox * 0.4, 2)
    score += danceability_pts
    reasons.append(f"danceability {song['danceability']} vs target {user_prefs.get('target_danceability', 0.5)} (+{danceability_pts})")

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest to lowest, and return the top k as (song, score, explanation)."""
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        (song, score, ", ".join(reasons))
        for song, score, reasons in scored[:k]
    ]
