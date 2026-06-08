if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch(() => null);
  });
}

const body = document.body;
const themeToggle = document.querySelector("[data-theme-toggle]");
const savedTheme = localStorage.getItem("ci-help-desk-theme") || "system";
body.dataset.theme = savedTheme;

themeToggle?.addEventListener("click", () => {
  const nextTheme = body.dataset.theme === "dark" ? "light" : body.dataset.theme === "light" ? "system" : "dark";
  body.dataset.theme = nextTheme;
  localStorage.setItem("ci-help-desk-theme", nextTheme);
});

const installBanner = document.querySelector("[data-install-banner]");
const dismissInstall = document.querySelector("[data-dismiss-install]");
const isIOS = /iphone|ipad|ipod/i.test(window.navigator.userAgent);
const isStandalone = window.navigator.standalone || window.matchMedia("(display-mode: standalone)").matches;

if (isIOS && !isStandalone && localStorage.getItem("ci-help-desk-dismiss-install") !== "true") {
  installBanner?.removeAttribute("hidden");
}

dismissInstall?.addEventListener("click", () => {
  localStorage.setItem("ci-help-desk-dismiss-install", "true");
  installBanner?.setAttribute("hidden", "hidden");
});