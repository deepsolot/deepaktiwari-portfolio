import urllib.parse
import re

SENDER_PROFILE = {
    "name": "Deepak Kumar Tiwari",
    "phone": "6204643184",
    "email": "deepaksolot@gmail.com",
    "linkedin": "https://www.linkedin.com/in/deepak-tiwari-ba9803257/",
    "github": "https://github.com/deepsolot",
    "portfolio": [
        {"name": "ARL Music Production", "url": "https://arlmusicproduction.com/"},
        {"name": "Dharohar Banarasi", "url": "https://dharoharbanarasi.com/"},
        {"name": "New Zen Advocate", "url": "https://newzenadvocate.com/"}
    ]
}

SIGNATURE = """Regards,
Deepak Kumar Tiwari
📞 6204643184
📧 deepaksolot@gmail.com
🔗 LinkedIn: https://www.linkedin.com/in/deepak-tiwari-ba9803257/
💻 GitHub: https://github.com/deepsolot"""

TEMPLATES = {
    "Deepak Official": {
        "followup": """Hello {owner_name_or_sir},

Thank you for speaking with me. As discussed, I’m reaching out regarding professional website development for *{business_name}* ({locality}, Varanasi).

We create modern, fast, mobile-friendly and professional websites using Next.js, a modern web technology that helps deliver:

• ⚡ Fast loading and smooth performance
• 📱 Fully responsive design for mobile, tablet & desktop
• 🔍 SEO-friendly structure to improve Google visibility
• 🎨 Modern and premium UI tailored to your brand
• 🔒 Secure and reliable website setup
• 📈 Better online presence and customer reach
• 📞 WhatsApp, Call, Contact Forms & Google Maps integration
• 🚀 Scalable website that can grow with your business

How a Website Can Help Your Business

A professional website helps customers find your business online, understand your services, view your work, contact you easily, and build trust before making a purchase or enquiry.

We handle the complete process — design → development → content setup → testing → deployment → basic SEO — so you receive a ready-to-use website.

Our Recent Projects

🌐 ARL Music Production (Cinematic Studio & Audio Platform):
https://arlmusicproduction.com/

🌐 Dharohar Banarasi (Banarasi Handloom Store):
https://dharoharbanarasi.com/

🌐 New Zen Advocate (Legal Consultation Portal):
https://newzenadvocate.com/

You can visit these websites to see examples of our work.

If you’re interested, I’d be happy to discuss your requirements and suggest a website structure suitable for your business.

""" + SIGNATURE,

        "cold_pitch": """Hello {owner_name_or_sir} 🙏

I came across *{business_name}* in {locality}, Varanasi and noticed you don't have an official direct website yet.

We develop fast, modern, mobile-friendly websites using Next.js to help local businesses gain direct online inquiries, rank on Google Maps, and avoid heavy third-party aggregator commissions.

Recent live projects built by us:
🌐 ARL Music Production (Cinematic Studio & Audio Platform):
https://arlmusicproduction.com/

🌐 Dharohar Banarasi (Banarasi Handloom Store):
https://dharoharbanarasi.com/

🌐 New Zen Advocate (Legal Consultation Portal):
https://newzenadvocate.com/

We can design and launch a complete, ready-to-use website for *{business_name}* within 48 hours.

Would you be open to a quick 2-minute chat or reviewing a free demo design preview for your business?

""" + SIGNATURE,

        "hinglish": """नमस्ते {owner_name_or_sir} जी 🙏

मैंने देखा कि वाराणसी में आपके प्रतिष्ठान *{business_name}* ({locality}) की प्रतिष्ठा बहुत अच्छी है! 🌟

आजकल 80% से ज्यादा ग्राहक किसी भी होटल, रेस्टोरेंट या शॉप पर जाने से पहले Google पर सर्च करते हैं। बिना वेबसाइट के बिजनेस को बिचौलियों और ऍप्स को 20-30% कमीशन देना पड़ता है।

हम Next.js टेक्नोलॉजी पर सुपर-फास्ट, मॉडर्न वेबसाइट बनाते हैं:
⚡ बिजली जैसी तेज स्पीड और मोबाइल रिस्पॉन्सिव
🔍 Google और Google Maps पर टॉप रैंकिंग (Local SEO)
📲 1-Click WhatsApp व Direct Calling बटन
💳 डायरेक्ट UPI / ऑनलाइन पेमेंट सुविधा

हमारे द्वारा बनाए गए हालिया लाइव प्रोजेक्ट्स:
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/
🌐 New Zen Advocate: https://newzenadvocate.com/

हम आपके बिज़नेस *{business_name}* के लिए मात्र 48 घंटे में रेडी-टू-यूज़ वेबसाइट तैयार कर सकते हैं।

क्या मैं आपको एक फ्री डेमो वेबसाइट डिज़ाइन भेज सकता हूँ?

""" + SIGNATURE,

        "hindi": """प्रणाम {owner_name_or_sir} जी 🙏, जय श्री काशी विश्वनाथ!

आशा है कि वाराणसी ({locality}) में आपका प्रतिष्ठान *{business_name}* उत्तम चल रहा होगा।

आज के डिजिटल युग में अपनी व्यक्तिगत वेबसाइट होने से ग्राहक सीधे आपसे जुड़ते हैं और बिचौलियों को 20-25% कमीशन नहीं देना पड़ता।

हम आधुनिक Next.js तकनीक पर वेबसाइट तैयार करते हैं जो अत्यंत तीव्र, सुरक्षित और Google पर आसानी से खोजी जा सकने योग्य होती हैं।

हमारे लाइव प्रोजेक्ट्स:
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/
🌐 New Zen Advocate: https://newzenadvocate.com/

क्या हम *{business_name}* के लिए एक निःशुल्क वेबसाइट डेमो साझा कर सकते हैं?

""" + SIGNATURE
    },

    "Hotels & Stays": {
        "deepak_followup": """Hello {owner_name_or_sir},

Thank you for speaking with me. As discussed, I’m reaching out regarding professional direct-booking website development for *{business_name}* ({locality}, Varanasi).

We create modern, fast, mobile-friendly websites using Next.js tailored for hotels & homestays:
• ⚡ Fast loading room showcase with HD photos
• 💰 Zero Commission Direct Bookings (Save 20-30% OTA commission)
• 📱 1-Click WhatsApp Booking & Direct UPI payments
• 🔍 Top Google Maps & Local Search visibility
• 📞 Contact forms, Call buttons & Location Map

Recent live projects:
🌐 New Zen Advocate: https://newzenadvocate.com/
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/

We can deliver a fully functional, ready-to-use booking website for {business_name} within 48 hours.

Looking forward to connecting!

""" + SIGNATURE,

        "hinglish": """नमस्ते {owner_name_or_sir} जी 🙏

मैंने देखा कि वाराणसी में आपके होटल *{business_name}* ({locality}) की रेटिंग और प्रतिष्ठा बहुत अच्छी है! 🌟

लेकिन अभी आपके पास अपनी *डायरेक्ट बुकिंग वेबसाइट* नहीं है। आजकल OYO, MakeMyTrip और Booking.com हर कमरे की बुकिंग पर 20% से 30% तक मोटा कमीशन काट लेते हैं! 💸

अगर आपके पास अपनी मॉडर्न Next.js वेबसाइट होगी तो:
✅ टूरिस्ट और भक्तगण सीधे आपकी वेबसाइट से रूम बुक करेंगे (Zero Commission!)
✅ सीधे आपके बैंक खाते / UPI में एडवांस पेमेंट आएगा
✅ Google Maps पर होटल सर्च करने पर सबसे ऊपर दिखेगा
✅ WhatsApp पर 1-Click रूम इन्क्वायरी बटन

हमारे लाइव प्रोजेक्ट्स:
🌐 New Zen Advocate: https://newzenadvocate.com/
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/

हम वाराणसी के होटलों के लिए मात्र 48 घंटे में प्रीमियम वेबसाइट तैयार करते हैं। 🚀
क्या मैं आपको एक *फ्री डेमो वेबसाइट डिज़ाइन* भेज सकता हूँ?

""" + SIGNATURE,

        "english": """Hello {owner_name_or_sir} 🙏

I noticed your wonderful property *{business_name}* in {locality}, Varanasi.

Did you know that relying only on OTAs costs you 20-30% in commissions on every booking?

We build high-converting direct booking websites using Next.js:
• Direct Online Booking Engine (Zero Commission)
• Direct UPI / Card payments into your bank account
• Google Maps Top Ranking (Local SEO)
• 1-Click WhatsApp Booking Integration

Recent live projects:
🌐 New Zen Advocate: https://newzenadvocate.com/
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/

Can I share a quick free demo link for {business_name}?

""" + SIGNATURE
    },

    "Restaurants & Cafes": {
        "deepak_followup": """Hello {owner_name_or_sir},

Thank you for speaking with me. As discussed, I’m reaching out regarding a modern digital menu & ordering website for *{business_name}* ({locality}, Varanasi).

Built with Next.js for high-speed performance:
• 🍕 Interactive Digital QR Menu & Food Showcase
• 💰 Zero Commission direct orders (Save 25-30% on Swiggy/Zomato)
• 📲 WhatsApp Table & Party Reservations
• 🔍 High Google Local ranking for food searches in Varanasi

Recent live work:
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/
🌐 New Zen Advocate: https://newzenadvocate.com/

I’d be glad to discuss your requirements and share a demo layout for your restaurant.

""" + SIGNATURE,

        "hinglish": """नमस्ते {owner_name_or_sir} जी 🙏

वाराणसी में आपके रेस्टोरेंट/कैफे *{business_name}* ({locality}) का खाना बहुत पसंद किया जाता है! 🍽️✨

क्या आप जानते हैं कि Swiggy और Zomato हर ऑनलाइन ऑर्डर पर 25-30% कमीशन लेते हैं? 
अगर आपके पास अपनी डिजिटल Next.js वेबसाइट होगी तो:
🍕 ग्राहक बिना किसी कमीशन के सीधे आपके मेनू से ऑनलाइन ऑर्डर करेंगे
📲 टेबल और पार्टी बुकिंग सीधे WhatsApp पर आएगी
⭐ Google Search पर आपका डिजिटल QR मेनू सबसे ऊपर दिखेगा
💳 पेमेंट सीधे आपके बैंक / QR कोड में आएगा

हमारे लाइव प्रोजेक्ट्स:
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/
🌐 New Zen Advocate: https://newzenadvocate.com/

क्या मैं आपको एक फ्री सैंपल मेनू वेबसाइट दिखा सकता हूँ? 📲

""" + SIGNATURE,

        "english": """Hello {owner_name_or_sir} 🙏

I love the great reputation of *{business_name}* in {locality}, Varanasi! 🍲

Having your own direct ordering website saves 25-30% commissions charged by delivery aggregators:
• Interactive Digital QR Menu
• Direct Table & Event Reservations
• Direct WhatsApp Food Orders & UPI Payments
• Local Google Food Search Optimization

Recent live projects:
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/
🌐 New Zen Advocate: https://newzenadvocate.com/

Can I send you a quick free demo preview? Thank you!

""" + SIGNATURE
    },

    "Banarasi Silk & Sarees": {
        "deepak_followup": """Hello {owner_name_or_sir},

Thank you for speaking with me. As discussed, I’m reaching out regarding e-commerce & digital catalog development for *{business_name}* ({locality}, Varanasi).

We specialize in Varanasi handloom and saree websites (developed with modern Next.js technology):
• 🥻 High-Definition Bridal & Handloom Saree Catalog
• 🌐 Pan-India & Global Customer Reach (Sell directly to Delhi, Mumbai, USA, UAE)
• 📲 WhatsApp Catalog integration for instant bridal consultations
• 💳 Direct UPI & international card payment gateways

We recently built and launched:
🌐 Dharohar Banarasi (Authentic Banarasi Saree & Handloom Store):
https://dharoharbanarasi.com/

You can visit Dharohar Banarasi to see how we showcase Banarasi silks online.

We can create a similar ready-to-sell online store for {business_name}.

""" + SIGNATURE,

        "hinglish": """प्रणाम {owner_name_or_sir} जी 🙏 (जय श्री काशी विश्वनाथ)

वाराणसी ({locality}) में आपके प्रतिष्ठान *{business_name}* की असली बनारसी साड़ियों का काम बहुत प्रतिष्ठित है! 🥻✨

आजकल मुंबई, दिल्ली, बैंगलोर और विदेशों से लोग असली बनारसी साड़ियां ऑनलाइन खरीदना चाहते हैं। अपनी ई-कॉमर्स वेबसाइट होने पर आप सीधे रिटेल और होलसेल ऑर्डर ले सकते हैं।

हमने हाल ही में बनारसी साड़ियों के लिए यह लाइव स्टोर तैयार किया है:
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/
🌐 New Zen Advocate: https://newzenadvocate.com/

हम आपके प्रतिष्ठान *{business_name}* के लिए भी ऐसा ही खूबसूरत ऑनलाइन कैटलॉग मात्र 48 घंटे में बना सकते हैं।

क्या मैं आपको एक फ्री डेमो कैटलॉग दिखा सकता हूँ?

""" + SIGNATURE,

        "english": """Namaste {owner_name_or_sir} 🙏

I came across your renowned silk boutique *{business_name}* located in {locality}, Varanasi. 🥻

With your own digital boutique:
• Showcase full bridal and handloom collections in HD
• Reach customers across India and worldwide
• Accept direct online payments (UPI, Cards, International)

See our recent live work for Varanasi handloom:
🌐 Dharohar Banarasi: https://dharoharbanarasi.com/
🌐 New Zen Advocate: https://newzenadvocate.com/

Could I share a complimentary demo design tailored for your saree collection?

""" + SIGNATURE
    }
}


