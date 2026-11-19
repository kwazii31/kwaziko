function startTypewriterAnimations() {
  document.querySelectorAll(".typewriter, .typewriter-line").forEach((element) => {
    const characterCount = Array.from(element.textContent.trim()).length;
    const availableWidth = element.parentElement?.clientWidth || element.scrollWidth;

    element.style.whiteSpace = "nowrap";
    const textWidth = element.scrollWidth + 2;
    element.style.removeProperty("white-space");

    element.style.setProperty("--typing-steps", characterCount);
    element.style.setProperty("--typing-width", `${Math.min(textWidth, availableWidth)}px`);
    element.classList.add("is-typing");
  });
}

if (document.fonts?.ready) {
  document.fonts.ready.then(startTypewriterAnimations);
} else {
  startTypewriterAnimations();
}