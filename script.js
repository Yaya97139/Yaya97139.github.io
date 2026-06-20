/* ═══════════════════════════════════════════════════════════════════════════
   YANNIS MONDUC — PORTFOLIO  |  script.js
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Navbar scroll behaviour ───────────────────────────────────────────────── */
const navbar  = document.getElementById('navbar');
const navLinks = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
  if (window.scrollY > 30) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
  updateActiveSection();
});

/* ── Mobile menu toggle ────────────────────────────────────────────────────── */
const navToggle = document.getElementById('navToggle');
const navMenu   = document.getElementById('navLinks');

navToggle.addEventListener('click', () => {
  navMenu.classList.toggle('open');
});

navLinks.forEach(link => {
  link.addEventListener('click', () => navMenu.classList.remove('open'));
});

/* ── Active section highlight ─────────────────────────────────────────────── */
const sections = document.querySelectorAll('section[id]');

function updateActiveSection() {
  const scrollPos = window.scrollY + 120;
  sections.forEach(section => {
    const top    = section.offsetTop;
    const bottom = top + section.offsetHeight;
    const id     = section.getAttribute('id');
    const link   = document.querySelector(`.nav-links a[href="#${id}"]`);
    if (link) {
      link.classList.toggle('active', scrollPos >= top && scrollPos < bottom);
    }
  });
}

/* ── Typewriter effect ────────────────────────────────────────────────────── */
const phrases = [
  'Ingénieur Systèmes Embarqués',
  'Spécialiste FPGA & VHDL',
  'Expert en Télécommunications',
  'Développeur Python & C',
  'Passionné de Traitement du Signal',
];

let phraseIdx = 0;
let charIdx   = 0;
let deleting  = false;
const typeEl  = document.getElementById('typewriter-text');

function type() {
  const current = phrases[phraseIdx];
  if (!deleting) {
    typeEl.textContent = current.slice(0, charIdx + 1);
    charIdx++;
    if (charIdx === current.length) {
      deleting = true;
      setTimeout(type, 1800);
      return;
    }
    setTimeout(type, 70);
  } else {
    typeEl.textContent = current.slice(0, charIdx - 1);
    charIdx--;
    if (charIdx === 0) {
      deleting = false;
      phraseIdx = (phraseIdx + 1) % phrases.length;
    }
    setTimeout(type, 40);
  }
}
setTimeout(type, 600);

/* ── Particle canvas background ──────────────────────────────────────────── */
(function initParticles() {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, particles = [];

  function resize() {
    W = canvas.width  = canvas.parentElement.offsetWidth;
    H = canvas.height = canvas.parentElement.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x  = Math.random() * W;
      this.y  = Math.random() * H;
      this.r  = Math.random() * 1.5 + 0.4;
      this.vx = (Math.random() - 0.5) * 0.4;
      this.vy = (Math.random() - 0.5) * 0.4;
      this.a  = Math.random() * 0.5 + 0.1;
    }
    update() {
      this.x += this.vx;
      this.y += this.vy;
      if (this.x < 0 || this.x > W) this.vx *= -1;
      if (this.y < 0 || this.y > H) this.vy *= -1;
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 200, 255, ${this.a})`;
      ctx.fill();
    }
  }

  const COUNT = window.innerWidth < 768 ? 60 : 120;
  for (let i = 0; i < COUNT; i++) particles.push(new Particle());

  function drawLines() {
    const DIST = 120;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < DIST) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0, 200, 255, ${0.12 * (1 - d / DIST)})`;
          ctx.lineWidth   = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => { p.update(); p.draw(); });
    drawLines();
    requestAnimationFrame(animate);
  }
  animate();
})();

/* ── Scroll reveal animations ─────────────────────────────────────────────── */
(function initScrollReveal() {
  const animatables = document.querySelectorAll(
    '.project-card, .skill-category, .timeline-item, .edu-card, .contact-item'
  );

  animatables.forEach((el, i) => {
    el.classList.add('fade-up');
    el.style.transitionDelay = `${(i % 4) * 80}ms`;
  });

  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          observer.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  animatables.forEach(el => observer.observe(el));
})();

/* ── Language bar animation ────────────────────────────────────────────────── */
(function initLangBars() {
  const fills = document.querySelectorAll('.lang-fill');
  fills.forEach(fill => {
    const target = fill.style.width;
    fill.style.width = '0';

    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        fill.style.width = target;
        obs.disconnect();
      }
    }, { threshold: 0.5 });
    obs.observe(fill);
  });
})();

/* ── QR Code generation ────────────────────────────────────────────────────── */
(function generateQRCode() {
  const qrContainer = document.getElementById('qrcode');
  if (!qrContainer || typeof QRCode === 'undefined') return;

  // Update this URL once GitHub Pages is deployed
  const portfolioURL = 'https://yaya97139.github.io';

  new QRCode(qrContainer, {
    text:           portfolioURL,
    width:          200,
    height:         200,
    colorDark:      '#000000',
    colorLight:     '#ffffff',
    correctLevel:   QRCode.CorrectLevel.H,
  });
})();

/* ── Smooth scroll for anchor links ─────────────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const offset = document.getElementById('navbar').offsetHeight;
    const top    = target.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});
