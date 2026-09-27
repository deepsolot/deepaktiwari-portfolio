import csv
import io
import json
import os
import time
from flask import Flask, jsonify, render_template, request, Response

from scraper import (
    CATEGORIES,
    LEADS_FILE,
    VARANASI_LOCALITIES,
    load_leads,
    run_live_scan,
    save_leads
)
from outreach_engine import TEMPLATES, generate_pitch, get_whatsapp_urls

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "index.html",
        localities=VARANASI_LOCALITIES,
        categories=CATEGORIES
    )


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")


@app.route("/robots.txt")
def robots_txt():
    content = """User-agent: *
Allow: /
Allow: /portfolio
Sitemap: https://deepaktiwari-portfolio.vercel.app/sitemap.xml
"""
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://deepaktiwari-portfolio.vercel.app/portfolio</loc>
    <lastmod>2026-09-26</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://deepaktiwari-portfolio.vercel.app/</loc>
    <lastmod>2026-09-26</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""
    return Response(xml_content, mimetype="application/xml")


@app.route("/google323487b5afd163b8.html")
def google_verification():
    return Response("google-site-verification: google323487b5afd163b8.html", mimetype="text/html")


@app.route("/api/leads", methods=["GET"])
def get_leads():
    leads = load_leads()

    # Query params for filtering
    category = request.args.get("category", "")
    locality = request.args.get("locality", "")
    no_website = request.args.get("no_website", "")
    status = request.args.get("status", "")
    search = request.args.get("search", "").strip().lower()

    filtered = leads
    if category:
        filtered = [l for l in filtered if l.get("category") == category]
    if locality:
        filtered = [l for l in filtered if l.get("locality") == locality]
    if no_website == "true":
        filtered = [l for l in filtered if not l.get("has_website")]
    if status:
        filtered = [l for l in filtered if l.get("status") == status]
    if search:
        filtered = [
            l for l in filtered
            if search in l.get("name", "").lower()
            or search in l.get("locality", "").lower()
            or search in l.get("phone", "").lower()
        ]

    # Stats calculation
    total = len(leads)
    no_web_count = sum(1 for l in leads if not l.get("has_website"))
    contacted_count = sum(1 for l in leads if l.get("status") in ["messaged", "follow_up", "converted"])
    converted_count = sum(1 for l in leads if l.get("status") == "converted")

    return jsonify({
        "status": "success",
        "total": len(filtered),
        "leads": filtered,
        "stats": {
            "total_leads": total,
            "no_website_leads": no_web_count,
            "contacted_leads": contacted_count,
            "converted_leads": converted_count
        }
    })


@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json or {}
    category = data.get("category", "Hotels & Stays")
    locality = data.get("locality", "Assi Ghat")
    max_results = int(data.get("max_results", 8))

    new_leads = run_live_scan(category, locality, max_results=max_results)
    return jsonify({
        "status": "success",
        "scanned_category": category,
        "scanned_locality": locality,
        "new_leads_found": len(new_leads),
        "leads": new_leads
    })


@app.route("/api/pitch/generate", methods=["POST"])
def pitch():
    data = request.json or {}
    lead_id = data.get("lead_id")
    language = data.get("language", "hinglish")
    sender_name = data.get("sender_name", "Varanasi Web Studio")

    leads = load_leads()
    lead = next((l for l in leads if l["id"] == lead_id), None)
    if not lead:
        return jsonify({"status": "error", "message": "Lead not found"}), 404

    message = generate_pitch(lead, language=language, sender_name=sender_name)
    wa_data = get_whatsapp_urls(lead.get("phone", ""), message)

    return jsonify({
        "status": "success",
        "lead_id": lead_id,
        "business_name": lead.get("name"),
        "language": language,
        "message": message,
        "phone": lead.get("phone"),
        "whatsapp_web": wa_data.get("web"),
        "whatsapp_direct": wa_data.get("direct"),
        "is_valid_phone": wa_data.get("valid")
    })


