function toggleGroup(el) {
  el.classList.toggle("open");
  var isOpen = el.classList.contains("open");
  el.setAttribute("aria-expanded", String(isOpen));
  var body = el.nextElementSibling;
  if (body) {
    body.classList.toggle("open");
  }
}

function toggleTool(el) {
  var detail = el.nextElementSibling;
  if (detail) {
    detail.classList.toggle("open");
    var isOpen = detail.classList.contains("open");
    el.setAttribute("aria-expanded", String(isOpen));
  }
}

function copyFromCode(btn) {
  var pre = btn.parentElement && btn.parentElement.querySelector("pre");
  if (!pre) return;
  var text = pre.textContent || "";

  function onSuccess() {
    var original = btn.innerHTML;
    btn.innerHTML = iconCheck() + " copied!";
    setTimeout(function () {
      btn.innerHTML = original;
    }, 1500);
  }

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(onSuccess).catch(function () {
      fallbackCopy(text, onSuccess);
    });
  } else {
    fallbackCopy(text, onSuccess);
  }
}

function fallbackCopy(text, onSuccess) {
  var textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand("copy");
    onSuccess();
  } catch (e) {}
  document.body.removeChild(textarea);
}

function switchTab(tabEl) {
  var tabs = document.querySelectorAll(".section-tab");
  var sections = document.querySelectorAll(".section-content");

  tabs.forEach(function (t) {
    t.classList.remove("active");
    t.setAttribute("aria-selected", "false");
  });
  sections.forEach(function (s) {
    s.classList.remove("active");
  });

  tabEl.classList.add("active");
  tabEl.setAttribute("aria-selected", "true");
  var targetId = tabEl.getAttribute("data-section");
  var target = document.getElementById(targetId);
  if (target) {
    target.classList.add("active");
  }
}

var THEME_CYCLE = ["dark", "light", "contrast"];
var THEME_NEXT = { dark: "light", light: "contrast", contrast: "dark" };
var THEME_LABELS = {
  dark: { icon: "sun", text: "Light", aria: "Switch to light theme" },
  light: { icon: "contrast", text: "Contrast", aria: "Switch to high contrast theme" },
  contrast: { icon: "moon", text: "Dark", aria: "Switch to dark theme" }
};

function toggleTheme() {
  var html = document.documentElement;
  var current = html.getAttribute("data-theme") || "dark";
  var next = THEME_NEXT[current] || "dark";
  html.setAttribute("data-theme", next);
  try { localStorage.setItem("mcpspec-theme", next); } catch (e) {}
  updateToggleButton(next);
}

function updateToggleButton(theme) {
  var btn = document.querySelector(".theme-toggle");
  if (!btn) return;
  var label = THEME_LABELS[theme] || THEME_LABELS.dark;
  var icon = label.icon === "sun" ? iconSun() : label.icon === "moon" ? iconMoon() : iconContrast();
  btn.innerHTML = icon + " " + label.text;
  btn.setAttribute("aria-label", label.aria);
}

function initTheme() {
  var saved = null;
  try { saved = localStorage.getItem("mcpspec-theme"); } catch (e) {}
  var theme = saved || "dark";
  document.documentElement.setAttribute("data-theme", theme);
  updateToggleButton(theme);
}

document.addEventListener("DOMContentLoaded", function () {
  initTheme();

  var tabs = document.querySelectorAll(".section-tab");
  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      switchTab(tab);
    });
  });

  // Keyboard support: Enter/Space activates role="button" and role="tab"
  document.addEventListener("keydown", function (e) {
    var role = e.target.getAttribute("role");
    if ((e.key === "Enter" || e.key === " ") && (role === "button" || role === "tab")) {
      e.preventDefault();
      e.target.click();
    }
  });
});
