const defaultPhrases = ["wsg gang", "im a gamer ", "im a html dev and py dev", "how do i fly again?", "wait what?..", "vs code on the TOP", "i want a domainnnnnn", "To be or not to be", "ai is getting to good bro", "wsh wh hw hq3q  qqedeqqQQUDGEUHFJDW9U8UHUQYB", "IDK WHAT TO SAY", "I want to learn hacks bruh", "alr im done it bouta reset", "Need any more funny quotes, just let me know😄👊", "haha gotchu lol u thoght that was chatgpt"];
const phraseOutput = document.querySelector("#phrase-output");
const phraseForm = document.querySelector("#phrase-form");
const phraseInput = document.querySelector("#phrase-input");
const phraseStorageKey = "kwaziko-typewriter-phrases";
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let phrases = defaultPhrases;
let phraseIndex = 0;
let characterIndex = 0;
let isDeleting = false;
let phraseTimer;

try {
  const savedPhrases = JSON.parse(localStorage.getItem(phraseStorageKey));
  if (Array.isArray(savedPhrases)) {
    phrases = savedPhrases.filter((phrase) =>
      typeof phrase === "string" && phrase.trim() && phrase.trim().toLowerCase() !== "max type car"
    );
  }
} catch {
  phrases = defaultPhrases;
}

if (phrases.length === 0) phrases = defaultPhrases;

function cyclePhrase() {
  const characters = Array.from(phrases[phraseIndex]);

  if (prefersReducedMotion) {
    phraseOutput.textContent = characters.join("");
    phraseIndex = (phraseIndex + 1) % phrases.length;
    phraseTimer = setTimeout(cyclePhrase, 2200);
    return;
  }

  characterIndex += isDeleting ? -1 : 1;
  phraseOutput.textContent = characters.slice(0, characterIndex).join("");

  if (!isDeleting && characterIndex === characters.length) {
    isDeleting = true;
    phraseTimer = setTimeout(cyclePhrase, 1100);
    return;
  }

  if (isDeleting && characterIndex === 0) {
    isDeleting = false;
    phraseIndex = (phraseIndex + 1) % phrases.length;
    phraseTimer = setTimeout(cyclePhrase, 250);
    return;
  }

  phraseTimer = setTimeout(cyclePhrase, isDeleting ? 38 : 82);
}

function startPhrase(index) {
  clearTimeout(phraseTimer);
  phraseIndex = index;
  characterIndex = 0;
  isDeleting = false;
  phraseOutput.textContent = "";
  cyclePhrase();
}

if (phraseForm && phraseInput) {
  phraseForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const phrase = phraseInput.value.trim();
    if (!phrase) return;

    phrases.push(phrase);
    try {
      localStorage.setItem(phraseStorageKey, JSON.stringify(phrases));
    } catch {
      // The phrase remains available for the current page if storage is unavailable.
    }
    startPhrase(phrases.length - 1);
    phraseInput.value = "";
    phraseInput.focus();
  });
}

startPhrase(0);

const tabButtons = Array.from(document.querySelectorAll('[role="tab"]'));
const tabPanels = Array.from(document.querySelectorAll('[role="tabpanel"]'));

function selectTab(selectedButton, moveFocus = false) {
  tabButtons.forEach((button, index) => {
    const isSelected = button === selectedButton;
    button.setAttribute("aria-selected", String(isSelected));
    button.tabIndex = isSelected ? 0 : -1;
    tabPanels[index].hidden = !isSelected;
  });
  if (moveFocus) selectedButton.focus();
}

tabButtons.forEach((button, index) => {
  button.addEventListener("click", () => selectTab(button));
  button.addEventListener("keydown", (event) => {
    let nextIndex = index;
    if (event.key === "ArrowRight") nextIndex = (index + 1) % tabButtons.length;
    else if (event.key === "ArrowLeft") nextIndex = (index - 1 + tabButtons.length) % tabButtons.length;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = tabButtons.length - 1;
    else return;
    event.preventDefault();
    selectTab(tabButtons[nextIndex], true);
  });
});

