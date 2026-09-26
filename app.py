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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
