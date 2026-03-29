from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

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

    # Optional refinements (backward-compatible with current tests)
    target_tempo_bpm: Optional[float] = None
    target_valence: Optional[float] = None
    target_danceability: Optional[float] = None
    target_acousticness: Optional[float] = None

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _proximity_score(value: float, target: float) -> float:
        """
        Returns a similarity score in [0, 1] where 1 means exact match
        and values decrease as distance from target grows.
        """
        return max(0.0, 1.0 - abs(value - target))

    def _score_song(self, user: UserProfile, song: Song) -> float:
        """
        Scores a song against user preferences.
        Uses proximity for numeric features so being closer is better.
        """
        score = 0.0
        total_weight = 0.0

        if song.genre.lower() == user.favorite_genre.lower():
            score += 0.5
        total_weight += 0.5

        if song.mood.lower() == user.favorite_mood.lower():
            score += 0.3
        total_weight += 0.3

        score += 0.20 * self._proximity_score(song.energy, user.target_energy)
        total_weight += 0.20

        acoustic_target = (
            user.target_acousticness
            if user.target_acousticness is not None
            else (1.0 if user.likes_acoustic else 0.0)
        )
        score += 0.10 * self._proximity_score(song.acousticness, acoustic_target)
        total_weight += 0.10

        if user.target_tempo_bpm is not None:
            # simple normalization from BPM distance to [0,1]
            tempo_sim = max(0.0, 1.0 - abs(song.tempo_bpm - user.target_tempo_bpm) / 200.0)
            score += 0.10 * tempo_sim
            total_weight += 0.10

        if user.target_valence is not None:
            score += 0.05 * self._proximity_score(song.valence, user.target_valence)
            total_weight += 0.05

        if user.target_danceability is not None:
            score += 0.05 * self._proximity_score(song.danceability, user.target_danceability)
            total_weight += 0.05

        return score / total_weight if total_weight > 0 else 0.0

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # Validate required inputs
        if not user.favorite_genre or not user.favorite_genre.strip():
            raise ValueError("favorite_genre cannot be blank")
        if not user.favorite_mood or not user.favorite_mood.strip():
            raise ValueError("favorite_mood cannot be blank")
        
        scored = [(song, self._score_song(user, song)) for song in self.songs]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons: List[str] = []

        if song.genre.lower() == user.favorite_genre.lower():
            reasons.append(f"genre matches your preference ({user.favorite_genre})")
        if song.mood.lower() == user.favorite_mood.lower():
            reasons.append(f"mood matches your preference ({user.favorite_mood})")

        energy_similarity = self._proximity_score(song.energy, user.target_energy)
        reasons.append(
            f"energy is close to your target ({song.energy:.2f} vs {user.target_energy:.2f}, similarity {energy_similarity:.2f})"
        )

        acoustic_target = 1.0 if user.likes_acoustic else 0.0
        acoustic_similarity = self._proximity_score(song.acousticness, acoustic_target)
        if user.likes_acoustic:
            reasons.append(
                f"acousticness aligns with your acoustic preference ({song.acousticness:.2f}, similarity {acoustic_similarity:.2f})"
            )
        else:
            reasons.append(
                f"lower acousticness aligns with your preference ({song.acousticness:.2f}, similarity {acoustic_similarity:.2f})"
            )

        return "; ".join(reasons)

def load_songs(path="data/songs.csv"):
    songs = []
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in float_fields:
                val = row.get(key)
                if val is None or val == "":
                    continue
                try:
                    row[key] = float(val)
                except ValueError:
                    pass
            songs.append(row)

    return songs


def _proximity_score(value: float, target: float) -> float:
    """Returns a distance-based similarity score in [0, 1]."""
    return max(0.0, 1.0 - abs(value - target))


def _normalize_text(value: object) -> str:
    """Normalizes user/song text fields for robust comparisons."""
    return str(value or "").strip().lower()


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamps numeric preferences to an expected range."""
    return max(low, min(high, value))


def score_song(user_prefs: Dict, song: Dict) -> float:
    """
        Scores a song dict using the catalog scoring rule:
        score = genre_match(+0.5)
                    + mood_match(+0.3)
                    + energy_proximity(up to +0.2)
                    + tempo_proximity(up to +0.15)
                    + valence_proximity(up to +0.1)
                    + acoustic_bonus/penalty(±0.5)
    """
    score = 0.0

    preferred_genre = _normalize_text(user_prefs.get("genre", ""))
    preferred_mood = _normalize_text(user_prefs.get("mood", ""))
    song_genre = _normalize_text(song.get("genre", ""))
    song_mood = _normalize_text(song.get("mood", ""))

    if preferred_genre and song_genre == preferred_genre:
        score += 0.5
    if preferred_mood and song_mood == preferred_mood:
        score += 0.3

    if "energy" in user_prefs and "energy" in song:
        user_energy = _clamp(float(user_prefs["energy"]))
        song_energy = _clamp(float(song["energy"]))
        score += 0.2 * _proximity_score(song_energy, user_energy)

    # Tempo scoring (default target 120 BPM)
    if "tempo_bpm" in song:
        user_tempo = float(user_prefs.get("tempo_bpm", 120.0))
        song_tempo = float(song.get("tempo_bpm", 0.0))
        tempo_sim = max(0.0, 1.0 - abs(song_tempo - user_tempo) / 200.0)
        score += 0.15 * tempo_sim

    # Valence scoring (default target 0.5 - neutral)
    if "valence" in song:
        user_valence = _clamp(float(user_prefs.get("valence", 0.5)))
        song_valence = _clamp(float(song.get("valence", 0.5)))
        score += 0.1 * _proximity_score(song_valence, user_valence)

    prefers_acoustic = bool(user_prefs.get("likes_acoustic", False))
    song_is_acoustic = float(song.get("acousticness", 0.0)) >= 0.5
    score += 0.5 if song_is_acoustic == prefers_acoustic else -0.5

    return score


def _score_song_dict(user_prefs: Dict, song: Dict) -> float:
    """Backward-compatible wrapper for starter implementations."""
    return score_song(user_prefs, song)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # Validate required inputs
    genre = _normalize_text(user_prefs.get("genre", ""))
    mood = _normalize_text(user_prefs.get("mood", ""))
    if not genre:
        raise ValueError("genre cannot be blank")
    if not mood:
        raise ValueError("mood cannot be blank")
    
    scored: List[Tuple[Dict, float, str]] = []
    user_energy = _clamp(float(user_prefs.get("energy", 0.0)))

    for song in songs:
        score = score_song(user_prefs, song)
        song_energy = _clamp(float(song.get("energy", 0.0)))
        song_tempo = float(song.get("tempo_bpm", 0.0))
        song_valence = _clamp(float(song.get("valence", 0.5)))
        user_tempo = float(user_prefs.get("tempo_bpm", 120.0))
        user_valence = _clamp(float(user_prefs.get("valence", 0.5)))
        
        explanation = (
            f"Genre: {song.get('genre')} | Mood: {song.get('mood')} | "
            f"Energy closeness: {_proximity_score(song_energy, user_energy):.2f} | "
            f"Tempo: {song_tempo:.0f}BPM (target {user_tempo:.0f}) | "
            f"Valence: {song_valence:.2f}"
        )
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
