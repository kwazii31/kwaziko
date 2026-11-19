import subprocess
import random

FAVORITE_WORDS = ["tusnammmi", "supernova", "medkit", "hell", "guns", "fortnite"]

words = [
    "afk",
    "angry",
    "arise",
    "aura",
    "baby",
    "ballerina",
    "ban",
    "bankai",
    "bonk",
    "bruh",
    "chillguy",
    "chimpanzini",
    "crazy",
    "cry",
    "dad",
    "dance",
    "darkclone",
    "delete",
    "die",
    "dizzy",
    "domain",
    "energy_blast",
    "end",
    "error",
    "ez",
    "fall",
    "falling_blocks",
    "fart",
    "fly",
    "gg",
    "gojo",
    "gravity",
    "guest",
    "hero",
    "minecraft",
    "mrbeast",
    "naruto",
    "pikachu",
    "rizz",
    "saitama",
    "sans",
    "sigma",
    "skibidi",
    "speed",
    "spiderman",
    "teleport",
    "time_stop",
    "troll",
    "tung",
    "win",
    "wow",
    "backrooms",
    "castle",
    "city",
    "graveyard",
    "heaven",
    "hell",
    "hospital",
    "house",
    "mansion",
    "maze",
    "school",
    "space",
    "zoo",
    "cat",
    "dog",
    "dinosaur",
    "elephant",
    "frog",
    "monkey",
    "shark",
    "spider",
    "dragon",
    "ghost",
    "giant",
    "herobrine",
    "monster",
    "robot",
    "zombie",
    "volcano",
    "earthquake",
    "flood",
    "meteor",
    "tornado",
    "tsunami",
    "apocalypse",
    "lightning",
    "snow",
    "storm",
    "waterfall",
    "banana",
    "food",
    "tacos"
]

def copy_to_clipboard(text):
    try:
        subprocess.run(["clip"], input=text, text=True, check=True)
    except (OSError, subprocess.SubprocessError):
        print("Could not copy to the clipboard.")
    else:
        print("Copied to clipboard!")


def generate_word(label):
    while True:
        random_word = random.choice(words)
        print(f"\n{label}: {random_word}")

        while True:
            choice = input("Copy it? (y/n/r/e): ").strip().lower()
            if choice == "y":
                copy_to_clipboard(random_word)
                return False
            if choice == "n":
                print("Word not copied.")
                return False
            if choice == "r":
                break
            if choice == "e":
                return True
            print("Enter y to copy, n to skip, r to reroll, or e to exit.")


def show_favorite_words():
    while True:
        print("\nMy favorite words:")
        for number, word in enumerate(FAVORITE_WORDS, start=1):
            print(f"{number}. {word}")
        print("A. Copy all favorites")
        print("0. Return to menu")

        choice = input("Choose a word to copy: ").strip().lower()
        if choice == "0":
            return
        if choice == "a":
            copy_to_clipboard("\n".join(FAVORITE_WORDS))
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(FAVORITE_WORDS):
            copy_to_clipboard(FAVORITE_WORDS[int(choice) - 1])
            continue
        print("Please choose a listed number, A, or 0.")


def menu():
    while True:
        print("\n1. Generate random word")
        print("2. Generate a random word for Survive Your Ideas")
        print("3. View my favorite words")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            if generate_word("Random word"):
                return
        elif choice == "2":
            if generate_word("Word for Survive Your Ideas"):
                return
        elif choice == "3":
            show_favorite_words()
        elif choice == "4":
            print("Exiting...")
            return
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    menu()
