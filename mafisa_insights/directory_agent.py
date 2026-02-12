import requests
from bs4 import BeautifulSoup
import json
import dataclasses
import datetime
from typing import List, Dict, Set
from mafisa_insights.data_models import DirectoryListing
import time
import random
import re

class DirectoryAgent:
    BASE_URL = "https://www.lesotho-info.co.za"
    START_URL = "https://www.lesotho-info.co.za/country/businesses"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    def __init__(self):
        self.listings: List[DirectoryListing] = []
        self.visited_urls: Set[str] = set()

    def scrape_directory(self, limit: int = 10):
        print(f"Starting scrape with limit {limit}...")
        try:
            # 1. Get Categories
            print(f"Fetching categories from {self.START_URL}...")
            response = requests.get(self.START_URL, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find category links.
            # Based on inspection: href="/country/businesses/ID/NAME"
            category_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/country/businesses/' in href and href != self.START_URL and not href.endswith('sort:Business.id/direction:asc'):
                    full_url = self._make_full_url(href)
                    if full_url not in category_links:
                        category_links.append(full_url)

            print(f"Found {len(category_links)} categories.")

            # 2. Visit Categories to find businesses
            business_links = set()

            # Shuffle categories to get variety if limit is small
            random.shuffle(category_links)

            for cat_url in category_links:
                if len(business_links) >= limit:
                    break

                print(f"Scraping category: {cat_url}")
                try:
                    cat_resp = requests.get(cat_url, headers=self.HEADERS, timeout=10)
                    cat_soup = BeautifulSoup(cat_resp.content, 'html.parser')

                    # Find business links. href="/country/business/ID/NAME"
                    for a in cat_soup.find_all('a', href=True):
                        href = a['href']
                        if '/country/business/' in href:
                            full_url = self._make_full_url(href)
                            business_links.add(full_url)
                            if len(business_links) >= limit:
                                break
                    time.sleep(0.5) # Be polite
                except Exception as e:
                    print(f"Error scraping category {cat_url}: {e}")

            print(f"Found {len(business_links)} businesses to scrape.")

            # 3. Visit Business pages
            for bus_url in list(business_links)[:limit]:
                print(f"Scraping business: {bus_url}")
                try:
                    listing = self._parse_business_page(bus_url)
                    if listing:
                        self.listings.append(listing)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error scraping business {bus_url}: {e}")

        except Exception as e:
            print(f"Global scraping error: {e}")

    def _make_full_url(self, href):
        if href.startswith('http'):
            return href
        return f"{self.BASE_URL}{href}" if href.startswith('/') else f"{self.BASE_URL}/{href}"

    def _parse_business_page(self, url: str) -> DirectoryListing:
        resp = requests.get(url, headers=self.HEADERS, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')

        name = soup.title.string.strip() if soup.title else "Unknown"
        # Clean up name
        for suffix in [" - Businesses in Lesotho", " - Lesotho Information Directory"]:
            if suffix in name:
                name = name.split(suffix)[0]

        # Sector: Inferred from URL or page content?
        # The page structure showed categories in breadcrumbs or similar, but let's default to "General"
        sector = "General"

        # Location
        location = "Lesotho"
        # Try to find "Location:" text
        location_node = soup.find(string=re.compile("Location:"))
        if location_node:
            # usually the text after
            parent = location_node.parent
            if parent:
                # Get next sibling or text in parent
                loc_text = parent.get_text().replace("Location:", "").strip()
                if loc_text:
                    location = loc_text

        # Contact Details
        phone = None
        email = None
        website = None

        # Using a helper to find links with 'tel:' or 'mailto:'
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('tel:'):
                phone = href.replace('tel:', '').strip()
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0].strip()

        # Website
        # Look for explicit Website link or regex
        if not website:
            website_node = soup.find(string=re.compile("Website:"))
            if website_node:
                # Use find_next on the soup starting from this node or its parent
                # Usually the link is next to the text or in the same block
                # Text: "Website: "
                # Link: <a href="...">...</a>
                # It might be a sibling of the parent element containing "Website:"

                # Try finding 'a' in the same parent first
                if website_node.parent:
                    link = website_node.parent.find('a', href=True)
                    if not link:
                        link = website_node.parent.find_next_sibling('a', href=True)

                    if link and 'lesotho-info.co.za' not in link['href']:
                        website = link['href']

            if not website:
                # Fallback search
                for a in soup.find_all('a', href=True):
                    if 'www.' in a['href'] or 'http' in a['href']:
                        if 'lesotho-info.co.za' not in a['href'] and 'facebook' not in a['href'] and 'twitter' not in a['href'] and 'instagram' not in a['href']:
                             if a.string and 'Website' in a.string:
                                 website = a['href']
                                 break

        # Socials
        socials = {}
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'facebook.com' in href:
                socials['facebook'] = href
            elif 'instagram.com' in href:
                socials['instagram'] = href
            elif 'twitter.com' in href or 'x.com' in href:
                socials['twitter'] = href
            elif 'linkedin.com' in href:
                socials['linkedin'] = href

        # Description
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', "")

        return DirectoryListing(
            name=name,
            sector=sector,
            location=location,
            phone=phone,
            email=email,
            website=website,
            social_links=socials,
            description=description,
            source_url=url,
            scraped_at=datetime.datetime.now().isoformat()
        )

    def save_data(self, filepath: str):
        data = [dataclasses.asdict(l) for l in self.listings]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved {len(data)} listings to {filepath}")

    def generate_insights_report(self, output_path: str):
        total = len(self.listings)
        if total == 0:
            print("No listings to report on.")
            # Create an empty report to avoid failure
            with open(output_path, 'w') as f:
                f.write(f"# Weekly Insights Report\n**Date:** {datetime.date.today()}\n\nNo data collected.")
            return

        with_email = sum(1 for l in self.listings if l.email)
        with_phone = sum(1 for l in self.listings if l.phone)
        with_website = sum(1 for l in self.listings if l.website)

        report = f"""# Weekly Insights Report
**Date:** {datetime.date.today()}

## SME Directory Enrichment
- **Total Businesses Scraped:** {total}
- **Enrichment Stats:**
    - Email Addresses: {with_email} ({with_email/total*100:.1f}%)
    - Phone Numbers: {with_phone} ({with_phone/total*100:.1f}%)
    - Websites: {with_website} ({with_website/total*100:.1f}%)

## Sector Trends
(Based on scraped data sample from lesotho-info.co.za)
- Data collected shows a variety of businesses.

## New Opportunities
- Businesses missing online presence (Website): {total - with_website}
- Businesses missing contact info (Email/Phone): {total - max(with_email, with_phone)}

## Recommendations
- Target businesses without websites for digital services.
- Verify contact details for {total - with_phone} entries.
"""
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"Report generated at {output_path}")
