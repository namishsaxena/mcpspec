function toggleGroup(el) {
  el.classList.toggle("open");
  var body = el.nextElementSibling;
  if (body) {
    body.classList.toggle("open");
  }
}

function toggleTool(el) {
  var detail = el.nextElementSibling;
  if (detail) {
    detail.classList.toggle("open");
  }
}

function copyToClipboard(text, btn) {
  if (!navigator.clipboard) {
    return;
  }
  navigator.clipboard.writeText(text).then(function () {
    var original = btn.textContent;
    btn.textContent = "copied!";
    setTimeout(function () {
      btn.textContent = original;
    }, 1500);
  });
}

function toggleTheme() {
  var html = document.documentElement;
  var current = html.getAttribute("data-theme") || "dark";
  var next = current === "dark" ? "light" : "dark";
  html.setAttribute("data-theme", next);
  try { localStorage.setItem("mcpspec-theme", next); } catch (e) {}
  var btn = document.querySelector(".theme-toggle");
  if (btn) btn.textContent = next === "dark" ? "Light" : "Dark";
}

function initTheme() {
  var saved = null;
  try { saved = localStorage.getItem("mcpspec-theme"); } catch (e) {}
  var theme = saved || "dark";
  document.documentElement.setAttribute("data-theme", theme);
  var btn = document.querySelector(".theme-toggle");
  if (btn) btn.textContent = theme === "dark" ? "Light" : "Dark";
}

function switchTab(tabEl) {
  var tabs = document.querySelectorAll(".section-tab");
  var sections = document.querySelectorAll(".section-content");

  tabs.forEach(function (t) {
    t.classList.remove("active");
  });
  sections.forEach(function (s) {
    s.classList.remove("active");
  });

  tabEl.classList.add("active");
  var targetId = tabEl.getAttribute("data-section");
  var target = document.getElementById(targetId);
  if (target) {
    target.classList.add("active");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  initTheme();
  var tabs = document.querySelectorAll(".section-tab");
  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      switchTab(tab);
    });
  });
});
