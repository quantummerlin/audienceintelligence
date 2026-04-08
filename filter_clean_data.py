import json
import requests

INPUT_FILE = "reddit_clean_data.json"
OUTPUT_FILE = "outputs/reddit_signal_posts.json"

# --- Tier 1: known-signal subreddits, auto-accept ---
SIGNAL_SUBS = {
    "Manifestation", "NevilleGoddard", "Subliminal", "manifestingSP",
    "lawofattraction", "lawofassumption", "manifestation_support",
    "GetYourSP", "livingfromtheend", "JosephMurphy", "SubconsciousMind",
    "quantummanifesting", "spirituality", "spiritualdevelopment"
}

# --- Tier 1: obvious noise subs, auto-reject ---
NOISE_SUBS = {
    "ottawa", "france", "TopCharacterTropes", "RHOBH", "BestofRedditorUpdates",
    "HFY", "JujutsuPowerScaling", "todayilearned", "CBSECommerce", "science",
    "AITAH", "Philippines", "CTsandbox", "OnePiece", "DestinyTheGame",
    "relationship_advice", "SaintMeghanMarkle", "Epstein", "DnD",
    "GoldenInuTokens", "Jujutsufolk", "realhousewivesofSLC", "Benophie",
    "ICSE", "AirUniversity"
}

MISTRAL_URL = "http://localhost:11434/api/generate"  # change if using API endpoint
MISTRAL_MODEL = "mistral"  # or "mistral-small" depending on your setup

SYSTEM_PROMPT = (
    "You are a content classifier. "
    "SIGNAL = genuinely about manifestation, law of attraction, subconscious reprogramming, "
    "reality creation, SP attraction, quantum consciousness, or subliminals for mindset. "
    "NOISE = uses 'manifest/quantum/reality' in any other context "
    "(gaming, sci-fi, stocks, wrestling, politics, religion, gossip). "
    "Respond with exactly one word: SIGNAL or NOISE."
)


def classify_with_mistral(title, body):
    snippet = body[:300].replace("\n", " ") if body else ""
    prompt = f"Title: {title}\nBody: {snippet}"
    try:
        resp = requests.post(MISTRAL_URL, json={
            "model": MISTRAL_MODEL,
            "system": SYSTEM_PROMPT,
            "prompt": prompt,
            "stream": False
        }, timeout=30)
        result = resp.json().get("response", "").strip().upper()
        return "SIGNAL" in result
    except Exception as e:
        print(f"  [Mistral error] {e} — defaulting to NOISE")
        return False


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        posts = json.load(f)

    print(f"Total posts: {len(posts)}")

    tier1_signal, tier1_noise, tier2_posts = [], [], []

    for post in posts:
        sub = post.get("subreddit", "")
        if sub in SIGNAL_SUBS:
            tier1_signal.append(post)
        elif sub in NOISE_SUBS:
            tier1_noise.append(post)
        else:
            tier2_posts.append(post)

    print(f"Tier 1 SIGNAL (known subs): {len(tier1_signal)}")
    print(f"Tier 1 NOISE  (known subs): {len(tier1_noise)}")
    print(f"Tier 2 unknown subs:        {len(tier2_posts)}")

    tier2_signal = []
    if tier2_posts:
        print(f"\nRunning Mistral on {len(tier2_posts)} ambiguous posts...")
        for i, post in enumerate(tier2_posts):
            is_signal = classify_with_mistral(post["title"], post.get("body", ""))
            label = "SIGNAL" if is_signal else "NOISE"
            print(f"  [{i+1}/{len(tier2_posts)}] {label} — [{post['subreddit']}] {post['title'][:60]}")
            if is_signal:
                tier2_signal.append(post)

    all_signal = tier1_signal + tier2_signal
    print(f"\nFinal SIGNAL posts: {len(all_signal)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_signal, f, indent=2, ensure_ascii=False)

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
