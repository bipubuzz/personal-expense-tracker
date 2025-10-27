//NAV_BAR_ADD_EXPENSE_POPUP
document
  .getElementById("add-expense-btn")
  .addEventListener("click", function () {
    document.getElementById("popup").classList.add("show");
  });
document.getElementById("exit-btn").addEventListener("click", function () {
  document.getElementById("popup").classList.remove("show");
});
