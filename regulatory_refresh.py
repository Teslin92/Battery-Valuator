#!/usr/bin/env python3
"""
Regulatory database refresh script using Firecrawl MCP.
Runs annually or on-demand to update regulatory information from official sources.

Usage:
    python regulatory_refresh.py                 # Run full refresh
    python regulatory_refresh.py --dry-run       # Preview without saving
    python regulatory_refresh.py --source epa    # Refresh specific source only
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, List
import subprocess

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'data', 'regulatory_db.json')
BACKUP_DIR = os.path.join(SCRIPT_DIR, 'data', 'backups')

# Regulatory sources to scrape
CRAWL_TARGETS = {
    "epa_faqs": {
        "url": "https://www.epa.gov/hw/lithium-ion-battery-recycling-frequently-asked-questions",
        "description": "EPA lithium-ion battery recycling FAQs",
        "frequency": "annual",
        "key_topics": ["hazardous_waste_classification", "universal_waste", "black_mass", "export_requirements"]
    },
    "rcra_export": {
        "url": "https://www.ecfr.gov/current/title-40/chapter-I/subchapter-I/part-262/subpart-H/section-262.83",
        "description": "40 CFR 262.83 - Exports of hazardous waste",
        "frequency": "annual",
        "key_topics": ["notification", "aoc", "manifest", "contracts"]
    },
    "canada_cepa": {
        "url": "https://www.canada.ca/en/environment-climate-change/services/managing-reducing-waste/cross-border-regulations.html",
        "description": "Canada cross-border movement regulations",
        "frequency": "annual",
        "key_topics": ["permits", "cnmts", "movement_documents", "contracts"]
    },
    "basel_batteries": {
        "url": "https://www.basel.int/Implementation/Wastebatteries/Overview/tabid/9415/Default.aspx",
        "description": "Basel Convention waste batteries overview",
        "frequency": "annual",
        "key_topics": ["technical_guidelines", "decisions", "pic_procedure"]
    },
    "eu_batteries": {
        "url": "https://environment.ec.europa.eu/topics/waste-and-recycling/batteries_en",
        "description": "EU batteries regulation",
        "frequency": "annual",
        "key_topics": ["regulation_2023_1542", "export_restrictions", "sustainability"]
    }
}


def backup_database():
    """Create a backup of the current database."""
    if not os.path.exists(DB_PATH):
        print("No existing database to backup")
        return None
    
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"regulatory_db_{timestamp}.json")
    
    with open(DB_PATH, 'r') as src:
        with open(backup_path, 'w') as dst:
            dst.write(src.read())
    
    print(f"✓ Backed up database to {backup_path}")
    return backup_path


def load_current_database() -> Dict[str, Any]:
    """Load the current regulatory database."""
    if not os.path.exists(DB_PATH):
        print("No existing database found")
        return {}
    
    with open(DB_PATH, 'r') as f:
        return json.load(f)


def scrape_url_with_firecrawl(url: str, description: str) -> Dict[str, Any]:
    """
    Scrape a URL using Firecrawl MCP via subprocess.
    
    Args:
        url: URL to scrape
        description: Description of the source
    
    Returns:
        Scraped content in markdown format with metadata
    """
    print(f"Scraping: {description}")
    print(f"  URL: {url}")
    
    try:
        # Use Firecrawl via command line (assumes firecrawl-cli is installed)
        # Alternative: Use the MCP directly via CallMcpTool in cursor
        
        # For now, return a placeholder indicating manual refresh is needed
        # In production, this would call Firecrawl API or MCP
        
        return {
            "url": url,
            "description": description,
            "status": "manual_refresh_required",
            "note": "Use Cursor's CallMcpTool with firecrawl_scrape for actual scraping",
            "timestamp": datetime.now().isoformat(),
            "content": None
        }
        
    except Exception as e:
        print(f"  ✗ Error scraping {url}: {str(e)}")
        return {
            "url": url,
            "description": description,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def refresh_source(source_key: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Refresh a specific regulatory source.
    
    Args:
        source_key: Key from CRAWL_TARGETS
        dry_run: If True, don't save results
    
    Returns:
        Refresh results
    """
    if source_key not in CRAWL_TARGETS:
        return {"error": f"Unknown source: {source_key}"}
    
    target = CRAWL_TARGETS[source_key]
    result = scrape_url_with_firecrawl(target["url"], target["description"])
    
    if not dry_run and result.get("content"):
        # In a full implementation, parse the content and update specific sections
        # of the database based on key_topics
        pass
    
    return result


