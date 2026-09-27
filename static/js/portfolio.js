// ==========================================================================
// Deepak Kumar Tiwari Portfolio • High-Performance Dynamic Engine
// Silky 60fps/120fps Particle Constellation + Smooth Spring 3D Glass Tilt
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initUltraSmoothCanvas();
  initSpring3DTilt();
  initSmoothScroll();
  initQuoteCalculator();
});

// --------------------------------------------------------------------------
// 1. Ultra-Smooth 60fps / 120fps Marigold Particle Constellation
// --------------------------------------------------------------------------
function initUltraSmoothCanvas() {
  const canvas = document.getElementById('dynamic-bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d', { alpha: true });

  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  let resizeTimer = null;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    }, 150);
  });

  const mouse = { x: -1000, y: -1000, active: false };

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.active = true;
  }, { passive: true });

  window.addEventListener('mouseleave', () => {
    mouse.x = -1000;
    mouse.y = -1000;
    mouse.active = false;
  }, { passive: true });

  // 36 Optimized particles with Sacred Marigold & Saffron Cyan palette
  const particleCount = Math.min(Math.floor(width / 35), 40);
  const particles = [];

  const marigoldColors = [
    'rgba(251, 191, 36, ',  // Marigold Gold #fbbf24
    'rgba(245, 158, 11, ',  // Rich Amber Marigold #f59e0b
    'rgba(234, 88, 12, ',   // Deep Saffron Orange #ea580c
    'rgba(56, 189, 248, '   // Electric Cyan accent
  ];

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.6;
      this.vy = (Math.random() - 0.5) * 0.6;
      this.radius = Math.random() * 1.8 + 1.2;
      this.color = marigoldColors[Math.floor(Math.random() * marigoldColors.length)];
      this.alpha = Math.random() * 0.45 + 0.35;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0) this.x = width;
      else if (this.x > width) this.x = 0;

      if (this.y < 0) this.y = height;
      else if (this.y > height) this.y = 0;

      // Mouse gentle repulsion / pull without jank
      if (mouse.active) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const distSq = dx * dx + dy * dy;
        if (distSq < 22500) { // 150px radius
          const dist = Math.sqrt(distSq);
          const force = (150 - dist) / 150;
          this.x += (dx / dist) * force * 1.2;
          this.y += (dy / dist) * force * 1.2;
        }
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, 6.283);
      ctx.fillStyle = this.color + this.alpha + ')';
      ctx.fill();
    }
  }

  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  // Optimized render loop with squared distance (no Math.sqrt for lines)
  function render() {
    ctx.clearRect(0, 0, width, height);

    const maxDistSq = 120 * 120; // 14400

    for (let i = 0; i < particles.length; i++) {
      const p1 = particles[i];
      p1.update();
      p1.draw();

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const distSq = dx * dx + dy * dy;

        if (distSq < maxDistSq) {
          const alpha = (1 - distSq / maxDistSq) * 0.18;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(251, 191, 36, ${alpha})`;
          ctx.lineWidth = 0.75;
          ctx.stroke();
        }
      }

      // Connect to mouse cursor
      if (mouse.active) {
        const dx = p1.x - mouse.x;
        const dy = p1.y - mouse.y;
        const distSq = dx * dx + dy * dy;
        if (distSq < maxDistSq) {
          const alpha = (1 - distSq / maxDistSq) * 0.28;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(245, 158, 11, ${alpha})`;
          ctx.lineWidth = 0.9;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(render);
  }

  requestAnimationFrame(render);
}

// --------------------------------------------------------------------------
// 2. High-Performance Spring 3D Glass Tilt (Decoupled with rAF)
// --------------------------------------------------------------------------
function initSpring3DTilt() {
  const cards = document.querySelectorAll('.tilt-target');
  if (!cards.length) return;

  cards.forEach((card) => {
    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;
    let isHovered = false;
    let animFrame = null;

    function springLoop() {
      // Smooth lerp interpolation
      currentX += (targetX - currentX) * 0.14;
      currentY += (targetY - currentY) * 0.14;

      card.style.transform = `perspective(1000px) rotateX(${currentX}deg) rotateY(${currentY}deg) translateZ(${isHovered ? 6 : 0}px)`;

      if (isHovered || Math.abs(currentX) > 0.05 || Math.abs(currentY) > 0.05) {
        animFrame = requestAnimationFrame(springLoop);
      } else {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
      }
    }

    card.addEventListener('mouseenter', () => {
      isHovered = true;
      cancelAnimationFrame(animFrame);
      animFrame = requestAnimationFrame(springLoop);
    });

    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      // Gentle, non-jarring tilt (max 5 degrees)
      targetX = ((y - centerY) / centerY) * -5;
      targetY = ((x - centerX) / centerX) * 5;
    }, { passive: true });

    card.addEventListener('mouseleave', () => {
      isHovered = false;
      targetX = 0;
      targetY = 0;
    });
  });
}

// --------------------------------------------------------------------------
// 3. Smooth Navigation Scroll
// --------------------------------------------------------------------------
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// --------------------------------------------------------------------------
// 4. Direct WhatsApp Inquiry Generator
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

// --------------------------------------------------------------------------
// 5. Interactive Live Quotation Calculator Engine
// --------------------------------------------------------------------------
function updateQuoteCalculator() {
  const baseTierInput = document.querySelector('input[name="quote-tier"]:checked');
  if (!baseTierInput) return;

  const basePrice = parseInt(baseTierInput.value, 10);
  const tierName = baseTierInput.dataset.name || 'Custom Package';

  let total = basePrice;
  const selectedAddons = [];

  document.querySelectorAll('.quote-addon-checkbox:checked').forEach((cb) => {
    total += parseInt(cb.value, 10);
    selectedAddons.push(cb.dataset.addon);
  });

  const formattedTotal = '₹ ' + total.toLocaleString('en-IN');
  const priceDisplay = document.getElementById('calc-total-display');
  if (priceDisplay) {
    priceDisplay.textContent = formattedTotal;
  }

  // Update WhatsApp pre-filled button
  const waBtn = document.getElementById('calc-whatsapp-btn');
  if (waBtn) {
    const isCelebration = tierName.includes('Wedding') || tierName.includes('Birthday') || tierName.includes('Memory');
    const intentLine = isCelebration 
      ? 'I want to discuss this wedding / celebration memory portal, event itinerary, RSVP, and timeline with you!'
      : 'I want to discuss this project structure, timeline, and get started for my business!';

    const msg = `Namaste Deepak ji 🙏

I built a custom website quotation on your portfolio:

📦 *Base Tier:* ${tierName} (₹${basePrice.toLocaleString('en-IN')})
🛠️ *Selected Custom Add-ons:*
${addonsText}

💰 *Estimated Total:* ${formattedTotal}

${intentLine}`;

    waBtn.href = `https://wa.me/916204643184?text=${encodeURIComponent(msg)}`;
  }
}

function initQuoteCalculator() {
  document.querySelectorAll('input[name="quote-tier"]').forEach((radio) => {
    radio.addEventListener('change', updateQuoteCalculator);
  });

  document.querySelectorAll('.quote-addon-checkbox').forEach((cb) => {
    cb.addEventListener('change', updateQuoteCalculator);
  });

  updateQuoteCalculator();
}
