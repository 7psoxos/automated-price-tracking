#!/usr/bin/env python3
"""
Price Tracking System for Vapestation
Monitors Greek vape competitor prices via Firecrawl
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import Json
import requests

load_dotenv()

# Initialize Firecrawl
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")
POSTGRES_URL = os.getenv("POSTGRES_URL")

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

class Product(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(description="Product price in EUR")
    currency: str = Field(default="EUR", description="Currency code")
    in_stock: bool = Field(default=True, description="Is product in stock")

def scrape_competitor(competitor: dict) -> list:
    """Scrape prices from a competitor website"""
    print(f"🕷️ Scraping {competitor['name']}...")
    
    try:
        response = app.scrape_url(
            competitor['url'],
            params={
                "formats": ["markdown"],
            }
        )
        
        if response and response.get('markdown'):
            # Log markdown for debugging
            print(f"✅ Got markdown from {competitor['name']} ({len(response['markdown'])} chars)")
            return response['markdown']
        else:
            print(f"⚠️ No data from {competitor['name']}")
            return None
            
    except Exception as e:
        print(f"❌ Error scraping {competitor['name']}: {str(e)}")
        return None

def save_to_supabase(competitor_id: str, competitor_name: str, scraped_content: str):
    """Save scraped data to Supabase"""
    try:
        # Use Supabase REST API
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
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
        else:
            print(f"⚠️ Supabase save failed for {competitor_name}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error saving to Supabase: {str(e)}")

def main():
    print("=" * 60)
    print("🚀 VAPESTATION PRICE WAR SCRAPER")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Competitors to track: {len(COMPETITORS)}")
    print("=" * 60)
    
    for competitor in COMPETITORS:
        print(f"\n📍 Processing: {competitor['name']}")
        
        # Scrape
        content = scrape_competitor(competitor)
        
        if content:
            # Save to Supabase
            save_to_supabase(
                competitor['id'],
                competitor['name'],
                content
            )
        
        print()
    
    print("=" * 60)
    print("✅ Scraping complete!")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
