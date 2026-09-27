// ==========================================================================
// Deepak Kumar Tiwari Portfolio • High-Performance Dynamic Engine
// Silky 60fps/120fps Particle Constellation + Smooth Spring 3D Glass Tilt
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initUltraSmoothCanvas();
  initSpring3DTilt();
  initSmoothScroll();
  initQuoteCalculator();
  initAIChatAssistant();
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

// --------------------------------------------------------------------------
// --------------------------------------------------------------------------
// 6. Interactive AI Chat Assistant Engine & Hybrid Intelligence
// --------------------------------------------------------------------------
let globalChatOpen = false;

window.openAIChat = function(e) {
  if (e && e.preventDefault) e.preventDefault();
  const chatWindow = document.getElementById('ai-chat-window');
  const launcherWrap = document.getElementById('ai-launcher-wrap');
  const chatBody = document.getElementById('ai-chat-body');
  const chatInput = document.getElementById('ai-chat-input');

  if (chatWindow) {
    chatWindow.style.display = 'flex';
    globalChatOpen = true;
  }
  if (launcherWrap) launcherWrap.style.display = 'none';
  if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
  if (chatInput) {
    setTimeout(() => chatInput.focus(), 150);
  }
};

window.closeAIChat = function(e) {
  if (e && e.preventDefault) e.preventDefault();
  const chatWindow = document.getElementById('ai-chat-window');
  const launcherWrap = document.getElementById('ai-launcher-wrap');

  if (chatWindow) {
    chatWindow.style.display = 'none';
    globalChatOpen = false;
  }
  if (launcherWrap) launcherWrap.style.display = 'block';
};

window.toggleAIChat = function(e) {
  if (e && e.preventDefault) e.preventDefault();
  const chatWindow = document.getElementById('ai-chat-window');
  if (!chatWindow) return;
  if (chatWindow.style.display === 'none' || !chatWindow.style.display || !globalChatOpen) {
    window.openAIChat(e);
  } else {
    window.closeAIChat(e);
  }
};

window.askQuickPrompt = function(elementOrPrompt) {
  const prompt = typeof elementOrPrompt === 'string'
    ? elementOrPrompt
    : (elementOrPrompt.dataset.prompt || elementOrPrompt.textContent);
  if (prompt) {
    window.handleAIQuery(prompt);
  }
};

window.sendAIChatMessage = function(e) {
  if (e && e.preventDefault) e.preventDefault();
  const chatInput = document.getElementById('ai-chat-input');
  if (!chatInput) return;
  const val = chatInput.value.trim();
  if (!val) return;
  chatInput.value = '';
  window.handleAIQuery(val);
};

