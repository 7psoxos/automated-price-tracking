#!/usr/bin/env python3
"""
VapeStation Price War Scraper
Monitors Greek vape competitor prices
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

COMPETITORS = [
    {"id": "e-smokers", "name": "E-Smokers.gr", "url": "https://www.e-smokers.gr"},
    {"id": "atmology", "name": "Atmology.gr", "url": "https://atmology.gr"},
    {"id": "vapormarket", "name": "VaporMarket.gr", "url": "https://www.vapormarket.gr"},
    {"id": "vapexperts", "name": "VapExperts.gr", "url": "https://vapexperts.gr"},
    {"id": "atmi-zo", "name": "Atmi-zo.gr", "url": "https://atmi-zo.gr"},
    {"id": "nexxton", "name": "Nexxton-ecig.com", "url": "https://nexxton-ecig.com"},
    {"id": "smok-e", "name": "Smok-e.gr", "url": "https://smok-e.gr"},
    {"id": "k110", "name": "K110.eu", "url": "https://k110.eu/"},
]

def scrape_competitor(competitor: dict, retries=2) -> str:
    """Scrape content with retry logic"""
    print(f"🕷️  Scraping {competitor['name']}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(competitor['url'], headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()[:5000]
            
            print(f"✅ Got content from {competitor['name']} ({len(text)} chars)")
            return text
            
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f"⚠️  Retry {attempt + 1}/{retries} for {competitor['name']}: {str(e)}")
                time.sleep(2)
            else:
                print(f"❌ Error scraping {competitor['name']}: {str(e)}")
                return None
    
    return None

def save_to_supabase(competitor_id: str, competitor_name: str, url: str, content: str) -> bool:
    """Save to Supabase with error handling"""
    if not content:
        return False
    
    try:
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "competitor_id": competitor_id,
            "name": competitor_name,
            "url": url,
            "scraped_content": content,
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/price_war_history",
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            print(f"💾 Saved {competitor_name}")
            return True
        else:
            print(f"⚠️  Save failed ({response.status_code}): {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("🚀 VAPESTATION PRICE WAR SCRAPER")
    print("=" * 70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Competitors: {len(COMPETITORS)}")
    print("=" * 70)
    
    success = 0
    failed = 0
    
    for competitor in COMPETITORS:
        print(f"\n📍 {competitor['name']}")
        
        content = scrape_competitor(competitor)
        
        if content and save_to_supabase(competitor['id'], competitor['name'], competitor['url'], content):
            success += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Complete! Success: {success}/{len(COMPETITORS)}, Failed: {failed}/{len(COMPETITORS)}")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
