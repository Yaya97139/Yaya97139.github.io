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

/* ── Language switch (FR / EN) ───────────────────────────────────────────── */
const li   = items => items.map(t => `<li><i class="fas fa-check-circle"></i> ${t}</li>`).join('');
const ul   = items => items.map(t => `<li>${t}</li>`).join('');
const tags = items => items.map(t => `<span>${t}</span>`).join('');

const PHRASES = {
  fr: [
    'Ingénieur Systèmes Embarqués',
    'Spécialiste FPGA & VHDL',
    'Expert en Télécommunications',
    'Développeur Python & C',
    'Passionné de Traitement du Signal',
  ],
  en: [
    'Embedded Systems Engineer',
    'FPGA & VHDL Specialist',
    'Telecommunications Expert',
    'Python & C Developer',
    'Signal Processing Enthusiast',
  ],
};

const META = {
  fr: {
    title: 'Yannis MONDUC — Ingénieur Systèmes Embarqués & Télécommunications',
    description: 'Portfolio de Yannis MONDUC, ingénieur spécialisé en systèmes embarqués, FPGA, et télécommunications. INSA Hauts-de-France. Stage ITA Brésil.',
    switchLabel: 'EN',
    switchTitle: 'Switch to English',
  },
  en: {
    title: 'Yannis MONDUC — Embedded Systems & Telecommunications Engineer',
    description: 'Portfolio of Yannis MONDUC, engineer specialized in embedded systems, FPGA and telecommunications. INSA Hauts-de-France. Internship at ITA, Brazil.',
    switchLabel: 'FR',
    switchTitle: 'Passer en français',
  },
};

