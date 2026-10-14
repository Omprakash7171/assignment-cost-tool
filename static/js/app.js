/* Assignment Cost Tool — progressive enhancement.
   Highlights the active tab from the current path as a fallback.
   Client-side constraint validation is native HTML5 (type/step/min/required
   emitted by the forms); the server remains the source of truth. */
(function () {
  "use strict";

  // Highlight the active tab from the current path as a fallback.
  document.addEventListener("DOMContentLoaded", function () {
    var links = document.querySelectorAll(".tab-link");
    var path = window.location.pathname;
    links.forEach(function (link) {
      var href = link.getAttribute("href") || "/";
      var base = href.replace(/\/+$/, "");
      var active = base === "" ? path === "/" : path.indexOf(base) === 0;
      if (active) {
        link.classList.add("is-active");
        link.setAttribute("aria-current", "page");
      }
    });
  });
})();
