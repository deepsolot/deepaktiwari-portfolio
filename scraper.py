import json
import os
import re
import time
import urllib.parse
from ddgs import DDGS

LEADS_FILE = os.path.join(os.path.dirname(__file__), "leads_db.json")

# Core localities in Varanasi
VARANASI_LOCALITIES = [
    "Assi Ghat",
    "Godowlia",
    "Dashashwamedh",
    "Sigra",
    "Lanka",
    "Cantonment",
    "Chowk",
    "Bhelupur",
    "Durgakund",
    "Sarnath",
    "Pandeypur"
]

# Business categories
CATEGORIES = [
    "Hotels & Stays",
    "Restaurants & Cafes",
    "Banarasi Silk & Sarees",
    "Tours & Travels",
    "Healthcare & Clinics",
    "Education & Coaching"
]


def load_leads():
    """Loads existing leads from JSON DB with Vercel /tmp fallback."""
    tmp_file = "/tmp/leads_db.json"
    if os.path.exists(tmp_file):
        try:
            with open(tmp_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    if not os.path.exists(LEADS_FILE):
        return []
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {LEADS_FILE}: {e}")
        return []


def save_leads(leads):
    """Saves leads array to JSON DB with /tmp fallback on read-only serverless."""
    try:
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Standard save failed, attempting /tmp save: {e}")
        try:
            with open("/tmp/leads_db.json", "w", encoding="utf-8") as f:
                json.dump(leads, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e2:
            print(f"Error saving to /tmp: {e2}")
            return False


def extract_phone_numbers(text):
    """Finds Indian mobile numbers (+91...) or landlines in Varanasi."""
    if not text:
        return []
    # Pattern for 10-digit mobile starting with 6-9, optional +91 or 0 prefix
    pattern = r"(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}|0542[\s-]?\d{6,7}"
    matches = re.findall(pattern, text)
    cleaned = []
    for m in matches:
        digits = re.sub(r"[\s-]", "", m)
        if len(digits) >= 10:
            if not digits.startswith("+91") and len(digits) == 10:
                digits = f"+91{digits}"
            elif digits.startswith("91") and len(digits) == 12:
                digits = f"+{digits}"
            cleaned.append(digits)
    return list(dict.fromkeys(cleaned))


def is_third_party_domain(url):
    """Checks if the URL is an aggregator rather than a proprietary website."""
    aggregators = [
        "justdial.com", "tripadvisor", "booking.com", "makemytrip.com",
        "goibibo.com", "zomato.com", "swiggy.com", "indiamart.com",
        "facebook.com", "instagram.com", "tradeindia.com", "magicbricks.com",
        "housing.com", "eazydiner.com", "dineout.co.in", "yatradham.org",
        "trip.com", "agoda.com", "skyscanner", "yellowpages"
    ]
    url_lower = url.lower()
    return any(agg in url_lower for agg in aggregators)


def clean_business_title(title):
    """Removes platform suffixes from titles like '... - Justdial' or '... | Zomato'."""
    title = re.sub(r"\s*[-|–]\s*(?:Justdial|Zomato|Tripadvisor|Booking\.com|MakeMyTrip|Trip\.com|Phone Number|Photos).*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^(?:Book|Top|Best|The 10 Best|20\+ Best)\s+", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+in\s+Varanasi.*$", "", title, flags=re.IGNORECASE)
    return title.strip()


def run_live_scan(category, locality, max_results=10):
    """Runs a live search query across Varanasi for the selected category and locality."""
    existing_leads = load_leads()
    existing_names = {l["name"].strip().lower() for l in existing_leads}
    existing_phones = {re.sub(r"\D", "", l.get("phone", "")) for l in existing_leads if l.get("phone")}

    # Craft targeted search queries
    term_map = {
        "Hotels & Stays": "hotel OR \"guest house\" OR homestay",
        "Restaurants & Cafes": "restaurant OR cafe OR bakery",
        "Banarasi Silk & Sarees": "banarasi saree showroom OR silk weavers",
        "Tours & Travels": "tour travel boat booking Varanasi",
        "Healthcare & Clinics": "clinic doctor hospital",
        "Education & Coaching": "coaching institute classes"
    }
    
    query_term = term_map.get(category, "business")
    search_query = f"{query_term} \"{locality}\" Varanasi contact phone"

    print(f"Executing search: {search_query}")
    new_found = []

    try:
        ddgs = DDGS()
        results = list(ddgs.text(search_query, max_results=max_results))
    except Exception as e:
        print(f"DDGS search error: {e}")
        results = []

    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        full_text = f"{title} {body}"

        phones = extract_phone_numbers(full_text)
        if not phones:
            continue

        raw_phone = phones[0]
        phone_digits = re.sub(r"\D", "", raw_phone)
        if phone_digits in existing_phones:
            continue

        clean_name = clean_business_title(title)
        if len(clean_name) < 4 or clean_name.lower() in existing_names:
            continue

        # Check if they have an independent website
        has_own_website = False
        website_url = ""
        if href and not is_third_party_domain(href):
            has_own_website = True
            website_url = href

        # Create new lead object
        lead_id = f"vns-scan-{int(time.time())}-{len(new_found)+1}"
        new_lead = {
            "id": lead_id,
            "name": clean_name,
            "category": category,
            "locality": locality,
            "address": f"Near {locality}, Varanasi",
            "phone": raw_phone,
            "has_website": has_own_website,
            "website_url": website_url,
            "rating": 4.2,
            "reviews_count": 45,
            "pain_point": "Needs a direct digital website to avoid commissions and capture direct tourist bookings." if not has_own_website else "Has a basic website, can be pitched a high-speed redesign.",
            "pitch_strategy": f"{category} Direct Digital Presence Pitch",
            "status": "new",
            "notes": f"Discovered via live scan on {time.strftime('%Y-%m-%d %H:%M')}",
            "date_added": time.strftime("%Y-%m-%d")
        }

        new_found.append(new_lead)
        existing_names.add(clean_name.lower())
        existing_phones.add(phone_digits)

    # Append to existing DB
    if new_found:
        existing_leads.extend(new_found)
        save_leads(existing_leads)

    return new_found
