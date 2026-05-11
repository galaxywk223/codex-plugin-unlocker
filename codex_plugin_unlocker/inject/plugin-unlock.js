(() => {
  const marker = "__codexPluginUnlocker";
  const version = "0.1.0";
  const selectors = {
    disabledInstallButton: 'button:disabled.w-full.justify-center, [role="button"][aria-disabled="true"].cursor-not-allowed',
    pluginNavButton: 'nav[role="navigation"] button.h-token-nav-row.w-full',
    pluginSvgPath: 'svg path[d^="M7.94562 14.0277"]',
  };

  window[marker] = { version, injectedAt: Date.now() };

  function reactFiberFrom(element) {
    const fiberKey = Object.keys(element).find((key) => key.startsWith("__reactFiber"));
    return fiberKey ? element[fiberKey] : null;
  }

  function reactPropsKeyFrom(element) {
    return Object.keys(element).find((key) => key.startsWith("__reactProps"));
  }

  function authContextValueFrom(element) {
    for (let fiber = reactFiberFrom(element); fiber; fiber = fiber.return) {
      for (const value of [fiber.memoizedProps?.value, fiber.pendingProps?.value]) {
        if (value && typeof value === "object" && typeof value.setAuthMethod === "function" && "authMethod" in value) {
          return value;
        }
      }
    }
    return null;
  }

  function spoofChatGPTAuthMethod(element) {
    const auth = authContextValueFrom(element);
    if (!auth || auth.authMethod === "chatgpt") return false;
    auth.setAuthMethod("chatgpt");
    return true;
  }

  function pluginEntryButton() {
    const byIcon = document.querySelector(`${selectors.pluginNavButton} ${selectors.pluginSvgPath}`)?.closest("button");
    if (byIcon) return byIcon;
    return Array.from(document.querySelectorAll(selectors.pluginNavButton)).find((button) => {
      const text = (button.textContent || "").trim();
      return /^(插件|Plugins)(\s+-\s+.*)?$/i.test(text);
    }) || null;
  }

  function normalizePluginEntryLabel(button) {
    const labelTextNode = Array.from(button.querySelectorAll("span, div")).reverse()
      .flatMap((node) => Array.from(node.childNodes))
      .find((node) => node.nodeType === 3 && /^(插件|Plugins)( - 已解锁| - Unlocked)?$/i.test((node.nodeValue || "").trim()));
    if (!labelTextNode) return;
    const current = (labelTextNode.nodeValue || "").trim();
    labelTextNode.nodeValue = /^Plugins/i.test(current) ? "Plugins" : "插件";
  }

  function enablePluginEntry() {
    const pluginButton = pluginEntryButton();
    if (!pluginButton) return;
    spoofChatGPTAuthMethod(pluginButton);
    pluginButton.disabled = false;
    pluginButton.removeAttribute("disabled");
    pluginButton.style.display = "";
    pluginButton.querySelectorAll("*").forEach((node) => {
      node.style.display = "";
    });
    normalizePluginEntryLabel(pluginButton);
    const reactPropsKey = reactPropsKeyFrom(pluginButton);
    if (reactPropsKey) {
      pluginButton[reactPropsKey].disabled = false;
    }
    if (pluginButton.dataset.codexPluginUnlockerEnabled === "true") return;
    pluginButton.dataset.codexPluginUnlockerEnabled = "true";
    pluginButton.addEventListener("click", () => {
      spoofChatGPTAuthMethod(pluginButton);
    }, true);
  }

  function installButtonLabel(element) {
    return (element.textContent || "").trim();
  }

  function unblockButtonElement(button) {
    button.disabled = false;
    button.removeAttribute("disabled");
    button.removeAttribute("aria-disabled");
    button.classList.remove("disabled", "opacity-50", "cursor-not-allowed", "pointer-events-none");
    button.style.pointerEvents = "auto";
    button.tabIndex = 0;
    const reactPropsKey = reactPropsKeyFrom(button);
    if (reactPropsKey) {
      button[reactPropsKey].disabled = false;
      button[reactPropsKey]["aria-disabled"] = false;
    }
  }

  function labelForcedInstallButton(button) {
    const textNode = Array.from(button.childNodes).find((node) => {
      const text = (node.nodeValue || "").trim();
      return node.nodeType === 3 && (/^安装\s/.test(text) || /^Install\s/.test(text) || text === "强制安装");
    });
    if (textNode) {
      textNode.nodeValue = "强制安装";
    }
  }

  function unblockPluginInstallButtons() {
    Array.from(document.querySelectorAll(selectors.disabledInstallButton)).forEach((button) => {
      const text = installButtonLabel(button);
      if (!/^安装\s/.test(text) && !/^Install\s/.test(text) && text !== "强制安装") return;
      unblockButtonElement(button);
      labelForcedInstallButton(button);
    });
  }

  function runUnlock() {
    try {
      enablePluginEntry();
      unblockPluginInstallButtons();
    } catch (error) {
      window.__codexPluginUnlockerLastError = String(error?.stack || error);
    }
  }

  function scheduleUnlock() {
    if (window.__codexPluginUnlockerScanPending) return;
    window.__codexPluginUnlockerScanPending = true;
    window.__codexPluginUnlockerScanTimer = setTimeout(() => {
      window.__codexPluginUnlockerScanPending = false;
      runUnlock();
    }, 200);
  }

  runUnlock();
  window.__codexPluginUnlockerObserver?.disconnect();
  window.__codexPluginUnlockerObserver = new MutationObserver(scheduleUnlock);
  window.__codexPluginUnlockerObserver.observe(document.body || document.documentElement, { childList: true, subtree: true });
})();
