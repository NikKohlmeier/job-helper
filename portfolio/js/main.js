// Theme Management
const themeToggle = document.querySelector('.theme-toggle');
const html = document.documentElement;

const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);

themeToggle.addEventListener('click', () => {
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
});

// GSAP Animations
gsap.registerPlugin(ScrollTrigger);

// Hero section animations
gsap.from('.hero__greeting', {
  opacity: 0,
  y: 30,
  duration: 0.8,
  delay: 0.2
});

gsap.from('.hero__title', {
  opacity: 0,
  y: 30,
  duration: 0.8,
  delay: 0.4
});

gsap.from('.hero__subtitle', {
  opacity: 0,
  y: 30,
  duration: 0.8,
  delay: 0.6
});

gsap.from('.hero__description', {
  opacity: 0,
  y: 30,
  duration: 0.8,
  delay: 0.8
});

gsap.from('.hero__cta', {
  opacity: 0,
  y: 30,
  duration: 0.8,
  delay: 1.0
});

// Section titles animation on scroll
gsap.utils.toArray('.section-title').forEach(title => {
  gsap.from(title, {
    opacity: 0,
    y: 50,
    duration: 0.8,
    scrollTrigger: {
      trigger: title,
      start: 'top 80%',
      end: 'bottom 20%',
      toggleActions: 'play none none none'
    }
  });
});

// About section
gsap.from('.about__text p', {
  opacity: 0,
  y: 30,
  duration: 0.6,
  stagger: 0.2,
  scrollTrigger: {
    trigger: '.about__text',
    start: 'top 80%'
  }
});

gsap.from('.about__highlight', {
  opacity: 0,
  y: 30,
  duration: 0.6,
  stagger: 0.15,
  scrollTrigger: {
    trigger: '.about__highlights',
    start: 'top 80%'
  }
});

// Skills categories
gsap.from('.skills__category', {
  opacity: 0,
  y: 40,
  duration: 0.6,
  stagger: 0.2,
  clearProps: 'transform',
  scrollTrigger: {
    trigger: '.skills__grid',
    start: 'top 80%'
  }
});

// Animate skill bars on scroll
gsap.utils.toArray('.skills__bar-fill').forEach((bar, index) => {
  const percent = bar.getAttribute('data-percent');

  gsap.fromTo(bar,
    { width: '0%' },
    {
      width: `${percent}%`,
      duration: 1.2,
      delay: index * 0.05,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: '.skills',
        start: 'top 70%',
        once: true
      }
    }
  );
});

// Work section
gsap.from('.work__intro', {
  opacity: 0,
  y: 30,
  duration: 0.8,
  scrollTrigger: {
    trigger: '.work__intro',
    start: 'top 80%'
  }
});

gsap.from('.work__demo', {
  opacity: 0,
  y: 50,
  duration: 0.8,
  scrollTrigger: {
    trigger: '.work__demo',
    start: 'top 80%'
  }
});

// Projects - animate each individually to ensure they all appear
document.querySelectorAll('.project').forEach((project, index) => {
  gsap.from(project, {
    opacity: 0,
    y: 50,
    duration: 0.8,
    delay: index * 0.2,
    scrollTrigger: {
      trigger: project,
      start: 'top 85%',
      toggleActions: 'play none none none'
    }
  });
});

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));

    if (target) {
      const headerOffset = 80;
      const elementPosition = target.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  });
});

// Nav scroll effect
let lastScroll = 0;
const nav = document.querySelector('.nav');

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;

  if (currentScroll > 100) {
    nav.style.boxShadow = '0 2px 10px var(--color-shadow)';
  } else {
    nav.style.boxShadow = 'none';
  }

  lastScroll = currentScroll;
});

// Mobile tooltip handling for skills
const isMobile = () => window.innerWidth <= 1024;
let activeTooltip = null;
let isScrolling = false;
let scrollTimeout;

window.addEventListener('scroll', () => {
  isScrolling = true;
  clearTimeout(scrollTimeout);

  // Hide active tooltip during scroll
  if (activeTooltip && isMobile()) {
    activeTooltip.classList.remove('skills__item--active');
    activeTooltip = null;
  }

  scrollTimeout = setTimeout(() => {
    isScrolling = false;
  }, 150);
});

