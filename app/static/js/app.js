if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch(() => null);
  });
}

const body = document.body;
const themeToggle = document.querySelector("[data-theme-toggle]");
const THEME_KEY = "invzeo-theme";
const INSTALL_DISMISS_KEY = "invzeo-install-dismissed";
const savedTheme = localStorage.getItem(THEME_KEY) || localStorage.getItem("ci-help-desk-theme") || "system";
body.dataset.theme = savedTheme;

themeToggle?.addEventListener("click", () => {
  const nextTheme = body.dataset.theme === "dark" ? "light" : body.dataset.theme === "light" ? "system" : "dark";
  body.dataset.theme = nextTheme;
  localStorage.setItem(THEME_KEY, nextTheme);
});

const installBanner = document.querySelector("[data-install-banner]");
const dismissInstall = document.querySelector("[data-dismiss-install]");
const isIOS = /iphone|ipad|ipod/i.test(window.navigator.userAgent);
const isStandalone = window.navigator.standalone || window.matchMedia("(display-mode: standalone)").matches;

if (isIOS && !isStandalone && localStorage.getItem(INSTALL_DISMISS_KEY) !== "true") {
  installBanner?.removeAttribute("hidden");
}

dismissInstall?.addEventListener("click", () => {
  localStorage.setItem(INSTALL_DISMISS_KEY, "true");
  installBanner?.setAttribute("hidden", "hidden");
});