const I18N_EN = {
  'nav.about': 'About',
  'nav.skills': 'Skills',
  'nav.projects': 'Projects',
  'nav.experience': 'Experience',
  'nav.education': 'Education',
  'nav.contact': 'Contact',

  'hero.greeting': "Hello, I'm",
  'hero.tagline': 'Engineer specialized in <strong>Embedded Systems</strong> and <strong>Telecommunications</strong> — INSA Hauts-de-France · Research internship at <strong>ITA, Brazil</strong>',
  'hero.ctaProjects': 'See my projects',
  'hero.scroll': 'Scroll',
  'cv.download': '<i class="fas fa-download"></i> Download my CV (FR)',

  'about.title': 'About <span class="accent">Me</span>',
  'about.location': '<i class="fas fa-map-marker-alt"></i> Mobile — Anywhere in France',
  'about.nationality': '<i class="fas fa-flag"></i> French nationality',
  'about.age': '<i class="fas fa-birthday-cake"></i> 22 years old',
  'about.available': '<i class="fas fa-circle"></i> Available immediately',
  'about.p1': 'Engineering graduate from <strong>INSA Hauts-de-France</strong> in Embedded Systems, Electronics and Telecommunications, I am passionate about designing systems at the intersection of <strong>hardware and software</strong>: FPGAs, microcontrollers, communication protocols and signal processing.',
  'about.p2': 'Currently completing my <strong>end-of-studies internship at ITA (Instituto Tecnológico de Aeronáutica)</strong> in Brazil, I work on FPGA solutions for embedded systems and on the implementation of advanced digital communication chains — an international experience within a world-renowned research laboratory.',
  'about.p3': 'My background combines hands-on projects (UWB indoor localization, patch antenna, real-time interfaces) and diverse professional experiences in aeronautics, mobility and agricultural research. I am looking for positions in <strong>aeronautics, space, embedded systems or telecommunications</strong>.',
  'lang.french': 'French',
  'lang.native': 'C2 — Native',
  'lang.english': 'English',
  'lang.spanish': 'Spanish',

  'skills.title': 'Technical <span class="accent">Skills</span>',
  'skills.embedded.title': 'Embedded Systems',
  'skills.embedded.tags': tags(['FPGA', 'VHDL', 'Arduino', 'ESP32', 'STM32', 'Raspberry Pi', 'Microcontrollers', 'RTOS', 'Bare-metal']),
  'skills.telecom.title': 'Telecommunications',
  'skills.telecom.tags': tags(['TDOA / RSSI', 'UWB', 'Digital Modulation', 'OFDM', 'WiFi / BLE', 'Wireless Networks', 'Patch Antenna', 'RF Design']),
  'skills.prog.title': 'Programming',
  'skills.tools.title': 'Tools & Software',
  'skills.tools.tags': tags(['Intel Quartus', 'Multisim', 'AIGLE', 'NumPy / SciPy', 'Matplotlib', 'Tkinter', 'WebSocket / Tornado', 'Office Suite']),
  'skills.arch.title': 'System Architecture',
  'skills.arch.tags': tags(['IoT', 'Connected Objects', 'CCO', 'Signal Processing', 'Sensor Fusion', 'Least Squares']),
  'skills.soft.tags': tags(['Reliable', 'Rigorous', 'Curious', 'Responsive', 'Autonomous', 'Methodical']),

  'projects.title': 'Professional <span class="accent">Projects</span>',
  'projects.subtitle': 'Concrete achievements combining research, design and development',
  'link.source': '<i class="fab fa-github"></i> Source Code',
  'link.report': '<i class="fas fa-file-alt"></i> Report (LaTeX)',
  'link.files': '<i class="fab fa-github"></i> Project Files',

  'p1.badge': 'End-of-Studies Internship',
  'p1.title': 'FPGA & Digital Communication Chains',
  'p1.org': 'ITA — Instituto Tecnológico de Aeronáutica · Brazil · 2025–2026',
  'p1.desc': 'Research internship within a world-renowned laboratory, <strong>ITA (São José dos Campos, Brazil)</strong>, the Brazilian equivalent of École Polytechnique. Work on the design and implementation of <strong>FPGA solutions for embedded systems</strong>, and in-depth study of <strong>digital communication chains</strong>: modulation, coding, synchronization and real-time decoding on hardware targets.',
  'p1.highlights': li([
    'Research and development of FPGA solutions',
    'Study of digital communication chains',
    'Simulation and synthesis on FPGA targets',
    'International collaboration in a research environment',
  ]),
  'p1.tags': tags(['FPGA', 'VHDL', 'Digital Communication', 'Embedded Systems', 'MATLAB', 'Intel Quartus']),

  'p2.badge': 'IEMN Internship',
  'p2.title': 'UWB Indoor Localization System',
  'p2.org': 'IEMN — Institute of Electronics, Microelectronics and Nanotechnology · 2026',
  'p2.desc': 'End-to-end design of an <strong>indoor localization</strong> system based on <strong>UWB (Ultra-Wideband)</strong> technology with fusion of complementary measurements. An ESP32 transmitter tag is located in a room using two fixed receivers (anchors) by combining:<br>— <strong>RSSI</strong> (signal strength → distance circle)<br>— <strong>TDOA</strong> (time difference of arrival → hyperbola)<br>The circle + hyperbola intersection gives the estimated position, refined with a <strong>least-squares algorithm</strong> (Levenberg-Marquardt).',
  'p2.highlights': li([
    'Arduino firmware on ESP32 (UWB transmitter tag)',
    'TDOA + RSSI algorithmic fusion (SciPy Least Squares)',
    'Real-time graphical interface (Python / Tkinter / Matplotlib)',
    'WiFi server for real-time data collection',
    'Complete scientific report written in LaTeX',
  ]),

  'p3.title': 'Embedded Thermal Camera',
  'p3.org': 'Academic Project · INSA Hauts-de-France',
  'p3.desc': 'Development of an <strong>embedded thermal vision</strong> system integrating an infrared sensor and a microcontroller. The project covers thermal data acquisition, digital processing and real-time display of a thermal map of the observed scene. Applications include industrial maintenance, presence detection and quality control.',
  'p3.highlights': li([
    'Infrared data acquisition and processing',
    'Real-time thermal mapping',
    'Integration on an embedded target (microcontroller)',
  ]),
  'p3.tags': tags(['Embedded Systems', 'IR Sensors', 'C / C++', 'Image Processing', 'IoT']),

  'p4.title': 'Real-Time Web Interface for Embedded Systems',
  'p4.org': 'Professional Project · 2025–2026',
  'p4.desc': 'Development of a <strong>web user interface</strong> (HTML/CSS/JavaScript) for embedded prototypes, with a Python backend handling hardware data. <strong>Real-time bidirectional</strong> communication via the <strong>WebSocket</strong> protocol (Tornado server), enabling monitoring and control of an embedded system from a browser with no perceptible latency.',
  'p4.highlights': li([
    'Responsive web interface (HTML / CSS / JS)',
    'Bidirectional real-time WebSocket communication',
    'Python Tornado server powering the embedded backend',
    'Live sensor data visualization',
  ]),

  'p5.title': 'Design & Fabrication of a Patch Antenna',
  'p5.org': 'Academic Project · INSA Hauts-de-France · 2024–2025',
  'p5.desc': 'Complete project covering the <strong>design and fabrication of a microstrip patch antenna</strong>, from initial specification to physical fabrication. Use of the <strong>AIGLE</strong> software for simulation and sizing. Advanced electromagnetic simulations: 3D radiation patterns, S-parameter measurements and impedance matching analysis.',
  'p5.highlights': li([
    'Design from concept phase to physical fabrication',
    'Electromagnetic simulations (radiation patterns)',
    'S-parameter measurement and analysis (matching)',
    'Experimental validation in an anechoic chamber',
  ]),
  'p5.tags': tags(['RF Design', 'AIGLE', 'Patch Antenna', 'Electromagnetics', 'S-Parameters']),

  'p6.title': 'Booster System - Embedded Platform',
  'p6.org': 'Academic Project · INSA Hauts-de-France',
  'p6.desc': 'Design and finalization of a <strong>booster-type embedded system</strong>, including the hardware and software architecture of a real-time control platform. The project integrates actuator management, sensor monitoring and inter-module communication, demonstrating full command of the embedded system development cycle.',
  'p6.highlights': li([
    'Real-time hardware and software architecture',
    'Actuator management and sensor monitoring',
    'Inter-module communication',
  ]),
  'p6.tags': tags(['Embedded Systems', 'C / C++', 'Real-Time', 'Microcontrollers']),

  'experience.title': 'Professional <span class="accent">Experience</span>',

  'exp1.title': 'End-of-Studies Internship - Embedded Systems Researcher',
  'exp1.org': '<i class="fas fa-building"></i> ITA - Instituto Tecnológico de Aeronáutica · São José dos Campos, Brazil',
  'exp1.tasks': ul([
    'Research and development of FPGA solutions for embedded systems',
    'Study and implementation of digital communication chains (modulation, coding, decoding)',
    'International experience in a world-renowned research laboratory',
  ]),
  'exp1.tags': tags(['FPGA', 'VHDL', 'Digital Communication', 'Research']),

  'exp2.title': 'Support & Monitoring Technician',
  'exp2.org': '<i class="fas fa-plane"></i> Pôle Caraïbes Airport · Guadeloupe',
  'exp2.tasks': ul([
    'Monitoring and operation of an automated parking control system (cameras)',
    'Real-time handling of technical incidents in a critical airport environment',
    'Traffic density tracking and field interventions via connected systems (IoT)',
  ]),
  'exp2.tags': tags(['IoT', 'Connected Systems', 'Monitoring', 'Real-Time']),

  'exp3.title': 'Engineering Intern',
  'exp3.org': '<i class="fas fa-bicycle"></i> Fixwheel (Micromobility)',
  'exp3.tasks': ul([
    'Optimization of repair processes for micromobility devices',
    'Improvement of quality control workflows',
    'Participation in project planning and technical coordination',
  ]),
  'exp3.tags': tags(['Project Management', 'Quality', 'Technical Coordination']),

  'exp4.title': 'Business Unit Member',
  'exp4.date': 'Feb. 2024',
  'exp4.org': '<i class="fas fa-lightbulb"></i> JINNOV — INSA Junior Enterprise',
  'exp4.tasks': ul([
    'Management of an internal services portfolio',
    'Product-service alignment with business objectives',
    'Collaboration with a multidisciplinary team',
  ]),
  'exp4.tags': tags(['Junior Enterprise', 'Business', 'Teamwork']),

  'exp5.title': 'Intern — Meteorological Data',
  'exp5.org': '<i class="fas fa-leaf"></i> INRAE (French National Research Institute for Agriculture, Food and Environment)',
  'exp5.tasks': ul([
    'Deployment of a meteorological data collection station',
    'Contribution to the automation of agricultural tasks',
  ]),
  'exp5.tags': tags(['Sensors', 'Data Collection', 'Agriculture']),

  'education.title': '<span class="accent">Education</span>',
  'edu1.title': 'Engineering Degree',
  'edu1.subtitle': 'Embedded Systems & Telecommunications',
  'edu1.highlights': ul([
    'Embedded systems architecture, wireless networks',
    'Digital modulation, IoT, signal processing',
    'FPGA, microcontrollers (Arduino, STM32), Raspberry Pi',
    'CCO - Object Design and Costing',
  ]),
  'edu2.title': 'Scientific Baccalaureate',
  'edu2.subtitle': 'Specialization in Mathematics & Physics-Chemistry',
  'edu2.highlights': ul([
    'Obtained with honors',
    'Specialization in Mathematics and Physics-Chemistry',
  ]),

  'contact.subtitle': 'Available immediately - Open to opportunities in embedded systems engineering, telecommunications, aeronautics, space, defense, Industry 4.0, IoT, signal processing, R&amp;D and electronic design',
  'contact.phone': 'Phone',
  'contact.location': 'Location',
  'contact.locationValue': 'Mobile — Anywhere in France',
  'contact.license': 'Driving licence',
  'contact.licenseValue': 'Category B',
  'contact.qrTitle': '<i class="fas fa-qrcode"></i> Scan to access the portfolio',
  'contact.qrHint': 'Add this QR code to your CV so recruiters can access this page directly.',

  'footer.copy': '© 2026 Yannis MONDUC - Embedded Systems & Telecommunications Engineer',
};

