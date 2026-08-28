import json, os, hashlib, requests
from bs4 import BeautifulSoup

KEYWORDS = ["psychol", "counsel", "clinical psych", "psychiatr", "social work",
            "mental health", "psycho-oncology", "rehabilitation", "therapist"]

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

def main():
    sources = json.load(open("sources.json"))
    seen = {}
    if os.path.exists("data/seen.json"):
        seen = json.load(open("data/seen.json"))

    new_findings = []
    for src in sources:
        text = fetch_text(src["url"], src["name"])
        if not text:
            continue
        h = hashlib.md5(text.encode()).hexdigest()
        if seen.get(src["name"]) != h:
            matches = find_matches(text)
            print(f"[{src['name']}] {len(matches)} keyword matches found")
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
