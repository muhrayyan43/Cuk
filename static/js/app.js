/* PilihCuk: helper JS bersama. Tanpa dependensi.
   Tersedia sebagai window.App: apiFetch, toast, confirm, modal. */
(function () {
  "use strict";

  /* ---------- CSRF + fetch ---------- */
  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  function ApiError(status, data, message) {
    this.name = "ApiError";
    this.status = status;
    this.data = data;
    this.message = message;
  }
  ApiError.prototype = Object.create(Error.prototype);

  function messageFor(status, data) {
    if (data && typeof data.error === "string") return data.error;
    if (status === 401) return "Sesi login sudah berakhir. Masuk lagi, lalu ulangi.";
    if (status === 403) return "Kamu tidak punya izin untuk tindakan ini.";
    if (status === 404) return "Data yang dicari tidak ditemukan.";
    if (status === 429) return "Terlalu banyak permintaan. Tunggu sebentar, lalu coba lagi.";
    if (status >= 500) return "Server sedang bermasalah. Coba lagi beberapa saat lagi.";
    return "Permintaan tidak bisa diproses. Periksa isiannya, lalu coba lagi.";
  }

  /* apiFetch(url, {method, data, headers, signal}) -> Promise<JSON>
     - data objek biasa dikirim sebagai JSON, FormData dikirim apa adanya.
     - Token CSRF otomatis dikirim untuk metode selain GET/HEAD.
     - Gagal -> ApiError (status, data, message berbahasa Indonesia). */
  function apiFetch(url, options) {
    options = options || {};
    var method = (options.method || "GET").toUpperCase();
    var headers = Object.assign(
      { Accept: "application/json", "X-Requested-With": "XMLHttpRequest" },
      options.headers || {}
    );
    var init = { method: method, headers: headers, credentials: "same-origin", signal: options.signal };
    if (method !== "GET" && method !== "HEAD") headers["X-CSRFToken"] = csrfToken();
    if (options.data !== undefined) {
      if (options.data instanceof FormData) {
        init.body = options.data;
      } else {
        headers["Content-Type"] = "application/json";
        init.body = JSON.stringify(options.data);
      }
    }
    return fetch(url, init).then(
      function (res) {
        // Endpoint AJAX tidak boleh mengalihkan. Pengalihan berarti sesi login habis.
        if (res.redirected) throw new ApiError(401, null, messageFor(401));
        var type = res.headers.get("content-type") || "";
        var body = type.indexOf("application/json") !== -1 ? res.json().catch(function () { return null; }) : Promise.resolve(null);
        return body.then(function (data) {
          if (!res.ok) throw new ApiError(res.status, data, messageFor(res.status, data));
          return data;
        });
      },
      function (err) {
        if (err && err.name === "AbortError") throw err;
        throw new ApiError(0, null, "Tidak bisa terhubung ke server. Periksa koneksi internetmu, lalu coba lagi.");
      }
    );
  }

  /* ---------- Toast ---------- */
  var ICON_PATHS = {
    success: '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    warning: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    error: '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    close: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'
  };
  function svg(name, size) {
    return '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="' + size + '" height="' + size +
      '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" ' +
      'stroke-linejoin="round" aria-hidden="true" focusable="false">' + ICON_PATHS[name] + "</svg>";
  }

  function dismiss(toast) {
    if (!toast || toast.classList.contains("is-leaving")) return;
    toast.classList.add("is-leaving");
    setTimeout(function () { toast.remove(); }, 200);
  }

  /* Pesan error tidak hilang sendiri. Timer berhenti saat kursor atau fokus ada di toast. */
  function arm(toast, timeout) {
    if (!timeout) return;
    var timer = null;
    function start() { clearTimeout(timer); timer = setTimeout(function () { dismiss(toast); }, timeout); }
    function stop() { clearTimeout(timer); }
    toast.addEventListener("mouseenter", stop);
    toast.addEventListener("mouseleave", start);
    toast.addEventListener("focusin", stop);
    toast.addEventListener("focusout", start);
    start();
  }

  function toast(message, options) {
    options = options || {};
    var type = ["success", "info", "warning", "error"].indexOf(options.type) !== -1 ? options.type : "info";
    var region = document.getElementById("toast-region");
    if (!region) return null;
    var el = document.createElement("div");
    el.className = "toast toast--" + type;
    el.setAttribute("role", type === "error" ? "alert" : "status");
    el.innerHTML = '<span class="toast__icon">' + svg(type, 20) + "</span>" +
      '<p class="toast__body"></p>' +
      '<button type="button" class="toast__close" aria-label="Tutup notifikasi">' + svg("close", 18) + "</button>";
    el.querySelector(".toast__body").textContent = message; // textContent: aman dari XSS
    region.appendChild(el);
    arm(el, type === "error" ? 0 : (options.timeout === undefined ? 6000 : options.timeout));
    return el;
  }

  // Pesan Django yang dirender server juga ikut auto-hilang (kecuali error).
  document.querySelectorAll("#toast-region .toast").forEach(function (el) {
    arm(el, el.classList.contains("toast--error") ? 0 : 6000);
  });

  /* ---------- Modal (<dialog>) ---------- */
  var modal = {
    open: function (target) {
      var d = typeof target === "string" ? document.querySelector(target) : target;
      if (d && typeof d.showModal === "function" && !d.open) d.showModal();
      return d;
    },
    close: function (target) {
      var d = typeof target === "string" ? document.querySelector(target) : target;
      if (d && d.open) d.close();
    }
  };

  /* App.confirm({title, message, confirmText, cancelText, danger}) -> Promise<boolean> */
  function confirmDialog(opts) {
    opts = opts || {};
    var d = document.getElementById("confirm-modal");
    if (!d) return Promise.resolve(window.confirm(opts.message || "Lanjutkan?"));
    d.querySelector("[data-confirm-title]").textContent = opts.title || "Yakin lanjutkan?";
    d.querySelector("[data-confirm-message]").textContent = opts.message || "";
    var ok = d.querySelector("[data-confirm-ok]");
    var cancel = d.querySelector("[data-confirm-cancel]");
    ok.textContent = opts.confirmText || "Lanjutkan";
    cancel.textContent = opts.cancelText || "Batal";
    ok.className = "btn " + (opts.danger ? "btn-danger" : "btn-primary");
    return new Promise(function (resolve) {
      function done(value) {
        ok.removeEventListener("click", onOk);
        d.removeEventListener("close", onClose);
        if (d.open) d.close();
        resolve(value);
      }
      function onOk() { done(true); }
      function onClose() { done(false); }
      ok.addEventListener("click", onOk);
      d.addEventListener("close", onClose, { once: true });
      d.showModal();
    });
  }

  document.addEventListener("click", function (e) {
    var t = e.target;
    var opener = t.closest("[data-modal-open]");
    if (opener) { modal.open(opener.getAttribute("data-modal-open")); return; }
    var closer = t.closest("[data-modal-close]");
    if (closer) { var dlg = closer.closest("dialog"); if (dlg) dlg.close(); return; }
    var closeToast = t.closest(".toast__close");
    if (closeToast) { dismiss(closeToast.closest(".toast")); return; }
    if (t.closest("[data-reload]")) { window.location.reload(); return; }
    // Klik di area gelap (backdrop) menutup dialog.
    if (t.tagName === "DIALOG" && t.classList.contains("modal")) {
      var r = t.getBoundingClientRect();
      var outside = e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      if (outside) t.close();
    }
  });

  window.App = { apiFetch: apiFetch, ApiError: ApiError, toast: toast, confirm: confirmDialog, modal: modal, csrfToken: csrfToken };
})();
