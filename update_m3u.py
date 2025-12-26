import requests
import json
import os
import re
from lxml import etree
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# === CONFIGURATION ===
# BASE_DIR remains dynamic to ensure the script works regardless of where it's called from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Fetch values from .env with fallbacks to defaults
BASE_URL = os.getenv("BASE_URL", "https://example.com")
EPG_SOURCES_FILE = os.path.join(BASE_DIR, os.getenv("EPG_SOURCES_FILENAME", "epg_sources.json"))
MAPPING_FILE = os.path.join(BASE_DIR, os.getenv("MAPPING_FILENAME", "mapping.json"))

# Files to generate
LOCAL_EPG_PATH = os.path.join(BASE_DIR, os.getenv("LOCAL_EPG_FILENAME", "epg.xml"))
LOCAL_M3U_PATH = os.path.join(BASE_DIR, os.getenv("LOCAL_M3U_FILENAME", "index.m3u"))

def natural_key(string_):
    """
    Helper function for natural alphanumeric sorting.
    """
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', string_)]

def fix_epg_and_m3u():
    # Check if required source files exist
    if not os.path.exists(MAPPING_FILE):
        print(f"Error: Mapping file not found at {MAPPING_FILE}")
        return
    if not os.path.exists(EPG_SOURCES_FILE):
        print(f"Error: EPG sources file not found at {EPG_SOURCES_FILE}")
        return

    # Load channel mapping and EPG sources
    with open(MAPPING_FILE, 'r') as f:
        channels = json.load(f)
    with open(EPG_SOURCES_FILE, 'r') as f:
        epg_sources = json.load(f)
    
    # Sort channels alphabetically (Natural Sort)
    channels.sort(key=lambda x: natural_key(x.get("name", "")))
    
    # 1. GENERATE EPG
    allowed_ids = set([ch.get("tvg_id") for ch in channels if ch.get("tvg_id")])
    
    combined_root = etree.Element("tv", {
        "generator-info-name": "Custom EPG Merger",
        "generator-info-url": BASE_URL
    })

    programme_count = 0

    for source in epg_sources:
        country = source.get("country", "Unknown")
        url = source.get("url")
        
        if not url:
            continue

        print(f"Downloading {country} EPG from {url}...")
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            source_xml = etree.fromstring(r.content, parser=etree.XMLParser(recover=True))
            
            # Extract channels
            for ch in source_xml.xpath("//channel"):
                if ch.get("id") in allowed_ids:
                    combined_root.append(ch)

            # Extract programmes
            for pr in source_xml.xpath("//programme"):
                if pr.get("channel") in allowed_ids:
                    combined_root.append(pr)
                    programme_count += 1
                    
        except Exception as e:
            print(f"Failed to process {country} EPG: {e}")

    # Write merged EPG to local full path
    with open(LOCAL_EPG_PATH, "wb") as f:
        f.write(etree.tostring(combined_root, pretty_print=True, encoding='utf-8', xml_declaration=True))
    
    print(f"Merged EPG saved to: {LOCAL_EPG_PATH}")

    # 2. GENERATE M3U
    print(f"Building M3U with natural sorting and categories...")
    epg_filename = os.path.basename(LOCAL_EPG_PATH)
    final_m3u = [f'#EXTM3U x-tvg-url="{BASE_URL}/{epg_filename}"']
    
    for ch in channels:
        name = ch.get("name", "Unknown Channel")
        tv_id = ch.get("tvg_id", "")
        tv_logo = ch.get("tvg_logo", "")
        stream_url = ch.get("stream_url", "")
        # Get category from JSON, fallback to "Uncategorized" if key is missing
        category = ch.get("category", "Uncategorized")
        
        if stream_url:
            # Added group-title="{category}" to the EXTF line
            final_m3u.append(f'#EXTINF:-1 tvg-id="{tv_id}" tvg-logo="{tv_logo}" group-title="{category}",{name}')
            final_m3u.append(stream_url)

    # Write M3U to local full path
    with open(LOCAL_M3U_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(final_m3u))
    
    print(f"M3U saved to: {LOCAL_M3U_PATH}")
    print(f"Done! Total programmes grabbed from EPG: {programme_count}")

if __name__ == "__main__":
    fix_epg_and_m3u()