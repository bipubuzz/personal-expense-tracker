// ============================================
//  PERSONAL EXPENSE TRACKER - MAIN SCRIPT
// ============================================
// This file contains all client-side JavaScript functionality
// organized into clear sections for maintainability

// ============================================
// SECTION 1: UTILITY FUNCTIONS
// ============================================

/**
 * Resets the expense form to "Add" mode
 * Restores original form action, title, and button text
 */
function resetFormToAddMode() {
  const form = document.getElementById("add-expense-form");
  const title = document.getElementById("popup-title");
  const submitBtn = document.getElementById("add-expense-submit-btn");

  if (form) {
    const originalAction = form.getAttribute("data-add-action");
    if (originalAction) {
      form.action = originalAction;
    }
    form.reset();
  }

  if (title) {
    title.textContent = "Add New Expense";
  }

  if (submitBtn) {
    submitBtn.textContent = "Add Expense";
  }
}

// ============================================
// SECTION 2: POPUP MANAGEMENT
// ============================================

/**
 * Opens the Add/Edit Expense popup
 */
function openPopup() {
  const popup = document.getElementById("popup");
  const overlay = document.querySelector(".popup-overlay");

  if (popup && overlay) {
    popup.classList.add("show");
    overlay.classList.add("show");
  }
}

/**
 * Closes the popup and resets form to Add mode
 */
function closePopup() {
  const popup = document.getElementById("popup");
  const overlay = document.querySelector(".popup-overlay");

  if (popup && overlay) {
    popup.classList.remove("show");
    overlay.classList.remove("show");
  }

  resetFormToAddMode();
}

// --- Popup Event Listeners ---

// Open popup when "Add Expense" button is clicked
document
  .getElementById("add-expense-btn")
  ?.addEventListener("click", function () {
    resetFormToAddMode();
    openPopup();
  });

// Close popup when "X" button is clicked
document
  .getElementById("add-expense-exit-btn")
  ?.addEventListener("click", function () {
    closePopup();
  });

// Close popup when clicking on the overlay backdrop
document
  .querySelector(".popup-overlay")
  ?.addEventListener("click", function () {
    closePopup();
  });

// ============================================
// SECTION 3: EDIT EXPENSE FUNCTIONALITY
// ============================================

/**
 * Populates the form with existing expense data for editing
 * Uses event delegation to handle dynamically loaded expense cards
 */
document.addEventListener("click", function (e) {
  // Check if an edit button was clicked
  const editBtn = e.target.closest && e.target.closest(".edit-btn");
  if (!editBtn) return;

  e.preventDefault();

  // Extract expense data from button attributes
  const id = editBtn.getAttribute("data-id");
  const amount = editBtn.getAttribute("data-amount");
  const category = editBtn.getAttribute("data-category");
  const description = editBtn.getAttribute("data-description");
  const date = editBtn.getAttribute("data-date");

  // Populate form fields with expense data
  const amountField = document.getElementById("amount");
  const categoryField = document.getElementById("category");
  const descriptionField = document.getElementById("description");
  const dateField = document.getElementById("date");

  if (amountField) amountField.value = amount || "";
  if (categoryField) categoryField.value = category || "";
  if (descriptionField) descriptionField.value = description || "";
  if (dateField) dateField.value = date || "";

  // Switch form to update mode
  const form = document.getElementById("add-expense-form");
  if (form) {
    // Store original add action URL if not already stored
    if (!form.getAttribute("data-add-action")) {
      form.setAttribute("data-add-action", form.action);
    }

    // Change form action to update endpoint
    form.action = "/update_expense/" + id;
  }

  // Update popup title and submit button text
  const title = document.getElementById("popup-title");
  const submitBtn = document.getElementById("add-expense-submit-btn");

  if (title) {
    title.textContent = "Update Expense";
  }

  if (submitBtn) {
    submitBtn.textContent = "Update Expense";
  }

  // Show the popup with pre-filled data
  openPopup();
});

// ============================================
// SECTION 4: FILTER CONTROLS
// ============================================

/**
 * Toggles visibility of advanced filters on expenses page
 */
function toggleAdvancedFilters() {
  const filters = document.getElementById("advanced-filters");

  if (!filters) return;

  // Toggle display between 'none' and 'block'
  if (filters.style.display === "none" || filters.style.display === "") {
    filters.style.display = "block";
  } else {
    filters.style.display = "none";
  }
}

// ============================================
// SECTION 5: INITIALIZATION
// ============================================

/**
 * Runs after DOM is fully loaded
 * Sets initial states and configurations
 */
document.addEventListener("DOMContentLoaded", function () {
  // Hide advanced filters by default
  const advancedFilters = document.getElementById("advanced-filters");
  if (advancedFilters) {
    advancedFilters.style.display = "none";
  }

  console.log("Expense Tracker: JavaScript initialized successfully");
});
