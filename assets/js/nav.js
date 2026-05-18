(function () {
  "use strict";

  const nav = document.getElementById("primary-nav");
  const toggle = document.querySelector(".nav-toggle");
  const items = document.querySelectorAll(".nav-item.has-mega");
  const mq = window.matchMedia("(max-width: 960px)");

  function closeAll(except) {
    items.forEach((item) => {
      if (item === except) return;
      item.classList.remove("is-open");
      const trigger = item.querySelector(".nav-trigger");
      if (trigger) trigger.setAttribute("aria-expanded", "false");
    });
  }

  function setMobileNav(open) {
    if (!nav || !toggle) return;
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
    document.body.style.overflow = open && mq.matches ? "hidden" : "";
  }

  if (toggle) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") !== "true";
      setMobileNav(open);
      if (!open) closeAll(null);
    });
  }

  items.forEach((item) => {
    const trigger = item.querySelector(".nav-trigger");
    if (!trigger) return;

    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const willOpen = !item.classList.contains("is-open");
      closeAll(item);
      item.classList.toggle("is-open", willOpen);
      trigger.setAttribute("aria-expanded", willOpen ? "true" : "false");
    });

    if (!mq.matches) {
      item.addEventListener("mouseenter", () => {
        closeAll(item);
        item.classList.add("is-open");
        trigger.setAttribute("aria-expanded", "true");
      });
      item.addEventListener("mouseleave", () => {
        item.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
      });
    }
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".nav-item.has-mega")) closeAll(null);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeAll(null);
      if (mq.matches && nav && nav.classList.contains("is-open")) {
        setMobileNav(false);
        toggle && toggle.focus();
      }
    }
  });

  mq.addEventListener("change", () => {
    closeAll(null);
    setMobileNav(false);
  });
})();
