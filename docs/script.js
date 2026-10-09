const revealItems = [...document.querySelectorAll(".reveal")];
const parallaxItems = [...document.querySelectorAll("[data-parallax]")];
const corporateBg = document.querySelector(".corporate-bg");

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

const applyParallax = () => {
  const center = window.innerHeight / 2;
  if (corporateBg) {
    corporateBg.style.transform = `translate3d(0, ${(window.scrollY * -0.16).toFixed(2)}px, 0)`;
  }
  for (const item of parallaxItems) {
    const strength = Number(item.dataset.parallax || 0);
    const rect = item.getBoundingClientRect();
    const delta = (rect.top + rect.height / 2 - center) * strength;
    item.style.setProperty("--parallax-y", `${delta.toFixed(2)}px`);
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
