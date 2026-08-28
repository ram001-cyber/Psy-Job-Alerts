import json, os, hashlib, requests
from bs4 import BeautifulSoup

KEYWORDS = ["psychol", "counsel", "clinical psych", "psychiatr", "social work",
            "mental health", "psycho-oncology", "rehabilitation", "therapist"]

def fetch_text(url):
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return ""

def find_matches(text):
    lower = text.lower()
    hits = []
    for line in text.split(". "):
        if any(k in line.lower() for k in KEYWORDS):
            hits.append(line.strip()[:300])
    return hits

def main():
    sources = json.load(open("sources.json"))
    seen = {}
    if os.path.exists("data/seen.json"):
        seen = json.load(open("data/seen.json"))

    new_findings = []
    for src in sources:
        text = fetch_text(src["url"])
        if not text:
            continue
        h = hashlib.md5(text.encode()).hexdigest()
        if seen.get(src["name"]) != h:
            matches = find_matches(text)
            if matches:
                new_findings.append({
                    "source": src["name"],
                    "url": src["url"],
                    "district": src["district"],
                    "matches": matches[:5]
                })
            seen[src["name"]] = h

    os.makedirs("data", exist_ok=True)
    json.dump(seen, open("data/seen.json", "w"), indent=2)

    if new_findings:
        json.dump(new_findings, open("data/latest_findings.json", "w"), indent=2)
        print(f"Found updates in {len(new_findings)} sources")
    else:
        print("No new updates")

if __name__ == "__main__":
    main()
