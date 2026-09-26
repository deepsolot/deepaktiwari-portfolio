#!/usr/bin/env python3
"""
KashiBiz Automated CLI Outreach Tool
====================================
Quick command-line interface to search Varanasi businesses lacking websites,
view phone contacts, and generate 1-click WhatsApp pitch links.

Usage:
    python auto_outreach_cli.py --list
    python auto_outreach_cli.py --category "Hotels & Stays"
    python auto_outreach_cli.py --scan --category "Hotels & Stays" --locality "Assi Ghat"
    python auto_outreach_cli.py --pitch vns-001 --lang hinglish
"""

import argparse
import sys
import webbrowser
from scraper import load_leads, run_live_scan, VARANASI_LOCALITIES, CATEGORIES
from outreach_engine import generate_pitch, get_whatsapp_urls


def print_banner():
    print("""
==================================================================
  🚩 KashiBiz: Varanasi Lead Finder & Automated Website Pitcher 🚩
==================================================================
    """)


def list_leads(leads, no_web_only=True):
    filtered = [l for l in leads if not l.get("has_website")] if no_web_only else leads
    print(f"Total Leads Found: {len(filtered)} (Showing 'No Website' high-priority targets)")
    print("-" * 75)
    print(f"{'ID':<10} | {'Category':<18} | {'Locality':<14} | {'Phone':<15} | {'Business Name'}")
    print("-" * 75)
    for l in filtered:
        print(f"{l.get('id', ''):<10} | {l.get('category', ''):<18} | {l.get('locality', ''):<14} | {l.get('phone', 'N/A'):<15} | {l.get('name', '')}")
    print("-" * 75)


def show_pitch(lead_id, lang="hinglish", auto_open=False):
    leads = load_leads()
    lead = next((l for l in leads if l["id"] == lead_id), None)
    if not lead:
        print(f"❌ Error: Lead ID '{lead_id}' not found.")
        return

    msg = generate_pitch(lead, language=lang)
    wa_info = get_whatsapp_urls(lead.get("phone", ""), msg)

    print(f"\n🎯 Target Business: {lead.get('name')} ({lead.get('category')} - {lead.get('locality')})")
    print(f"📱 Phone: {lead.get('phone')} (Cleaned for WhatsApp: +{wa_info.get('clean_phone')})")
    print(f"🌐 Website Status: {'Has Website' if lead.get('has_website') else 'NO WEBSITE (Hot Target!)'}")
    print(f"\n--- [Generated WhatsApp Pitch ({lang.upper()})] ---")
    print(msg)
    print("--------------------------------------------------")
    print(f"\n🔗 WhatsApp Web Link:\n{wa_info.get('web')}\n")

    if auto_open and wa_info.get("web"):
        print("🚀 Opening WhatsApp Web in browser...")
        webbrowser.open(wa_info.get("web"))


def main():
    parser = argparse.ArgumentParser(description="KashiBiz Varanasi Business Lead & Outreach Automation")
    parser.add_argument("--list", action="store_true", help="List businesses without websites")
    parser.add_argument("--all", action="store_true", help="List all businesses including those with websites")
    parser.add_argument("--category", type=str, help="Filter by category (e.g. 'Hotels & Stays')")
    parser.add_argument("--locality", type=str, help="Filter by Varanasi locality (e.g. 'Assi Ghat')")
    parser.add_argument("--scan", action="store_true", help="Run live web scraper for new businesses")
    parser.add_argument("--pitch", type=str, help="Lead ID to generate WhatsApp pitch for (e.g. vns-001)")
    parser.add_argument("--lang", type=str, default="followup", choices=["followup", "cold_pitch", "hinglish", "hindi", "english"], help="Pitch template/language")
    parser.add_argument("--send", action="store_true", help="Auto open WhatsApp Web for the pitched lead")

    args = parser.parse_args()
    print_banner()

    leads = load_leads()

    if args.scan:
        cat = args.category or "Hotels & Stays"
        loc = args.locality or "Assi Ghat"
        print(f"🔍 Scanning Varanasi for '{cat}' in '{loc}'...")
        new_leads = run_live_scan(cat, loc, max_results=8)
        print(f"✅ Scan complete! Found {len(new_leads)} new business leads.")
        list_leads(load_leads())
        return

    if args.pitch:
        show_pitch(args.pitch, lang=args.lang, auto_open=args.send)
        return

    if args.category:
        leads = [l for l in leads if args.category.lower() in l.get("category", "").lower()]
    if args.locality:
        leads = [l for l in leads if args.locality.lower() in l.get("locality", "").lower()]

    list_leads(leads, no_web_only=not args.all)


if __name__ == "__main__":
    main()
