import random
import json
import sys
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "game_state.json")

WORDS = [
    "python", "dator", "programmering", "tangentbord", "skärm",
    "algoritm", "variabel", "funktion", "loop", "lista",
    "robot", "nätverk", "databas", "terminal", "linux"
]

STAGES = [
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

def show(state):
    word = state["word"]
    guessed = set(state["guessed"])
    wrong = state["wrong"]
    print(STAGES[wrong])
    display = " ".join(c if c in guessed else "_" for c in word)
    print(f"  Ord:             {display}")
    wrong_letters = sorted(c for c in guessed if c not in word)
    print(f"  Fel bokstäver:   {', '.join(wrong_letters) if wrong_letters else '-'}")
    print(f"  Gissningar kvar: {6 - wrong}\n")

def new_game():
    state = {"word": random.choice(WORDS), "guessed": [], "wrong": 0, "status": "playing"}
    json.dump(state, open(STATE_FILE, "w"))
    print("\n=== HÄNGA GUBBEN ===\n")
    show(state)

def guess(letter):
    if not os.path.exists(STATE_FILE):
        print("Inget spel igång. Starta med: python hangman.py ny")
        return
    state = json.load(open(STATE_FILE))
    if state["status"] != "playing":
        print("Spelet är slut. Starta nytt med: python hangman.py ny")
        return
    letter = letter.lower()
    if len(letter) != 1 or not letter.isalpha():
        print("Ange exakt en bokstav!")
        return
    if letter in state["guessed"]:
        print(f"'{letter}' är redan gissad!\n")
        show(state)
        return
    state["guessed"].append(letter)
    if letter not in state["word"]:
        state["wrong"] += 1
    if all(c in set(state["guessed"]) for c in state["word"]):
        state["status"] = "won"
    elif state["wrong"] >= 6:
        state["status"] = "lost"
    json.dump(state, open(STATE_FILE, "w"))
    show(state)
    if state["status"] == "won":
        print(f"  GRATTIS! Du vann! Ordet var: {state['word'].upper()}")
    elif state["status"] == "lost":
        print(f"  GAME OVER! Ordet var: {state['word'].upper()}")

def interactive():
    while True:
        os.system("clear")
        print("=== HÄNGA GUBBEN ===\n")
        word = random.choice(WORDS)
        guessed = set()
        wrong = 0
        status = "playing"
        while status == "playing":
            os.system("clear")
            print("=== HÄNGA GUBBEN ===\n")
            state = {"word": word, "guessed": list(guessed), "wrong": wrong}
            show(state)
            if all(c in guessed for c in word):
                print(f"  GRATTIS! Du vann! Ordet var: {word.upper()}")
                status = "won"
                break
            if wrong >= 6:
                print(f"  GAME OVER! Ordet var: {word.upper()}")
                status = "lost"
                break
            try:
                letter = input("  Gissa en bokstav: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n  Hej då!")
                return
            if len(letter) != 1 or not letter.isalpha():
                continue
            if letter in guessed:
                continue
            guessed.add(letter)
            if letter not in word:
                wrong += 1
        try:
            again = input("\n  Spela igen? (j/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Hej då!")
            return
        if again != "j":
            print("  Hej då!")
            break

if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive()
    elif sys.argv[1] == "ny":
        new_game()
    elif sys.argv[1] == "gissa" and len(sys.argv) == 3:
        guess(sys.argv[2])
    else:
        print("Användning:")
        print("  python hangman.py          → Interaktivt (kör lokalt)")
        print("  python hangman.py ny       → Nytt spel (via chatt)")
        print("  python hangman.py gissa a  → Gissa bokstav (via chatt)")
