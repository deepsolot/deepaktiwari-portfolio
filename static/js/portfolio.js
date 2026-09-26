// ==========================================================================
// Deepak Kumar Tiwari Portfolio • Dynamic Interactive Engine
// Constellation Canvas + 3D Glass Tilt + Interactive WhatsApp Engine
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initConstellationCanvas();
  init3DCardTilt();
});

// --------------------------------------------------------------------------
// 1. Dynamic Interactive Particle Constellation Canvas
// --------------------------------------------------------------------------
function initConstellationCanvas() {
  const canvas = document.getElementById('dynamic-bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const mouse = { x: null, y: null, radius: 150 };

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener('mouseout', () => {
    mouse.x = null;
    mouse.y = null;
  });

  // Particle configuration
  const particleCount = Math.floor(Math.min(width, 1400) / 16);
  const particles = [];

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.7;
      this.vy = (Math.random() - 0.5) * 0.7;
      this.radius = Math.random() * 1.8 + 0.8;
      // Palette: Cyan, Gold, Purple
      const colors = [
        'rgba(56, 189, 248, ',   // Cyan
        'rgba(245, 158, 11, ',   // Gold
        'rgba(168, 85, 247, ',   // Purple
        'rgba(236, 72, 153, '    // Pink
      ];
      this.baseColor = colors[Math.floor(Math.random() * colors.length)];
      this.alpha = Math.random() * 0.5 + 0.3;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      // Bounce off boundaries
      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // Gravitate toward cursor if close
      if (mouse.x !== null && mouse.y !== null) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          const force = (mouse.radius - dist) / mouse.radius;
          this.x += (dx / dist) * force * 1.8;
          this.y += (dy / dist) * force * 1.8;
        }
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = this.baseColor + this.alpha + ')';
      ctx.shadowBlur = 10;
      ctx.shadowColor = this.baseColor + '0.8)';
      ctx.fill();
    }
  }

  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    // Draw connecting lines between close particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 110) {
          const lineAlpha = (1 - dist / 110) * 0.22;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(148, 163, 184, ${lineAlpha})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }

      // Connect to mouse cursor
      if (mouse.x !== null && mouse.y !== null) {
        const dx = particles[i].x - mouse.x;
        const dy = particles[i].y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          const lineAlpha = (1 - dist / mouse.radius) * 0.35;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(56, 189, 248, ${lineAlpha})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      particles[i].update();
      particles[i].draw();
    }

    requestAnimationFrame(render);
  }

  render();
}

// --------------------------------------------------------------------------
// 2. Dynamic 3D Card Tilt with Specular Reflection
// --------------------------------------------------------------------------
function init3DCardTilt() {
  const cards = document.querySelectorAll('.tilt-target');

  cards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -6; // max 6 deg
      const rotateY = ((x - centerX) / centerX) * 6;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.015, 1.015, 1.015)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });
}

// --------------------------------------------------------------------------
// 3. Direct WhatsApp Inquiry Generator
// --------------------------------------------------------------------------
function sendPortfolioInquiry(e) {
  e.preventDefault();

  const name = document.getElementById('inq-name').value.trim();
  const category = document.getElementById('inq-cat').value;
  const msg = document.getElementById('inq-msg').value.trim();

  const text = `Namaste Deepak ji 🙏

My Name / Business: *${name}*
Industry: *${category}*
Details: ${msg || 'I want to discuss professional Next.js website development for my business.'}

I checked your live projects (ARL Music Production, Dharohar Banarasi, and New Zen Advocate) and would like to get a quote and timeline!`;

  const encoded = encodeURIComponent(text);
  const waUrl = `https://wa.me/916204643184?text=${encoded}`;

  window.open(waUrl, '_blank');
}
