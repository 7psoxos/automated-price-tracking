#!/usr/bin/env python3
"""
Price Tracking System for Vapestation
Monitors Greek vape competitor prices via web scraping
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

# Competitors to track (Greek vape shops)
COMPETITORS = [
    {
        "id": "e-smokers",
        "name": "E-Smokers.gr",
        "url": "https://www.e-smokers.gr",
        "category": "retail_competitor"
    },
    {
        "id": "atmology",
        "name": "Atmology.gr",
        "url": "https://atmology.gr",
        "category": "retail_competitor"
    },
    {
        "id": "vapormarket",
        "name": "VaporMarket.gr",
        "url": "https://www.vapormarket.gr",
        "category": "retail_competitor"
    },
    {
        "id": "vapexperts",
        "name": "VapExperts.gr",
        "url": "https://vapexperts.gr",
        "category": "retail_competitor"
    },
    {
        "id": "atmi-zo",
        "name": "Atmi-zo.gr",
        "url": "https://atmi-zo.gr",
        "category": "retail_competitor"
    },
    {
        "id": "nexxton",
        "name": "Nexxton-ecig.com",
        "url": "https://nexxton-ecig.com",
        "category": "retail_competitor"
    },
    {
        "id": "smok-e",
        "name": "Smok-e.gr",
        "url": "https://smok-e.gr",
        "category": "retail_competitor"
    },
    {
        "id": "k110",
        "name": "K110.eu",
        "url": "https://k110.eu/",
        "category": "retail_competitor"
    }
]

def scrape_competitor(competitor: dict) -> str:
    """Scrape basic content from a competitor website"""
    print(f"🕷️  Scraping {competitor['name']}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(competitor['url'], headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()[:5000]  # Limit to 5000 chars
        
        print(f"✅ Got content from {competitor['name']} ({len(text)} chars)")
        return text
        
    except Exception as e:
        print(f"❌ Error scraping {competitor['name']}: {str(e)}")
        return None

def save_to_supabase(competitor_id: str, competitor_name: str, scraped_content: str):
    """Save scraped data to Supabase"""
    try:
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "competitor_id": competitor_id,
            "name": competitor_name,
            "url": next((c['url'] for c in COMPETITORS if c['id'] == competitor_id), ""),
            "scraped_content": scraped_content,
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/price_war_history",
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            print(f"💾 Saved {competitor_name} to Supabase")
            return True
        else:
            print(f"⚠️  Supabase save failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving to Supabase: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🚀 VAPESTATION PRICE WAR SCRAPER")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Competitors to track: {len(COMPETITORS)}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for competitor in COMPETITORS:
        print(f"\n📍 Processing: {competitor['name']}")
        
        # Scrape
        content = scrape_competitor(competitor)
        
        if content:
            # Save to Supabase
            if save_to_supabase(competitor['id'], competitor['name'], content):
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
        
        print()
    
    print("=" * 60)
    print(f"✅ Scraping complete! Success: {success_count}, Failed: {fail_count}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
