/* PilihCuk: menu navbar untuk layar sempit. Tanpa dependensi. */
(function () {
  "use strict";

  document.querySelectorAll("[data-site-header]").forEach(function (header) {
    var toggle = header.querySelector("[data-nav-toggle]");
    if (!toggle) return;

    function setOpen(open) {
      header.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Tutup menu" : "Buka menu");
    }

    toggle.addEventListener("click", function () {
      setOpen(!header.classList.contains("is-open"));
    });

    // Esc menutup menu dan mengembalikan fokus ke tombol.
    header.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && header.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });

    // Kembali ke layar lebar: pastikan status "terbuka" dibersihkan.
    var narrow = window.matchMedia("(max-width: 75rem)");
    narrow.addEventListener("change", function (e) { if (!e.matches) setOpen(false); });
  });
})();