@app.route("/api/lead/update_status", methods=["POST"])
def update_status():
    data = request.json or {}
    lead_id = data.get("id")
    new_status = data.get("status")
    notes = data.get("notes")

    leads = load_leads()
    found = False
    for l in leads:
        if l["id"] == lead_id:
            if new_status:
                l["status"] = new_status
            if notes is not None:
                l["notes"] = notes
            found = True
            break

    if found:
        save_leads(leads)
        return jsonify({"status": "success", "message": "Lead updated successfully"})
    return jsonify({"status": "error", "message": "Lead not found"}), 404


@app.route("/api/lead/add", methods=["POST"])
def add_lead():
    data = request.json or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"status": "error", "message": "Business name is required"}), 400

    leads = load_leads()
    lead_id = f"vns-manual-{int(time.time())}"
    new_lead = {
        "id": lead_id,
        "name": name,
        "category": data.get("category", "General"),
        "locality": data.get("locality", "Varanasi"),
        "address": data.get("address", "Varanasi, UP"),
        "phone": data.get("phone", ""),
        "has_website": bool(data.get("has_website", False)),
        "website_url": data.get("website_url", ""),
        "rating": float(data.get("rating", 4.0)),
        "reviews_count": int(data.get("reviews_count", 10)),
        "pain_point": data.get("pain_point", "Needs custom website design."),
        "pitch_strategy": "Direct Outreach Pitch",
        "status": "new",
        "notes": data.get("notes", "Manually added lead"),
        "date_added": time.strftime("%Y-%m-%d")
    }

    leads.insert(0, new_lead)
    save_leads(leads)
    return jsonify({"status": "success", "lead": new_lead})


@app.route("/api/templates", methods=["GET"])
def get_templates():
    return jsonify(TEMPLATES)


