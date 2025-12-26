# IPTV M3U & EPG Generator

A powerful Python script designed to create custom IPTV playlists (`.m3u`) and merge multiple Electronic Program Guide (EPG) sources into a single, filtered XMLTV file.

## Features

- **Natural Alphanumeric Sorting**: Automatically sorts channels in a human-friendly way (e.g., "NFL 2" comes before "NFL 10").
- **Dynamic EPG Merging**: Pulls data from multiple remote XMLTV sources and filters them based on your specific channel mapping to keep the file size optimized.
- **Category Support**: Supports `group-title` tags for better channel organization in IPTV players.
- **Environment-Based Configuration**: Uses `.env` files to manage sensitive or environment-specific data like Base URLs and filenames.
- **Absolute Path Logic**: Designed to be reliable when executed via Cron Jobs or automated Task Schedulers by resolving paths relative to the script location.

## Project Structure

- `update_m3u.py`: The main logic script.
- `mapping.json`: Your master list of channels, logos, stream URLs, and categories.
- `epg_sources.json`: A list of remote XML EPG providers to scrape data from.
- `.env`: Local environment configuration (URL and file paths).
- `requirements.txt`: Python dependencies.

## Prerequisites

- Python 3.7 or higher.
- A web server or GitHub Pages to host the generated files (optional).

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/indakabarody/iptv-epg-generator.git
   cd iptv-epg-generator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the environment:** Create a `.env` file in the same directory:
  ```ini, toml
  BASE_URL=https://your-server-address.com
  MAPPING_FILENAME=mapping.json
  EPG_SOURCES_FILENAME=epg_sources.json
  LOCAL_EPG_FILENAME=epg.xml
  LOCAL_M3U_FILENAME=index.m3u
  ```

## Configuration
1. **Mapping Channels (`mapping.json`)**
Define your channels using this JSON structure:
  ```json
  [
    {
      "name": "Channel 1",
      "tvg_id": "CH01.ex",
      "tvg_logo": "https://example.com/logo.png",
      "stream_url": "http://stream.com/ch01.m3u",
      "category": "Sports"
    }
  ]
  ```

2. **EPG Sources (`epg_sources.json`)**
Add as many XMLTV providers as needed:
  ```json
  [
    {
      "country": "United States",
      "url": "https://iptv-epg.org/files/epg-us.xml"
    },
    {
      "country": "Canada",
      "url": "https://iptv-epg.org/files/epg-ca.xml"
    }
  ]
  ```

## Usage
Run the script manually using:
  ```bash
  python update_m3u.py
  ```
### Output:
- `index.m3u`: A sorted playlist containing your streams and categories.
- `epg.xml`: A single XMLTV file containing program schedules only for the channels defined in your mapping.

## Automation (GitHub Actions)
You can automate this script to run every 24 hours using GitHub Actions. Create a file at `.github/workflows/update.yml`:

  ```yaml
  name: Update IPTV Files
  on:
    schedule:
      - cron: '0 0 * * *' # Runs daily at midnight
    workflow_dispatch:

  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.9'
        - name: Install dependencies
          run: pip install -r requirements.txt
        - name: Run script
          run: python update_m3u.py
        - name: Commit and Push
          run: |
            git config --local user.email "action@github.com"
            git config --local user.name "GitHub Action"
            git add .
            git commit -m "Update EPG and M3U" || exit 0
            git push
  ```

## License
This project is licensed under the **MIT License**. Feel free to use and modify it as needed.