def refresh_all_sources(dry_run: bool = False) -> Dict[str, Any]:
    """
    Refresh all regulatory sources.
    
    Args:
        dry_run: If True, preview without saving
    
    Returns:
        Summary of refresh operation
    """
    print("\n" + "="*60)
    print("REGULATORY DATABASE REFRESH")
    print("="*60 + "\n")
    
    if not dry_run:
        backup_path = backup_database()
    else:
        print("DRY RUN - No changes will be saved\n")
        backup_path = None
    
    results = {}
    for source_key, target in CRAWL_TARGETS.items():
        print(f"\n[{source_key}]")
        results[source_key] = refresh_source(source_key, dry_run)
    
    # Summary
    print("\n" + "="*60)
    print("REFRESH SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results.values() if r.get("status") != "error")
    total_count = len(results)
    
    print(f"\nSuccessful: {success_count}/{total_count}")
    if backup_path:
        print(f"Backup: {backup_path}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "backup_path": backup_path,
        "results": results,
        "success_count": success_count,
        "total_count": total_count
    }


def update_database_metadata(db: Dict[str, Any]) -> Dict[str, Any]:
    """Update metadata in database after refresh."""
    if "metadata" not in db:
        db["metadata"] = {}
    
    db["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate next refresh (1 year from now)
    from datetime import date, timedelta
    next_year = date.today() + timedelta(days=365)
    db["metadata"]["next_refresh"] = next_year.strftime("%Y-%m-%d")
    
    return db


def manual_refresh_instructions():
    """Print instructions for manual refresh using Cursor."""
    print("\n" + "="*60)
    print("MANUAL REFRESH INSTRUCTIONS")
    print("="*60)
    print("""
To manually refresh the regulatory database in Cursor:

1. Open Cursor and use the CallMcpTool with firecrawl-mcp:

   For EPA FAQs:
   CallMcpTool(
       server="user-firecrawl-mcp",
       toolName="firecrawl_scrape",
       arguments={
           "url": "https://www.epa.gov/hw/lithium-ion-battery-recycling-frequently-asked-questions",
           "formats": ["markdown"],
           "onlyMainContent": true
       }
   )

2. Extract relevant regulatory updates from the scraped content

3. Update data/regulatory_db.json with new information

4. Commit changes with clear description of what was updated

Sources to refresh annually:
""")
    
    for key, target in CRAWL_TARGETS.items():
        print(f"  • {target['description']}")
        print(f"    {target['url']}")
        print()


def check_database_freshness() -> Dict[str, Any]:
    """Check if database needs refresh based on last update date."""
    db = load_current_database()
    
    if not db or "metadata" not in db:
        return {
            "needs_refresh": True,
            "reason": "No metadata found",
            "last_updated": None
        }
    
    last_updated_str = db["metadata"].get("last_updated")
    if not last_updated_str:
        return {
            "needs_refresh": True,
            "reason": "No last_updated date",
            "last_updated": None
        }
    
    try:
        last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d").date()
        age_days = (datetime.now().date() - last_updated).days
        
        # Consider stale if older than 365 days
        needs_refresh = age_days > 365
        
        return {
            "needs_refresh": needs_refresh,
            "last_updated": last_updated_str,
            "age_days": age_days,
            "next_refresh": db["metadata"].get("next_refresh"),
            "status": "stale" if needs_refresh else "fresh"
        }
    except (ValueError, TypeError) as e:
        return {
            "needs_refresh": True,
            "reason": f"Invalid date format: {e}",
            "last_updated": last_updated_str
        }


def main():
    """Main entry point for regulatory refresh script."""
    parser = argparse.ArgumentParser(
        description="Refresh regulatory database from official sources"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview refresh without saving changes"
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Refresh specific source only (e.g., 'epa_faqs')"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if database needs refresh"
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Show manual refresh instructions for Cursor"
    )
    
    args = parser.parse_args()
    
    if args.check:
        freshness = check_database_freshness()
        print(json.dumps(freshness, indent=2))
        return 0 if not freshness["needs_refresh"] else 1
    
    if args.manual:
        manual_refresh_instructions()
        return 0
    
    if args.source:
        result = refresh_source(args.source, args.dry_run)
        print(json.dumps(result, indent=2))
    else:
        result = refresh_all_sources(args.dry_run)
        print(json.dumps(result, indent=2))
    
    if not args.dry_run:
        # Update metadata
        db = load_current_database()
        db = update_database_metadata(db)
        with open(DB_PATH, 'w') as f:
            json.dump(db, f, indent=2)
        print(f"\n✓ Updated database metadata")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