// Client-Side Fallback Knowledge Engine (guarantees 100% offline & fast resilience)
window.getClientFallbackReply = function(query) {
  const q = (query || '').toLowerCase();

  if ((q.includes('why') && (q.includes('charge') || q.includes('cost') || q.includes('much') || q.includes('price') || q.includes('money'))) || q.includes('roi') || q.includes('expensive') || q.includes('value') || q.includes('justif') || q.includes('mehenga')) {
    return {
      reply: "💡 **Why Our Pricing (₹15k – ₹45k) Saves You Money:**\n\n• **3-Year Hosting & Domain Included:** Saves ₹12,000+ upfront vs cheap sites that charge yearly renewals.\n• **1 Year Free Support & AMC:** ₹18,000 agency value included.\n• **Next.js Sub-Second Speed (<0.8s):** 95+ Google PageSpeed, zero PHP malware.\n• **1–2 Client Deals Payback:** High-converting lead funnels recover your full cost.\n• **100% Code Ownership:** Full GitHub repository handoff.\n• **50/50 Milestone:** 50% advance, 50% only on final approval.",
      suggestions: ["💰 View Packages", "🤝 Discuss Budget", "📞 Talk to Deepak"]
    };
  }

  if (q.includes('negotiat') || q.includes('budget') || q.includes('discount') || q.includes('flexible') || q.includes('kam') || q.includes('bargain')) {
    return {
      reply: "🤝 **Friendly Negotiation & Budget Flexibility:**\n\nWe build relationships, not rigid invoices! Deepak is directly accessible:\n• 50% advance to start, 50% only after live staging review.\n• Scope can be adjusted to match your exact starting budget.\n• Call or WhatsApp Deepak directly (+91 6204643184) for a friendly chat.",
      suggestions: ["💬 WhatsApp Deepak", "💰 View Pricing", "⚡ Why Next.js?"]
    };
  }

  if (q.includes('wedding') || q.includes('shaadi') || q.includes('birthday') || q.includes('memory') || q.includes('celebrat') || q.includes('shagun') || q.includes('rsvp')) {
    return {
      reply: "💍 **Royal Wedding & Memory Celebration Portals:**\n\n• **WhatsApp RSVP:** Headcount & dietary preferences.\n• **Multi-Event GPS Navigation:** Google Maps directions to Haldi, Sangeet & Shaadi.\n• **Pre-Wedding Reels:** HD photo gallery & drone film embeds.\n• **UPI Shagun QR:** Direct digital gifts to bride/groom.\n• **Live Blessings Wall:** Friends worldwide post photos & wishes.\n\n**Pricing:** Birthday/Tribute ₹8,999 | Royal Wedding ₹14,999 – ₹18,999.",
      suggestions: ["💍 Book Royal Wedding Portal", "🎂 Book Birthday Portal", "📞 Talk to Deepak"]
    };
  }

  if (q.includes('price') || q.includes('pricing') || q.includes('rate') || q.includes('package') || q.includes('how much') || q.includes('cost') || q.includes('charge')) {
    return {
      reply: "💎 **Web & Software Pricing Packages:**\n\n1. **Starter Business:** ₹ 14,999 (3–5 Days)\n2. **Growth & Lead Engine ⭐:** ₹ 21,000 – ₹ 24,999 (3 Years Hosting + 1 Year AMC)\n3. **Enterprise & E-Commerce:** ₹ 34,999 – ₹ 45,000\n4. **Royal Wedding Portal:** ₹ 14,999 – ₹ 18,999\n5. **Native Mobile App:** ₹ 25,000 – ₹ 55,000\n\nAll packages include 50/50 milestone payment and source code ownership!",
      suggestions: ["💡 Why ₹15k–₹45k?", "🤝 Budget Negotiation", "🧮 Calculator"]
    };
  }

  if (q.includes('contact') || q.includes('phone') || q.includes('whatsapp') || q.includes('hire') || q.includes('call') || q.includes('email') || q.includes('address')) {
    return {
      reply: "📞 **Contact Deepak Kumar Tiwari Directly:**\n\n• **WhatsApp & Phone:** [+91 6204643184](https://wa.me/916204643184)\n• **Email:** [deepaksolot@gmail.com](mailto:deepaksolot@gmail.com)\n• **Location:** Varanasi (Kashi), UP, India\n\nDrop a quick WhatsApp message to get an instant reply!",
      suggestions: ["💬 Open WhatsApp Chat", "💰 View Pricing Menu", "💼 View Projects"]
    };
  }

  return {
    reply: "Namaste! 🙏 I am **Deepak's AI Concierge**.\n\nI can help you with pricing, our 3-year hosting inclusions, 50/50 milestone payments, royal wedding portals, or connecting directly with Deepak on WhatsApp (+91 6204643184). What would you like to know?",
    suggestions: ["💰 Pricing Packages", "💡 Why ₹15k–₹45k?", "💍 Wedding Portals", "🤝 Budget Negotiation"]
  };
};

