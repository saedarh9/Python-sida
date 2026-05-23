import json
import random
import sys
import os

STATE_FILE = "game_state.json"

WORDS = [
    "python", "dator", "programmering", "tangentbord", "skärm",
    "algoritm", "variabel", "funktion", "loop", "lista",
    "robot", "nätverk", "databas", "terminal", "linux"
]

HANGMAN_STAGES = [
    """
  +---+
  |   |
      |
      |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
========="""
]

def display_state(state):
    wrong = state["wrong_guesses"]
    print(HANGMAN_STAGES[wrong])
    print()
    word = state["word"]
    guessed = set(state["guessed_letters"])
    display = " ".join(c if c in guessed else "_" for c in word)
    print(f"  Ord: {display}")
    print()
    wrong_letters = [c for c in state["guessed_letters"] if c not in word]
    print(f"  Fel bokstäver: {', '.join(wrong_letters) if wrong_letters else '-'}")
    print(f"  Gissningar kvar: {6 - wrong}")
    print()

def start_game():
    word = random.choice(WORDS)
    state = {
        "word": word,
        "guessed_letters": [],
        "wrong_guesses": 0,
        "status": "playing"
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
    print("=== HÄNGA GUBBEN ===")
    print("Nytt spel startat! Gissa en bokstav i taget.\n")
    display_state(state)

def guess(letter):
    if not os.path.exists(STATE_FILE):
        print("Inget aktivt spel. Starta ett nytt spel.")
        return

    with open(STATE_FILE) as f:
        state = json.load(f)

    if state["status"] != "playing":
        print("Spelet är slut. Starta ett nytt spel.")
        return

    letter = letter.lower()

    if len(letter) != 1 or not letter.isalpha():
        print("Ange exakt en bokstav!")
        return

    if letter in state["guessed_letters"]:
        print(f"Du har redan gissat '{letter}'!")
        display_state(state)
        return

    state["guessed_letters"].append(letter)

    if letter not in state["word"]:
        state["wrong_guesses"] += 1

    word = state["word"]
    guessed = set(state["guessed_letters"])

    if all(c in guessed for c in word):
        state["status"] = "won"
    elif state["wrong_guesses"] >= 6:
        state["status"] = "lost"

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

    display_state(state)

    if state["status"] == "won":
        print(f"  GRATTIS! Du gissade rätt! Ordet var: {word.upper()}")
    elif state["status"] == "lost":
        print(HANGMAN_STAGES[6])
        print(f"  GAME OVER! Ordet var: {word.upper()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Användning: python hangman.py start | python hangman.py guess <bokstav>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "start":
        start_game()
    elif cmd == "guess" and len(sys.argv) == 3:
        guess(sys.argv[2])
    else:
        print("Okänt kommando.")
