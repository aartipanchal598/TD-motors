const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav-links');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
}
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal, .service-card, .car-card, .review-card').forEach(el => observer.observe(el));

// Accessible reveal fallback and image recovery
document.documentElement.classList.add('js-ready');
document.querySelectorAll('img').forEach(img => { img.addEventListener('error', () => { img.classList.add('image-failed'); }); });
