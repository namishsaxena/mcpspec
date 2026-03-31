// ==========================================================================
// mcpspec.dev — Landing Page Script
// ==========================================================================

(function () {
  "use strict";

  // ---------- Nav scroll border ----------

  var nav = document.getElementById("nav");

  function onScroll() {
    if (window.scrollY > 10) {
      nav.classList.add("scrolled");
    } else {
      nav.classList.remove("scrolled");
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---------- Smooth scroll for anchor links ----------

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      var target = document.querySelector(link.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  // ---------- Code tabs ----------

  var codeTabs = document.querySelectorAll(".code-tab");

  codeTabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      codeTabs.forEach(function (t) {
        t.classList.remove("active");
        t.setAttribute("aria-selected", "false");
      });
      document.querySelectorAll(".code-panel").forEach(function (p) {
        p.classList.remove("active");
      });

      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");
      var panelId = tab.getAttribute("data-panel");
      var panel = document.getElementById(panelId);
      if (panel) {
        panel.classList.add("active");
      }
    });
  });

  // ---------- Copy buttons ----------

  document.querySelectorAll(".copy-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      if (!text) return;

      copyText(text, function () {
        var svg = btn.innerHTML;
        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3 8.5l3.5 3.5 6.5-7"/></svg>';
        setTimeout(function () {
          btn.innerHTML = svg;
        }, 1500);
      });
    });
  });

  function copyText(text, onSuccess) {
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
    } catch (e) { /* ignore */ }
    document.body.removeChild(textarea);
  }

  // ---------- Viewer ----------

  var yamlInput = document.getElementById("yaml-input");
  var yamlError = document.getElementById("yaml-error");
  var previewFrame = document.getElementById("preview-frame");
  var loadExampleBtn = document.getElementById("load-example");
  var debounceTimer = null;

  function renderPreview(yamlStr) {
    var spec;
    try {
      spec = jsyaml.load(yamlStr);
      yamlError.textContent = "";
      yamlError.classList.remove("visible");
    } catch (err) {
      yamlError.textContent = "YAML parse error: " + err.message;
      yamlError.classList.add("visible");
      return;
    }

    if (!spec || typeof spec !== "object") {
      yamlError.textContent = "Invalid spec: expected a YAML object";
      yamlError.classList.add("visible");
      return;
    }

    var title = (spec.info && (spec.info.title || spec.info.name)) || "MCP Server";
    var jsonPayload = JSON.stringify(spec).replace(/<\//g, "<\\/");

    var html = DOCS_TEMPLATE
      .replace("__SPEC_DATA__", jsonPayload)
      .replace("__TITLE__", escapeHtml(title));

    previewFrame.srcdoc = html;
  }

  function escapeHtml(str) {
    if (str == null) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  yamlInput.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      renderPreview(yamlInput.value);
    }, 300);
  });

  loadExampleBtn.addEventListener("click", function () {
    yamlInput.value = EXAMPLE_YAML;
    renderPreview(EXAMPLE_YAML);
  });

  // Load example on page load
  yamlInput.value = EXAMPLE_YAML;
  renderPreview(EXAMPLE_YAML);
})();