def clean_phone_number(raw_phone):
    """Normalizes phone to 10-digit or 91XXXXXXXXXX standard for WhatsApp."""
    if not raw_phone:
        return ""
    digits = re.sub(r"\D", "", str(raw_phone))
    
    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    
    if len(digits) == 10:
        return f"91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        return digits
    elif len(digits) > 10 and digits.startswith("91"):
        return digits[:12]
    
    return digits


def generate_pitch(lead, language="followup", sender_name="Deepak Kumar Tiwari"):
    """Generates customized pitch for a lead based on template category and chosen language/style."""
    category = lead.get("category", "General")
    
    # Check if category-specific group exists
    cat_key = "Deepak Official"
    if "Hotel" in category or "Stay" in category or "Guest" in category:
        cat_key = "Hotels & Stays"
    elif "Restaurant" in category or "Cafe" in category or "Food" in category:
        cat_key = "Restaurants & Cafes"
    elif "Silk" in category or "Saree" in category or "Handloom" in category:
        cat_key = "Banarasi Silk & Sarees"
    
    template_group = TEMPLATES.get(cat_key, TEMPLATES["Deepak Official"])
    
    # Fallback to Deepak Official if the specific key doesn't have the selected template
    if language not in template_group:
        template_group = TEMPLATES["Deepak Official"]
        
    template = template_group.get(language, template_group.get("followup", template_group.get("hinglish")))
    
    # Fill variables
    business_name = lead.get("name", "आपके व्यवसाय")
    locality = lead.get("locality", "Varanasi")
    owner_name = lead.get("owner_name", "Sir/Ma’am")
    
    msg = template.format(
        business_name=business_name,
        locality=locality,
        owner_name_or_sir=owner_name,
        sender_name=sender_name
    )
    return msg


def get_whatsapp_urls(phone, message):
    """Generates both WhatsApp Web and WhatsApp Mobile deep links."""
    clean_p = clean_phone_number(phone)
    if not clean_p:
        return {"web": "", "direct": "", "valid": False}
        
    encoded_msg = urllib.parse.quote(message)
    web_url = f"https://web.whatsapp.com/send?phone={clean_p}&text={encoded_msg}"
    direct_url = f"https://wa.me/{clean_p}?text={encoded_msg}"
    
    return {
        "clean_phone": clean_p,
        "web": web_url,
        "direct": direct_url,
        "valid": True
    }
