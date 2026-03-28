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
  var tabs = document.querySelectorAll(".section-tab");
  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      switchTab(tab);
    });
  });
});