window.appendAIChatMessage = function(sender, text, suggestions = []) {
  const chatBody = document.getElementById('ai-chat-body');
  if (!chatBody) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = `ai-msg ai-msg-${sender}`;

  let formatted = (text || '')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/\n• /g, '<br>• ')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');

  const bubble = document.createElement('div');
  bubble.className = 'ai-msg-bubble';
  bubble.innerHTML = formatted;
  msgDiv.appendChild(bubble);

  const timeSpan = document.createElement('span');
  timeSpan.className = 'ai-msg-time';
  const now = new Date();
  timeSpan.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  msgDiv.appendChild(timeSpan);

  // Move typing indicator back to end if it's there
  const typing = document.getElementById('ai-typing');
  if (typing && typing.parentNode === chatBody) {
    chatBody.insertBefore(msgDiv, typing);
  } else {
    chatBody.appendChild(msgDiv);
  }

  // If bot provided suggestions, render them
  if (sender === 'bot' && suggestions && suggestions.length > 0) {
    const chipsDiv = document.createElement('div');
    chipsDiv.className = 'ai-chips-wrap';
    suggestions.forEach((s) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'ai-chip';
      btn.dataset.prompt = s;
      btn.textContent = s;
      btn.onclick = function() { window.askQuickPrompt(this); };
      chipsDiv.appendChild(btn);
    });
    chatBody.appendChild(chipsDiv);
  }

  chatBody.scrollTop = chatBody.scrollHeight;
};

window.handleAIQuery = function(query) {
  if (!query || !query.trim()) return;
  const cleanQuery = query.trim();

  // Make sure chat window is visible
  window.openAIChat();

  // Append user message immediately
  window.appendAIChatMessage('user', cleanQuery);

  const chatBody = document.getElementById('ai-chat-body');
  const typing = document.getElementById('ai-typing');
  if (typing && chatBody) {
    chatBody.appendChild(typing);
    typing.style.display = 'flex';
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  let answered = false;

  // Timeout controller for 3.5 seconds
  const controller = new AbortController();
  const timer = setTimeout(() => {
    if (!answered) {
      answered = true;
      controller.abort();
      if (typing) typing.style.display = 'none';
      const fallback = window.getClientFallbackReply(cleanQuery);
      window.appendAIChatMessage('bot', fallback.reply, fallback.suggestions);
    }
  }, 3500);

  fetch('/api/ai-chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: cleanQuery }),
    signal: controller.signal
  })
    .then((res) => {
      if (!res.ok) throw new Error('Status: ' + res.status);
      return res.json();
    })
    .then((data) => {
      if (!answered) {
        answered = true;
        clearTimeout(timer);
        if (typing) typing.style.display = 'none';
        window.appendAIChatMessage('bot', data.reply || 'Namaste! How can I assist you further?', data.suggestions || []);
      }
    })
    .catch((_err) => {
      if (!answered) {
        answered = true;
        clearTimeout(timer);
        if (typing) typing.style.display = 'none';
        const fallback = window.getClientFallbackReply(cleanQuery);
        window.appendAIChatMessage('bot', fallback.reply, fallback.suggestions);
      }
    });
};

function initAIChatAssistant() {
  const launcherBtn = document.getElementById('ai-launcher-btn');
  const navAiBtn = document.getElementById('nav-ai-btn');
  const dockAiBtn = document.getElementById('dock-ai-btn');
  const chatClose = document.getElementById('ai-chat-close');
  const chatMinimize = document.getElementById('ai-chat-minimize');
  const chatForm = document.getElementById('ai-chat-form');

  if (launcherBtn) launcherBtn.addEventListener('click', window.toggleAIChat);
  if (navAiBtn) navAiBtn.addEventListener('click', window.openAIChat);
  if (dockAiBtn) dockAiBtn.addEventListener('click', window.openAIChat);
  if (chatClose) chatClose.addEventListener('click', window.closeAIChat);
  if (chatMinimize) chatMinimize.addEventListener('click', window.closeAIChat);

  // Bind existing chips
  document.querySelectorAll('.ai-chip').forEach((chip) => {
    chip.addEventListener('click', function() {
      window.askQuickPrompt(this);
    });
  });

  if (chatForm) {
    chatForm.addEventListener('submit', window.sendAIChatMessage);
  }
}


