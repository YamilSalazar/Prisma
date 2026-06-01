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

// Modales
document.addEventListener("click", (e) => {
  const openBtn = e.target.closest("[data-open-modal]");
  if (openBtn) {
    const overlay = document.getElementById(openBtn.dataset.openModal);
    if (overlay) overlay.classList.add("is-open");
    return;
  }
  const closeBtn = e.target.closest("[data-close-modal]");
  if (closeBtn) {
    const overlay = document.getElementById(closeBtn.dataset.closeModal);
    if (overlay) overlay.classList.remove("is-open");
    return;
  }
  if (e.target.classList.contains("modal-overlay")) {
    e.target.classList.remove("is-open");
  }
});

// Inline edit de campos en Mi Cuenta
document.addEventListener("click", (e) => {
  const editBtn = e.target.closest("[data-field-edit]");
  if (editBtn) {
    const row = editBtn.closest(".account-row");
    const valueEl = row.querySelector("[data-field-value]");
    const currentValue = valueEl.textContent.trim();

    const input = document.createElement("input");
    input.className = "account-row__input";
    input.value = currentValue;
    valueEl.replaceWith(input);
    input.focus();

    const actions = document.createElement("div");
    actions.className = "account-row__save-actions";
    actions.innerHTML = `
      <button class="button button--primary" data-field-save>
        <i class="ph ph-check" aria-hidden="true"></i> Guardar
      </button>
      <button class="button button--secondary" data-field-cancel data-original="${currentValue}">Cancelar</button>
    `;
    editBtn.replaceWith(actions);
    return;
  }

  const saveBtn = e.target.closest("[data-field-save]");
  if (saveBtn) {
    const row = saveBtn.closest(".account-row");
    const input = row.querySelector(".account-row__input");
    const newValue = input.value.trim() || input.value;

    const strong = document.createElement("strong");
    strong.setAttribute("data-field-value", "");
    strong.textContent = newValue;
    input.replaceWith(strong);

    const editBtn = document.createElement("button");
    editBtn.className = "account-row__edit-btn";
    editBtn.setAttribute("data-field-edit", "");
    editBtn.innerHTML = `<i class="ph ph-pencil-simple" aria-hidden="true"></i> Editar`;
    saveBtn.closest(".account-row__save-actions").replaceWith(editBtn);
    return;
  }

  const cancelBtn = e.target.closest("[data-field-cancel]");
  if (cancelBtn) {
    const row = cancelBtn.closest(".account-row");
    const input = row.querySelector(".account-row__input");
    const original = cancelBtn.dataset.original;

    const strong = document.createElement("strong");
    strong.setAttribute("data-field-value", "");
    strong.textContent = original;
    input.replaceWith(strong);

    const editBtn = document.createElement("button");
    editBtn.className = "account-row__edit-btn";
    editBtn.setAttribute("data-field-edit", "");
    editBtn.innerHTML = `<i class="ph ph-pencil-simple" aria-hidden="true"></i> Editar`;
    cancelBtn.closest(".account-row__save-actions").replaceWith(editBtn);
    return;
  }
});

// Limpiar filtros
const filterClearBtn = document.querySelector("[data-filter-clear]");
if (filterClearBtn) {
  filterClearBtn.addEventListener("click", (e) => {
    e.preventDefault();
    const panel = filterClearBtn.closest(".filters-panel");

    panel.querySelectorAll("input[type='radio']").forEach((radio) => {
      radio.checked = radio.hasAttribute("checked");
    });

    const [minInput, maxInput] = panel.querySelectorAll(".price-range input");
    if (minInput) minInput.value = "0";
    if (maxInput) maxInput.value = "2000";
  });
}

// Star picker
const starPicker = document.getElementById("star-picker");
if (starPicker) {
  const buttons = starPicker.querySelectorAll(".star-picker__btn");
  const hint = document.getElementById("star-hint");
  const submitBtn = document.getElementById("btn-enviar-resena");
  let selected = 0;

  const highlight = (upTo) => {
    buttons.forEach((b) => b.classList.toggle("is-active", parseInt(b.dataset.star) <= upTo));
  };

  buttons.forEach((btn) => {
    btn.addEventListener("mouseenter", () => highlight(parseInt(btn.dataset.star)));
    btn.addEventListener("mouseleave", () => highlight(selected));
    btn.addEventListener("click", () => {
      selected = parseInt(btn.dataset.star);
      highlight(selected);
      if (hint) hint.textContent = `${selected} de 5 estrellas`;
      if (submitBtn) submitBtn.disabled = false;
    });
  });
}

