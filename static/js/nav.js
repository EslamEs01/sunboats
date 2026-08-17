(function () {
  var button = document.querySelector("[data-nav-toggle]");
  var menu = document.getElementById("mobile-menu");
  if (!button || !menu) return;

  function closeMenu() {
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-label", "Open menu");
    menu.hidden = true;
    document.body.classList.remove("nav-is-open");
  }

  function openMenu() {
    button.setAttribute("aria-expanded", "true");
    button.setAttribute("aria-label", "Close menu");
    menu.hidden = false;
    document.body.classList.add("nav-is-open");
  }

  button.addEventListener("click", function (event) {
    event.stopPropagation();
    if (menu.hidden) openMenu();
    else closeMenu();
  });

  document.addEventListener("click", function (event) {
    if (menu.hidden) return;
    if (!menu.contains(event.target) && !button.contains(event.target)) closeMenu();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeMenu();
  });
})();
