import random
import os

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

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def display(word, guessed, wrong_count):
    print(HANGMAN_STAGES[wrong_count])
    print()
    display_word = " ".join(c if c in guessed else "_" for c in word)
    print(f"  Ord:             {display_word}")
    wrong_letters = sorted(c for c in guessed if c not in word)
    print(f"  Fel bokstäver:   {', '.join(wrong_letters) if wrong_letters else '-'}")
    print(f"  Gissningar kvar: {6 - wrong_count}")
    print()

def play():
    while True:
        clear()
        print("╔══════════════════════════╗")
        print("║     HÄNGA GUBBEN 🎮      ║")
        print("╚══════════════════════════╝")
        print()

        word = random.choice(WORDS)
        guessed = set()
        wrong_count = 0

        while True:
            clear()
            print("╔══════════════════════════╗")
            print("║     HÄNGA GUBBEN 🎮      ║")
            print("╚══════════════════════════╝")
            display(word, guessed, wrong_count)

            if all(c in guessed for c in word):
                print(f"  GRATTIS! Du vann! Ordet var: {word.upper()}")
                break
            if wrong_count >= 6:
                print(f"  GAME OVER! Ordet var: {word.upper()}")
                break

            try:
                letter = input("  Gissa en bokstav: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n\n  Avslutar spelet. Hej då!")
                return

            if len(letter) != 1 or not letter.isalpha():
                print("  Ange exakt en bokstav!")
                input("  Tryck Enter för att fortsätta...")
                continue

            if letter in guessed:
                print(f"  Du har redan gissat '{letter}'!")
                input("  Tryck Enter för att fortsätta...")
                continue

            guessed.add(letter)
            if letter not in word:
                wrong_count += 1

        print()
        try:
            again = input("  Vill du spela igen? (j/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Hej då!")
            return

        if again != "j":
            print("\n  Tack för att du spelade! Hej då!")
            break

if __name__ == "__main__":
    play()
