
## Taste Profile Design

### Proposed Profile — "Chill Indie Pop" Listener

A user who enjoys melodic, moderately upbeat music for studying or casual listening; avoids aggressive or passive-extreme tracks.

```python
user_prefs = {
    "favorite_genre":    "indie pop",  # categorical
    "favorite_mood":     "chill",      # categorical
    "target_energy":     0.55,         # mid-range; avoids metal (0.96) and ambient (0.28)
    "target_valence":    0.72,         # bright but not euphoric
    "target_danceability": 0.65,       # moderately groovy
    "target_acousticness": 0.50,       # neutral — neither purely acoustic nor electronic
    "target_tempo_bpm":  95.0,         # moderate (~90–110 BPM sweet spot)
    "likes_acoustic":    False,        # leans electronic but not strongly
}
```

`UserProfile` dataclass needs matching fields: add `target_valence`, `target_danceability`, `target_acousticness`, `target_tempo_bpm`.

---

### Critique

**What it differentiates well:**
- "Shatter" (metal, angry, 0.96 energy, 168 BPM) → penalized hard on energy, tempo, genre, and mood
- "Midnight Coding" (lofi, chill, 0.42 energy) → mood matches but energy and genre penalize it
- "Rooftop Lights" (indie pop, happy, 0.76 energy) → genre match lifts it; energy 0.76 is closer to 0.55 than metal's 0.96

**Weaknesses to address during implementation:**
1. `likes_acoustic: bool` overlaps with `target_acousticness: float` — scoring should use the float and treat the bool as a soft flag or remove it
2. Genre/mood matching is binary (match or no-match) — no genre proximity (e.g., "indie pop" ≠ "metal" but "indie pop" ≈ "pop"). Consider a genre similarity map or partial-match bonus
3. `target_energy=0.55` places "Midnight Coding" (0.42) and "Golden Hour" r&b (0.58) close together despite being very different — genre + mood must carry that distinction

**Verdict:** Profile is expressive enough for extreme cases (intense vs. chill). For mid-range differentiation, scoring must combine all numeric features with weighted proximity — no single feature is sufficient alone.

---

## Scoring Algorithm Recipe

### Design Rationale (from data analysis on 20 songs)

| Feature | Observation | Impact on Weight |
|---|---|---|
| Genre | 15 unique genres; lofi=3, pop=2, rest=1 | Rare match → worth more |
| Mood | 17 unique moods; chill=3, intense=2, happy=2 | Slightly easier to hit → worth slightly less |
| Energy | Range 0.28–0.96, std dev 0.22 | Well-spread, strong discriminator |
| Tempo | Range 60–168 BPM, std dev 32 | Very spread; ~50% of songs near any target |
| Acousticness | Range 0.04–0.95, std dev 0.38, **bimodal** | Highest discriminating power |
| Valence | Range 0.31–0.87, std dev 0.15 | Clustered near mean — weaker discriminator |
| Danceability | Range 0.28–0.91, std dev 0.15 | Same as valence — weaker discriminator |

---

### Scoring Rules (per song)

**Categorical matches (flat points):**
```
genre match  → +2.0 pts   (rare; strong intent signal)
mood  match  → +1.5 pts   (slightly easier to hit than genre)
```

**Numeric proximity (each contributes 0.0–max pts based on closeness):**

Formula: `proximity = 1.0 - abs(song_value - target_value)`, clamped to [0, 1]
Tempo exception: `proximity = 1.0 - abs(song_bpm - target_bpm) / 100.0`, clamped to [0, 1]

```
energy       → proximity × 1.5   (well-spread, high signal)
acousticness → proximity × 1.2   (highest variance — bimodal)
tempo        → proximity × 0.8   (spread but ~50% of songs already score near any target)
valence      → proximity × 0.5   (clustered; weak discriminator)
danceability → proximity × 0.4   (same as valence)
```

**Max possible score: 2.0 + 1.5 + 1.5 + 1.2 + 0.8 + 0.5 + 0.4 = 7.9 pts**

---

### Walk-through: Two Contrasting Songs vs. "Chill Indie Pop" Profile

Profile targets: `genre="indie pop", mood="chill", energy=0.55, acousticness=0.50, tempo=95, valence=0.72, danceability=0.65`

| Component | "Shatter" (metal/angry) | "Rooftop Lights" (indie pop/happy) |
|---|---|---|
| Genre match | 0 | +2.0 |
| Mood match | 0 | 0 (happy ≠ chill) |
| Energy prox × 1.5 | (1-\|0.96-0.55\|)×1.5 = **0.89** | (1-\|0.76-0.55\|)×1.5 = **1.19** |
| Acousticness × 1.2 | (1-\|0.04-0.50\|)×1.2 = **0.65** | (1-\|0.35-0.50\|)×1.2 = **1.02** |
| Tempo × 0.8 | (1-73/100)×0.8 = **0.22** | (1-29/100)×0.8 = **0.57** |
| Valence × 0.5 | (1-\|0.31-0.72\|)×0.5 = **0.30** | (1-\|0.81-0.72\|)×0.5 = **0.46** |
| Danceability × 0.4 | (1-\|0.55-0.65\|)×0.4 = **0.36** | (1-\|0.82-0.65\|)×0.4 = **0.33** |
| **Total** | **2.42 / 7.9** | **5.57 / 7.9** |

Clear separation: "Rooftop Lights" scores more than double "Shatter". ✓

---

### Implementation Notes

- Clamp all proximity values to [0.0, 1.0] before multiplying by weight
- `likes_acoustic: bool` is superseded by `target_acousticness: float` — use float only, drop the bool
- Genre/mood use exact string match for now; genre similarity map is a future improvement
- Optionally normalize final score to [0, 1] by dividing by 7.9 for cleaner display

---