document.querySelectorAll('.skills__item').forEach(item => {
  // Touch handling for mobile
  item.addEventListener('touchstart', (e) => {
    if (!isMobile() || isScrolling) return;

    // If tapping the same item, close it
    if (activeTooltip === item) {
      item.classList.remove('skills__item--active');
      activeTooltip = null;
      return;
    }

    // Close previous tooltip
    if (activeTooltip) {
      activeTooltip.classList.remove('skills__item--active');
    }

    // Open new tooltip
    item.classList.add('skills__item--active');
    activeTooltip = item;

    // Prevent default to avoid triggering hover on touch
    e.preventDefault();
  });

  // Click handling for mobile (fallback)
  item.addEventListener('click', (e) => {
    if (!isMobile()) return;

    if (activeTooltip === item) {
      item.classList.remove('skills__item--active');
      activeTooltip = null;
    } else {
      if (activeTooltip) {
        activeTooltip.classList.remove('skills__item--active');
      }
      item.classList.add('skills__item--active');
      activeTooltip = item;
    }
  });
});

// Close tooltip when tapping outside
document.addEventListener('touchstart', (e) => {
  if (!isMobile() || !activeTooltip) return;

  if (!e.target.closest('.skills__item')) {
    activeTooltip.classList.remove('skills__item--active');
    activeTooltip = null;
  }
});

// Spacecursor Interactive Demo
const spacecursorDemo = document.querySelector('.spacecursor');
if (spacecursorDemo) {
  const cursor = document.getElementById('cursor');
  const moon = document.getElementById('moon');
  let lastX, lastY;
  let isOverMoon = false;
  let lastAngle = 0;

  // Unified handler for both mouse and touch
  const handleMove = (clientX, clientY) => {
    const rect = spacecursorDemo.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;

    if (lastX !== undefined && lastY !== undefined) {
      const deltaX = x - lastX;
      const deltaY = y - lastY;
      let angle = Math.atan2(deltaY, deltaX) * 180 / Math.PI;

      if (angle - lastAngle > 180) {
        angle -= 360;
      } else if (angle - lastAngle < -180) {
        angle += 360;
      }

      lastAngle = angle;

      gsap.to(cursor, {
        duration: 1,
        rotation: angle,
        x: x,
        y: y,
        ease: 'power4.out',
      });
    } else {
      gsap.set(cursor, {
        x: x,
        y: y,
      });
    }

    lastX = x;
    lastY = y;

    const moonRect = moon.getBoundingClientRect();
    const cursorRect = cursor.getBoundingClientRect();
    const demoRect = spacecursorDemo.getBoundingClientRect();

    const moonRelative = {
      left: moonRect.left - demoRect.left,
      right: moonRect.right - demoRect.left,
      top: moonRect.top - demoRect.top,
      bottom: moonRect.bottom - demoRect.top
    };

    const cursorRelative = {
      left: cursorRect.left - demoRect.left,
      right: cursorRect.right - demoRect.left,
      top: cursorRect.top - demoRect.top,
      bottom: cursorRect.bottom - demoRect.top
    };

    if (
      cursorRelative.left < moonRelative.right &&
      cursorRelative.right > moonRelative.left &&
      cursorRelative.top < moonRelative.bottom &&
      cursorRelative.bottom > moonRelative.top
    ) {
      if (!isOverMoon) {
        isOverMoon = true;
        gsap.to(moon, {
          duration: 2,
          boxShadow: '0 0 20px 15px rgba(255, 255, 255, 0.8)',
          ease: 'power.out',
        });
      }
    } else if (isOverMoon) {
      isOverMoon = false;
      gsap.to(moon, {
        duration: 2,
        boxShadow: '0 0 0px 0px white',
        ease: 'power.out',
      });
    }
  };

  const handleEnd = () => {
    gsap.to(cursor, {
      duration: 0.5,
      opacity: 0
    });
    if (isOverMoon) {
      isOverMoon = false;
      gsap.to(moon, {
        duration: 2,
        boxShadow: '0 0 0px 0px white',
        ease: 'power.out',
      });
    }
    lastX = undefined;
    lastY = undefined;
  };

  const handleStart = () => {
    gsap.to(cursor, {
      duration: 0.5,
      opacity: 1
    });
  };

  // Mouse events
  spacecursorDemo.addEventListener('mousemove', (e) => {
    handleMove(e.clientX, e.clientY);
  });

  spacecursorDemo.addEventListener('mouseleave', handleEnd);
  spacecursorDemo.addEventListener('mouseenter', handleStart);

  // Touch events
  spacecursorDemo.addEventListener('touchstart', (e) => {
    e.preventDefault();
    handleStart();
    const touch = e.touches[0];
    handleMove(touch.clientX, touch.clientY);
  });

  spacecursorDemo.addEventListener('touchmove', (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    handleMove(touch.clientX, touch.clientY);
  });

  spacecursorDemo.addEventListener('touchend', (e) => {
    e.preventDefault();
    handleEnd();
  });

  spacecursorDemo.addEventListener('touchcancel', handleEnd);
}
