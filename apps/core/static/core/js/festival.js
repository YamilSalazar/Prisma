document.querySelectorAll("[data-toggle-password]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.querySelector(button.dataset.togglePassword);
    if (!input) return;
    input.type = input.type === "password" ? "text" : "password";
  });
});

document.querySelectorAll("[data-accordion]").forEach((accordion) => {
  const button = accordion.querySelector(".accordion-card__head");
  const body = accordion.querySelector(".accordion-card__body");
  const caret = accordion.querySelector(".accordion-card__caret");
  if (!button || !body) return;

  button.addEventListener("click", () => {
    const expanded = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!expanded));
    body.hidden = expanded;
    if (caret) {
      caret.classList.toggle("ph-caret-up", !expanded);
      caret.classList.toggle("ph-caret-down", expanded);
    }
  });
});

document.querySelectorAll("[data-reservation-tab]").forEach((tab) => {
  tab.addEventListener("click", () => {
    const target = tab.dataset.reservationTab;
    document.querySelectorAll("[data-reservation-tab]").forEach((button) => {
      const active = button === tab;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-selected", String(active));
    });
    document.querySelectorAll("[data-reservation-panel]").forEach((panel) => {
      const active = panel.dataset.reservationPanel === target;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
    });
  });
});