@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    leads = load_leads()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Business Name", "Category", "Locality", "Address",
        "Phone", "Has Website", "Website URL", "Rating", "Reviews",
        "Pain Point", "Pitch Strategy", "Status", "Notes", "Date Added"
    ])

    for l in leads:
        writer.writerow([
            l.get("id"),
            l.get("name"),
            l.get("category"),
            l.get("locality"),
            l.get("address"),
            l.get("phone"),
            "YES" if l.get("has_website") else "NO (HOT TARGET)",
            l.get("website_url", ""),
            l.get("rating"),
            l.get("reviews_count"),
            l.get("pain_point"),
            l.get("pitch_strategy"),
            l.get("status"),
            l.get("notes"),
            l.get("date_added")
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=varanasi_website_leads.csv"}
    )


# -----------------------------------------------------------------------------
# AI Chat Assistant Engine for Deepak Kumar Tiwari's Portfolio
# -----------------------------------------------------------------------------
AI_SUGGESTIONS = [
    "💰 What are the website packages & pricing?",
    "💡 Why do you charge ₹15k–₹45k? (Cost Value)",
    "💍 Tell me about Wedding & Memory Portals",
    "🤝 Can we negotiate the budget?",
    "⚡ Why Next.js instead of WordPress?",
    "📞 How can I contact Deepak directly?"
]

def generate_local_ai_response(msg_lower):
    """Smart contextual response engine for client queries."""
    
    # 1. Cost Justification & Why We Charge That Much
    if ("why" in msg_lower and any(w in msg_lower for w in ["charge", "cost", "price", "rate", "much", "money"])) or any(k in msg_lower for k in ["why so much", "why charge", "why this cost", "cost justification", "expensive", "mehenga", "worth", "value", "roi", "satisf"]):
        return {
            "reply": """💡 **Why Our Pricing (₹15,000 – ₹45,000) Saves You Money & Delivers 10x ROI:**

Many agencies quote ₹3,000–₹5,000 for a broken WordPress template, then hit you with recurring server bills, broken plugins, and zero support. Here is why our bespoke Next.js engineering is an investment that actually saves you money:

• **🌐 3-Year Domain + Cloud Hosting Included (Saves ₹12,000+ upfront):** You pay ₹0 in server renewal bills for 36 full months!
• **🛠️ 1 Full Year Free Support & AMC (₹18,000 Value):** Direct WhatsApp & phone support for updates, maintenance, and bug fixes without monthly agency fees.
• **⚡ Sub-Second Speed (<0.8s) vs Slow WordPress (5s+):** Over 53% of mobile users leave slow websites. Next.js gives 95+ Google PageSpeed and is 100% immune to PHP malware.
• **📈 1–2 Client Deals Recover 100% of Cost:** With built-in WhatsApp lead capture, click-to-call, and Google Maps local SEO, just 1 or 2 new paying clients covers your entire investment!
• **🔑 100% Code & Asset Ownership:** Full GitHub repository handoff. No monthly rental fees like Wix or Shopify.
• **🛡️ 50/50 Milestone Safety:** You pay 50% advance to start, and the remaining 50% only after you review and approve the staging site before launch.

Would you like to discuss a custom package for your business?""",
            "suggestions": ["💰 View Pricing Packages", "🤝 Discuss Budget Negotiation", "📞 Talk to Deepak on WhatsApp"]
        }

    # 2. Negotiation, Discount & Budget Flexibility
    if any(k in msg_lower for k in ["negotiat", "discount", "budget", "kam", "flexible", "bargain", "payment term", "installment", "advance"]):
        return {
            "reply": """🤝 **Yes! We Have a Friendly Negotiation & Budget Flexibility Policy:**

We build long-term relationships, not rigid invoices. We understand every business, doctor, artisan, and family has unique financial milestones:

1. **Open for Friendly Discussion:** Deepak is directly accessible. If your budget is tight, we can adjust features or scope to match your comfort level.
2. **50/50 Milestone Payment:** You pay 50% advance to initiate architecture, and the balance 50% only after you test the live demo and are 100% satisfied.
3. **Phase-Wise Launch:** Start with essential core pages now within your budget, and add advanced add-ons later as your revenue increases!

Feel free to connect directly with Deepak on WhatsApp (+91 6204643184) to discuss a win-win budget!""",
            "suggestions": ["💬 Chat with Deepak on WhatsApp", "💰 View Pricing Menu", "⚡ Why Choose Next.js?"]
        }

    # 3. Wedding, Birthday & Memory Celebration Portals
    if any(k in msg_lower for k in ["wedding", "shaadi", "vivah", "patrika", "marriage", "birthday", "memory", "memorial", "anniversary", "celebrat", "shagun", "rsvp"]):
        return {
            "reply": """💍 **Luxury Wedding, Birthday & Memory Celebration Portals:**

Why spend ₹25,000 on paper wedding cards that get thrown away? Give your guests a luxury digital celebration hub:

• **💌 Interactive WhatsApp RSVP:** Guests confirm headcount and dietary preferences directly into WhatsApp.
• **📍 Multi-Event GPS Route Navigation:** Haldi, Mehendi, Sangeet, Shaadi & Reception with 1-tap Google Maps driving directions.
• **🎬 Cinematic Pre-Wedding Reels:** High-resolution couple gallery, love story timeline, and embedded drone video player.
• **🎁 UPI Shagun QR Code:** Relatives across the world can scan a custom QR code to send Shagun safely to your bank.
• **🕊️ Live Digital Blessings Wall & Guestbook:** Relatives and friends post photos and heartfelt blessings in real-time.
• **📱 Vector QR Code for Printed Cards:** Print-ready QR code for your paper invitations.

**Investment Tiers:**
• *Milestone Birthday & Tribute Portal:* **₹ 8,999** (2–3 days delivery)
• *Grand Royal Wedding Hub:* **₹ 14,999 – ₹ 18,999** (4–5 days delivery, 3-year cloud archive)""",
            "suggestions": ["💍 Book Royal Wedding Portal", "🎂 Book Birthday Portal", "📞 Talk to Deepak on WhatsApp"]
        }

    # 4. Pricing, Rates & Packages
    if any(k in msg_lower for k in ["price", "pricing", "package", "cost", "rate", "menu", "charge", "kitna", "fees", "how much"]):
        return {
            "reply": """💎 **Transparent Web & Software Pricing Packages:**

1. **Starter Business (₹ 14,999 | 3–5 Days):**
   • 3 to 5 custom Next.js pages
   • 1 Year Domain + Fast Edge Hosting + SSL included
   • WhatsApp lead capture, click-to-call & Google Maps
   • 6 Months free support

2. **Growth & Lead Engine ⭐ (₹ 21,000 – ₹ 24,999 | 5–7 Days):**
   • **3 Full Years of Domain & Global Cloud Hosting Included!**
   • 5 to 8 bespoke Next.js 16 pages with luxury glassmorphic UX
   • Appointment & consultation booking engine
   • Google SEO rich snippets + Search Console verification
   • Professional vector logo included + 1 Year Free AMC

3. **Enterprise & E-Commerce (₹ 34,999 – ₹ 45,000 | 10–14 Days):**
   • Razorpay/UPI payment gateway, custom CRM admin panel & database
   • Audio player, video reels, or full catalog cart

4. **Native Mobile App (React Native):** ₹ 25,000 – ₹ 55,000

All packages come with full GitHub source code ownership and 50/50 milestone payments!""",
            "suggestions": ["💡 Why Our Pricing Delivers 10x ROI", "🤝 Discuss Budget Negotiation", "🧮 Use Interactive Calculator"]
        }

    # 5. Mobile App Development
    if any(k in msg_lower for k in ["app", "mobile app", "android", "ios", "react native", "play store", "apk"]):
        return {
            "reply": """📱 **Cross-Platform Android & iOS Mobile App Development:**

We engineer high-performance mobile apps using **React Native**, sharing your website's database, customer accounts, and real-time orders:

• Single codebase for Android & iOS (saves 50% development cost)
• Push notifications for offers and booking updates
• Real-time database synchronization & offline storage
• Google Play Store & Apple App Store deployment readiness
• Investment: **₹ 25,000 – ₹ 55,000** based on feature complexity.

Would you like to build a mobile app companion for your business?""",
            "suggestions": ["📞 Inquire About Mobile App", "💰 View Full Pricing Menu", "🤝 Discuss Budget"]
        }

    # 6. Technology & Why Next.js
    if any(k in msg_lower for k in ["next", "nextjs", "next.js", "wordpress", "tech", "react", "speed", "stack", "technology", "slow"]):
        return {
            "reply": """⚡ **Why Handcrafted Next.js vs Generic WordPress:**

• **Sub-Second Speed (<0.8s):** Next.js pre-renders pages at the edge, achieving a 95+ score on Google PageSpeed. WordPress takes 4–6+ seconds and loses visitors.
• **100% Hack-Proof & Secure:** Zero PHP vulnerabilities, zero malicious plugins, bank-grade SSL security.
• **Superior Google SEO:** Server-Side Rendering (SSR) ensures Google bots instantly index every keyword and rich snippet.
• **Fluid 60FPS Micro-Animations:** Apple-grade glassmorphic design and reactive user experiences that build instant brand trust.""",
            "suggestions": ["💡 Why Our Pricing Delivers 10x ROI", "💼 View Live Projects", "💰 View Pricing Packages"]
        }

    # 7. Live Projects & Showcase
    if any(k in msg_lower for k in ["project", "work", "portfolio", "sample", "example", "client", "case study", "arl", "advocate", "dharohar"]):
        return {
            "reply": """🚀 **Deepak's Live Production Projects:**

1. **🎵 ARL Music Production Studio (arlmusicproduction.com):**
   • Flagship music studio web application featuring an interactive 432Hz ambient audio player, service inquiry funnels, and dark studio aesthetic.

2. **⚖️ New Zen Advocate / MK Associates (newzenadvocate.com):**
   • High-converting legal consultation portal for Adv. Madan Kumar Upadhyay & Adv. Madhvesh Upadhyay (Delhi, Varanasi & Kaimur). Includes WhatsApp appointment booking & LegalService Google Schema.

3. **✨ Dharohar Banarasi (dharoharbanarasi.com):**
   • Luxury e-commerce showcase celebrating authentic handloom Banarasi silk sarees with high-res zoom galleries and WhatsApp lead engine.

You can inspect all live links directly on this portfolio!""",
            "suggestions": ["💰 View Pricing Packages", "💡 Why Our Pricing Delivers 10x ROI", "📞 Contact Deepak"]
        }

    # 8. Contact & Hiring Details
    if any(k in msg_lower for k in ["contact", "phone", "call", "whatsapp", "email", "address", "location", "hire", "meet", "varanasi", "kashi"]):
        return {
            "reply": """📞 **Get in Touch with Deepak Kumar Tiwari:**

• **WhatsApp & Direct Call:** [+91 6204643184](https://wa.me/916204643184)
• **Email:** [deepaksolot@gmail.com](mailto:deepaksolot@gmail.com)
• **Location:** Varanasi (Kashi), Uttar Pradesh, India
• **Availability:** Mon – Sat, 9:00 AM – 9:00 PM IST (WhatsApp replies within 15 minutes!)

Feel free to click the WhatsApp button to start a friendly, no-obligation discussion!""",
            "suggestions": ["💬 Open WhatsApp Chat", "💰 View Pricing Menu", "🤝 Discuss Budget Negotiation"]
        }

    # 9. Timeline & Delivery
    if any(k in msg_lower for k in ["how long", "timeline", "time", "days", "delivery", "kab tak", "kitna din"]):
        return {
            "reply": """⏱️ **Project Delivery Timelines:**

• **Starter Business:** 3 to 5 business days
• **Growth & Lead Engine:** 5 to 7 business days
• **Enterprise / E-Commerce:** 10 to 14 business days
• **Wedding Portal:** 4 to 5 business days
• **Birthday / Celebration Portal:** 2 to 3 business days
• **Mobile App (React Native):** 2 to 3 weeks

We provide daily progress previews via private staging links so you see your website coming to life!""",
            "suggestions": ["💰 View Pricing Packages", "🤝 Discuss Milestone Payments", "📞 Talk to Deepak"]
        }

    # Default friendly greeting / general query
    return {
        "reply": """Namaste! 🙏 I am **Deepak's AI Concierge**.

I can help you with:
• **Pricing & Rates:** Packages from ₹14,999 to ₹45,000+
• **Cost Value Breakdown:** Why our 3-year hosting + 1-year AMC saves you ₹12,000+
• **Budget Flexibility:** Friendly negotiation & 50/50 milestone payment
• **Celebration Portals:** Royal wedding invitations, WhatsApp RSVP, and UPI Shagun
• **Next.js Benefits:** Sub-second speed and zero WordPress malware
• **Live Projects:** ARL Music, New Zen Advocate & Dharohar Banarasi

What type of project or question would you like to explore?""",
        "suggestions": AI_SUGGESTIONS
    }


@app.route("/api/ai-chat", methods=["POST"])
def ai_chat():
    data = request.json or {}
    user_msg = (data.get("message") or "").strip()
    
    if not user_msg:
        return jsonify({
            "status": "success",
            "reply": "Namaste! 🙏 How can I assist you with your website, app, or celebration portal today?",
            "suggestions": AI_SUGGESTIONS
        })

    # Optional: If GEMINI_API_KEY is configured, try Google Gemini first
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import urllib.request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "system_instruction": {
                    "parts": [{"text": (
                        "You are Deepak Kumar Tiwari's professional AI Assistant for his software and web development portfolio in Varanasi, India. "
                        "You represent Deepak (+91 6204643184, deepaksolot@gmail.com). "
                        "Pricing: Starter ₹14,999 (3-5 days), Growth Pro ₹21,000-₹24,999 (3 years hosting + 1 year AMC included), Enterprise ₹34,999+, "
                        "Wedding Portal ₹14,999-₹18,999 (WhatsApp RSVP, GPS maps, UPI Shagun, Blessings Wall), Birthday Portal ₹8,999. "
                        "Explain cost value (3-year hosting included saves ₹12k, 1 year AMC included saves ₹18k, Next.js speed <0.8s, 1-2 clients covers cost). "
                        "Always mention friendly negotiation and 50/50 milestone payments. "
                        "Keep responses polite, formatted with bullet points, and invite them to connect on WhatsApp."
                    )}]
                },
                "contents": [{"parts": [{"text": user_msg}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({
                    "status": "success",
                    "reply": text,
                    "suggestions": ["💬 Talk to Deepak on WhatsApp", "💰 View Pricing Packages", "🤝 Discuss Budget"]
                })
        except Exception:
            pass  # Seamlessly fall back to rich local knowledge engine

    # Fast, reliable knowledge engine response
    res = generate_local_ai_response(user_msg.lower())
    return jsonify({
        "status": "success",
        "reply": res["reply"],
        "suggestions": res.get("suggestions", AI_SUGGESTIONS)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)

