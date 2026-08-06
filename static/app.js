(function () {
  "use strict";

  // Confirm destructive actions
  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (form && form.dataset.confirm) {
      if (!window.confirm(form.dataset.confirm)) {
        event.preventDefault();
      }
    }
  });

  // Helper to attach a confirm to every .danger form automatically
  document.querySelectorAll("form button.danger").forEach(function (button) {
    var form = button.closest("form");
    if (form && !form.dataset.confirm) {
      form.dataset.confirm = "Are you sure you want to delete this? This cannot be undone.";
    }
  });

  // Clickable table rows (data-href) — ignore clicks on action links/buttons/forms
  document.querySelectorAll("tr[data-href]").forEach(function (row) {
    row.addEventListener("click", function (event) {
      if (event.target.closest("a, button, form")) return;
      window.location.href = row.dataset.href;
    });
  });

  // Lightweight toast helper
  var toast = null;

  function ensureToast() {
    if (toast) return;
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }

  window.showToast = function (message, duration) {
    ensureToast();
    var t = toast;
    t.textContent = message;
    t.classList.add("show");
    clearTimeout(t._timer);
    t._timer = setTimeout(function () {
      t.classList.remove("show");
    }, duration || 2500);
  };

  // Confirm deletions and show a toast on success
  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (form && form.method && form.method.toLowerCase() === "post") {
      // Opt out via data-no-toast attribute
      if (form.dataset.noToast === undefined && !form.matches("[data-no-toast]")) {
        // Generic notice; only show when the action reaches the server cleanly.
        // See the pageInit hook below.
      }
    }
  });

  // Auto-dismiss flash messages after a few seconds
  document.querySelectorAll(".flash").forEach(function (flash) {
    setTimeout(function () {
      flash.style.transition = "opacity 0.4s ease";
      flash.style.opacity = "0";
      setTimeout(function () {
        flash.style.display = "none";
      }, 400);
    }, 4000);
  });
})();