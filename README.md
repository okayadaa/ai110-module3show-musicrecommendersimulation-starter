# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

- Changes on the weights (genre: 2.0 -> 0.5, mood: 1.0 -> 0.3, energy: 1.5 -> 0.2):
  Genre and mood was a dominating score but tweaking the values, there was a small change where energy and acoustic have real influence on the rankings. The concept behind it is that balanced weights is more diverse recommendations due to the reducing values of genre and mood dominance, the energy and other features establishes a compete fair. 

- Adding tempo or valence to the score:
  Based on the output, there are two new data points 'tempo' where song'ss beats per minute vs your target and 'valence' where song's musical presents positiveness. The results rely on actual musical characteristics like speed and mood vibe. Which leads the recommender to a more multi-dimensional

- System behavior for different types of users:
  The system recommends songs based on user's music preferences by the score of each songs. Genre and mood provide full points if it matches exactly. Energy, tempo, valence are based on closer to target (higher score). The system simply balances genre and mood preferences with audio features such as energy, tempo, and acoustic

---

## Limitations and Risks

--> energy_gap dominates ranking when the score rewards provide too much importance in user_energy - song_energy. Songs with the closest energy wins if it strongly favors small gap. Therefore, top results will continue being in the first 2-3 high energy songs. User will consistenly see the same energy (around 0.75 - 0.90) so discovery shrinks.

--> Mid energy users could be underserved in the dataset since energy is clustered low or high. With few mid energy songs may get weak or unstable matches

--> Extreme users can be treated unevenly if using a hard cutoff on energy gap. Low and high energy users could potentially lose candidates quickly  



---

## Reflection

Based on my analyzation for vibeFinder is the system collects data about users(what they like or behavior) and it observes patterns. It looks for connections of what songs users like or user's having similar music taste to other user's taste. Therefore, it establishes predictions and suggest a recommendation. The common problem areas is that there were popular bias where the system would recommend well knoen popular items because of the amount of data. Another common issue was the cold start where new users would have little data so the recommendations would be either poor or biased towards defaults. Lastly, one unfairness did appear with feedback loop. It's when popular recommendations get recommended more becoming extremely popular while other fade away.  