const i18nEls = document.querySelectorAll('[data-i18n]');
i18nEls.forEach(el => { el.dataset.i18nFr = el.innerHTML; });

const langSwitch      = document.getElementById('langSwitch');
const langSwitchLabel = document.getElementById('langSwitchLabel');
const metaDescription = document.querySelector('meta[name="description"]');

function getInitialLang() {
  const fromUrl = new URLSearchParams(window.location.search).get('lang');
  if (fromUrl === 'en' || fromUrl === 'fr') return fromUrl;
  try {
    const saved = localStorage.getItem('lang');
    if (saved === 'en' || saved === 'fr') return saved;
  } catch (e) { /* storage unavailable */ }
  return 'fr';
}

let currentLang = getInitialLang();

function applyLang(lang) {
  currentLang = lang;
  i18nEls.forEach(el => {
    const html = lang === 'en' ? I18N_EN[el.dataset.i18n] : el.dataset.i18nFr;
    if (html !== undefined) el.innerHTML = html;
  });

  const meta = META[lang];
  document.documentElement.lang = lang;
  document.title = meta.title;
  if (metaDescription) metaDescription.content = meta.description;
  langSwitchLabel.textContent = meta.switchLabel;
  langSwitch.title = meta.switchTitle;
  langSwitch.setAttribute('aria-label', meta.switchTitle);

  try { localStorage.setItem('lang', lang); } catch (e) { /* storage unavailable */ }
}

langSwitch.addEventListener('click', () => {
  applyLang(currentLang === 'fr' ? 'en' : 'fr');
  // Restart the typewriter with the new language phrases
  phraseIdx = 0;
  charIdx   = 0;
  deleting  = false;
});

if (currentLang !== 'fr') applyLang(currentLang);

/* ── Typewriter effect ────────────────────────────────────────────────────── */
let phraseIdx = 0;
let charIdx   = 0;
let deleting  = false;
const typeEl  = document.getElementById('typewriter-text');

function type() {
  const phrases = PHRASES[currentLang];
  const current = phrases[phraseIdx % phrases.length];
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
