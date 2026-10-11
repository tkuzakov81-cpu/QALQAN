# QALQAN — Message Safety Lab

A local educational prototype that highlights possible warning signs in suspicious messages.

## Run on Windows

1. Install Python 3.11 or newer from https://www.python.org/downloads/
   - During installation, tick **Add Python to PATH**.
2. Extract this ZIP into a folder.
3. Open that folder in File Explorer.
4. Click the address bar, type `cmd`, and press Enter.
5. Run these commands:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Your browser should open the app. If it doesn't, copy the local URL shown in the terminal (usually http://localhost:8501) into your browser.

## What it does

- Applies transparent phrase-based rules to a message.
- Gives a heuristic warning score.
- Highlights detected phrases and explains each category.
- Includes Russian and Kazakh sample messages.
- Runs locally and does not send message text to an external API.

## Important limitation

This is a first prototype, not a definitive scam detector. A low score does not prove that a message is safe. Scores are heuristic and have not yet been calibrated on a representative dataset.

## Next development steps

1. Add a labelled evaluation dataset with benign and suspicious examples.
2. Measure precision, recall, F1 score, and false positives.
3. Compare the rule-based baseline with a simple machine-learning model.
4. Improve phrase matching for Russian and Kazakh morphology.
5. Add a results export and a polished project demo.
