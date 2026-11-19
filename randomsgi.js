const storageKey = "kwaziko-random-stuff";
const entryForm = document.querySelector("#entry-form");
const titleInput = document.querySelector("#entry-title");
const contentInput = document.querySelector("#entry-content");
const entryList = document.querySelector("#entry-list");
const entryCount = document.querySelector("#entry-count");
const emptyState = document.querySelector("#empty-state");
const saveStatus = document.querySelector("#save-status");

function loadEntries() {
  try {
    const savedEntries = JSON.parse(localStorage.getItem(storageKey) || "[]");
    if (!Array.isArray(savedEntries)) return [];
    return savedEntries.filter((entry) =>
      entry && typeof entry.id === "string" && typeof entry.content === "string"
    );
  } catch {
    saveStatus.textContent = "Saved items could not be loaded from this browser.";
    return [];
  }
}

let entries = loadEntries();

function saveEntries() {
  try {
    localStorage.setItem(storageKey, JSON.stringify(entries));
    saveStatus.textContent = "";
  } catch {
    saveStatus.textContent = "This browser could not save the latest changes.";
  }
}

function formatDate(timestamp) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(timestamp));
}

function renderEntries() {
  entryList.replaceChildren();
  entries.forEach((entry) => {
    const item = document.createElement("li");
    const header = document.createElement("div");
    const title = document.createElement("h3");
    const date = document.createElement("p");
    const content = document.createElement("p");
    const deleteButton = document.createElement("button");

    item.className = "entry-item";
    header.className = "entry-item-header";
    title.className = "entry-title";
    title.textContent = entry.title || "Untitled";
    date.className = "entry-date";
    date.textContent = formatDate(entry.createdAt);
    content.className = "entry-content";
    content.textContent = entry.content;
    deleteButton.className = "delete-button";
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.setAttribute("aria-label", `Delete ${entry.title || "untitled item"}`);
    deleteButton.addEventListener("click", () => {
      entries = entries.filter((savedEntry) => savedEntry.id !== entry.id);
      saveEntries();
      renderEntries();
    });

    header.append(title, deleteButton);
    item.append(header, date, content);
    entryList.append(item);
  });

  entryCount.textContent = `${entries.length} ${entries.length === 1 ? "item" : "items"}`;
  emptyState.hidden = entries.length > 0;
}

entryForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const content = contentInput.value.trim();
  if (!content) return;

  entries.unshift({
    id: globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`,
    title: titleInput.value.trim(),
    content,
    createdAt: Date.now()
  });
  saveEntries();
  renderEntries();
  entryForm.reset();
  contentInput.focus();
});

renderEntries();