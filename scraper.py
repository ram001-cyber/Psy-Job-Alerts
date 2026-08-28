import json, os, hashlib, requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

KEYWORDS = ["psychol", "counsel", "clinical psych", "psychiatr", "social work",
            "mental health", "psycho-oncology", "rehabilitation", "therapist"]

MAX_AGE_DAYS = 30

def fetch_text(url, name):
    try:
        r = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        print(f"[{name}] status={r.status_code}, length={len(r.text)}")
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, "lxml")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"[{name}] FAILED: {e}")
        return ""

def find_matches(text):
    hits = []
    for line in text.split(". "):
        if any(k in line.lower() for k in KEYWORDS):
            hits.append(line.strip()[:300])
    return hits

def load_listings():
    if os.path.exists("data/listings.json"):
        return json.load(open("data/listings.json"))
    return []

def prune_old(listings):
    cutoff = datetime.utcnow() - timedelta(days=MAX_AGE_DAYS)
    kept = []
    for item in listings:
        try:
            seen_date = datetime.fromisoformat(item["first_seen"])
            if seen_date >= cutoff:
                kept.append(item)
        except Exception:
            continue
    return kept

def main():
    sources = json.load(open("sources.json"))
    listings = prune_old(load_listings())
    known_ids = {item["id"] for item in listings}

    new_count = 0
    fresh_for_notify = []

    for src in sources:
        text = fetch_text(src["url"], src["name"])
        if not text:
            continue
        matches = find_matches(text)
        print(f"[{src['name']}] {len(matches)} keyword matches found")
        for m in matches[:8]:
            uid = hashlib.md5((src["name"] + m).encode()).hexdigest()
            if uid in known_ids:
                continue
            entry = {
                "id": uid,
                "type": "official",
                "source": src["name"],
                "org": src["name"],
                "url": src["url"],
                "district": src["district"],
                "summary": m,
                "first_seen": datetime.utcnow().isoformat()
            }
            listings.append(entry)
            known_ids.add(uid)
            fresh_for_notify.append(entry)
            new_count += 1

    os.makedirs("data", exist_ok=True)
    json.dump(listings, open("data/listings.json", "w"), indent=2)

    if fresh_for_notify:
        json.dump(fresh_for_notify, open("data/latest_findings.json", "w"), indent=2)
        print(f"Added {new_count} new listings")
    else:
        print("No new updates")

if __name__ == "__main__":
    main()
