const revealItems = [...document.querySelectorAll(".reveal")];
const parallaxItems = [...document.querySelectorAll("[data-parallax]")];
const corporateBg = document.querySelector(".corporate-bg");
const heroPattern = document.querySelector(".hero-pattern");
const sections = [...document.querySelectorAll("section[id]")];
const navLinks = [...document.querySelectorAll(".page-nav a")];
const video = document.querySelector(".video-stage video");
const videoToggle = document.querySelector(".video-toggle");
const processItems = [...document.querySelectorAll(".process li")];

const observer = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
      }
    }
  },
  { threshold: 0.18 },
);

for (const item of revealItems) observer.observe(item);

for (const item of processItems) {
  item.addEventListener("click", () => {
    for (const processItem of processItems) processItem.classList.remove("is-selected");
    item.classList.add("is-selected");
  });
}

if (video && videoToggle) {
  const syncVideoButton = () => {
    videoToggle.textContent = video.paused ? "Play" : "Pause";
    videoToggle.setAttribute("aria-label", `${video.paused ? "Play" : "Pause"} workflow video`);
  };

  videoToggle.addEventListener("click", () => {
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  });

  video.addEventListener("play", syncVideoButton);
  video.addEventListener("pause", syncVideoButton);
  video.addEventListener("ended", syncVideoButton);
  syncVideoButton();
}

const applyParallax = () => {
  const center = window.innerHeight / 2;
  if (corporateBg) {
    corporateBg.style.transform = `translate3d(0, ${(window.scrollY * -0.24).toFixed(2)}px, 0)`;
  }
  if (heroPattern) {
    heroPattern.style.transform = `translate3d(0, ${(window.scrollY * -0.44).toFixed(2)}px, 0)`;
  }
  for (const item of parallaxItems) {
    const strength = Number(item.dataset.parallax || 0);
    const rect = item.getBoundingClientRect();
    const delta = (rect.top + rect.height / 2 - center) * strength;
    item.style.setProperty("--parallax-y", `${delta.toFixed(2)}px`);
  }

  let activeSection = sections[0];
  for (const section of sections) {
    if (section.getBoundingClientRect().top < window.innerHeight * 0.38) {
      activeSection = section;
    }
  }
  for (const link of navLinks) {
    link.classList.toggle("is-active", link.getAttribute("href") === `#${activeSection.id}`);
  }
};

let ticking = false;
const requestParallax = () => {
  if (ticking) return;
  ticking = true;
  requestAnimationFrame(() => {
    applyParallax();
    ticking = false;
  });
};

applyParallax();
window.addEventListener("scroll", requestParallax, { passive: true });
window.addEventListener("resize", requestParallax);
