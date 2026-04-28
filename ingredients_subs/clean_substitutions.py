import json
import re
from collections import Counter

INPUT_FILE = "data/fooddotcom_review_sub_data.json"
OUTPUT_FILE = "data/fooddotcom_review_sub_data_clean.json"
REJECTED_FILE = "data/fooddotcom_review_sub_data_rejected.json"

# Common non-ingredient / noisy tokens
BAD_EXACT = {
    "", "it", "this", "that", "they", "them", "one", "ones", "thing", "things",
    "recipe", "recipes", "dish", "dishes", "flavor", "taste", "texture", "time",
    "times", "version", "help", "success", "problems", "effects", "results",
    "half", "part", "parts", "portion", "some", "others", "other", "more",
    "less", "instead", "rest", "substitute", "substituted", "replace", "replaced",
    "subbed", "stitution", "stitute"
}

BAD_CONTAINS = {
    "worked", "perfectly", "delicious", "great", "wonderful", "thanks", "review",
    "recipe", "flavor", "taste", "texture", "turned out", "came out", "my mom",
    "wife", "family", "grocer", "sandwich", "periscope", "brilliant", "lovely",
    "served", "exactly", "followed", "next time", "on hand", "get together",
    "availablity", "availability"
}

MEASURE_WORDS = {
    "cup", "cups", "tablespoon", "tablespoons", "tbsp", "teaspoon", "teaspoons", "tsp",
    "pound", "pounds", "lb", "lbs", "ounce", "ounces", "oz", "can", "cans", "packet",
    "packets", "small", "large", "medium", "few", "bit", "dash", "pinch", "handful"
}

CONNECTOR_WORDS = {
    "because", "though", "although", "while", "still", "turned", "came",
    "worked", "made", "using", "used", "added", "left", "omit", "omitted",
    "other", "than", "with", "without", "cause", "since", "due"
}

GENERIC_WORDS = {
    "rest", "mixture", "batter", "filling", "topping", "sauce", "stuff",
    "dish", "meal", "recipe", "version", "one", "ones", "thing", "things",
    "ingredients", "ingredient", "top", "bottom", "side", "kind", "brand"
}

# Ingredient-like words that are often valid even if short or broad
ALLOWED_INGREDIENT_HEADS = {
    "butter", "oil", "milk", "cream", "cheese", "sugar", "salt", "pepper", "egg",
    "eggs", "flour", "broth", "stock", "yogurt", "chicken", "beef", "turkey",
    "pork", "rice", "beans", "onion", "onions", "garlic", "cabbage", "broccoli",
    "cauliflower", "spinach", "banana", "pumpkin", "apple", "applesauce", "honey",
    "walnuts", "pecans", "dates", "raisins", "feta", "ricotta", "parmesan",
    "mozzarella", "cheddar", "sour cream", "vinegar", "cilantro", "basil", "mint",
    "oregano", "thyme", "sage", "leeks", "scallions", "shallots", "tofu", "chickpeas",
    "mushrooms", "tomatoes", "tomato", "jalapeno", "paprika", "cinnamon", "cloves",
    "allspice", "nutmeg", "cumin", "cardamom", "barley", "cornmeal", "breadcrumbs",
    "panko", "mustard", "broccoli", "chard"
}

def load_data(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def strip_leading_articles(text: str) -> str:
    return re.sub(r"^(the|a|an)\s+", "", text).strip()

def strip_substitution_artifacts(text: str) -> str:
    # Remove common broken prefixes from regex extraction
    text = re.sub(r"\b(?:substitute|substituted|subbed|replace|replaced|situted|stituted|stitued|stituting|situting|sub|stitue|stitutions|tituted|stituded)\b", " ", text)
    text = re.sub(r"\b(?:ing|stitute|stitution)\b", " ", text)
    return normalize_space(text)

def truncate_garbage(text: str) -> str:
    # Truncate trailing phrases
    pattern = r"\b(?:instead|because|to make|for a|and made|and used|and added|in equal|as we|in the|anyway|due to|but|which|since|and switch|and add|and omit|plus|as someone|one day|as a|as an|and whipped|and it was)\b.*$"
    text = re.sub(pattern, "", text).strip()
    
    # Aggressively truncate at "for" since it's usually restating the original ingredient (e.g. "coconut milk for cream")
    text = re.sub(r"\b(?:for)\b.*$", "", text).strip()

    # Strip some generic quantifying prefixes and regex artifacts
    prefix_pattern = r"^(?:amount of|some of the|half a of|half of|snack of|part of the|equal amount of|equal amounts of|one half of|equal parts|little of|couple of|couple of of|s were|were|i make is)\b"
    text = re.sub(prefix_pattern, "", text).strip()
    
    # Clean trailing " and", " or"
    text = re.sub(r"\b(?:and|or)$", "", text).strip()
    return text

def strip_measurements(text: str) -> str:
    # Remove numeric quantities and units
    text = re.sub(r"\b\d+(?:/\d+)?\b", " ", text)
    words = [w for w in text.split() if w not in MEASURE_WORDS]
    return normalize_space(" ".join(words))

def basic_clean(text: str) -> str:
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"[^a-z\s\-]", " ", text)
    text = re.sub(r"\b(?:very|really|quite|just)\b", " ", text)
    
    # Strip leading articles first so prefixes match cleanly
    text = strip_leading_articles(text)
    
    text = strip_substitution_artifacts(text)
    text = truncate_garbage(text)
    text = strip_measurements(text)
    text = normalize_space(text)
    return text

def looks_fragmented(text: str) -> bool:
    if not text:
        return True
    if len(text) < 2:
        return True
    if text in BAD_EXACT:
        return True
    if text.endswith(("and", "or", "for", "with", "of", "to", "in", "out")):
        return True
    if text.startswith(("and ", "or ", "for ", "with ", "of ", "to ", "in ", "out ")):
        return True
    return False

def contains_bad_phrase(text: str) -> bool:
    return any(phrase in text for phrase in BAD_CONTAINS)

def too_long_or_sentence_like(text: str) -> bool:
    words = text.split()
    if len(words) == 0:
        return True
    if len(words) > 5:
        return True
    # Too many connector words usually means it is a sentence fragment, not an ingredient
    connector_hits = sum(1 for w in words if w in CONNECTOR_WORDS)
    if connector_hits >= 2:
        return True
    return False

def ingredientish(text: str) -> bool:
    if text in ALLOWED_INGREDIENT_HEADS:
        return True
    if any(text.endswith(" " + h) for h in ALLOWED_INGREDIENT_HEADS):
        return True
    if any(h in text for h in ALLOWED_INGREDIENT_HEADS):
        return True
    # Accept short noun-like phrases as a fallback
    words = text.split()
    if 1 <= len(words) <= 4 and all(len(w) > 1 for w in words):
        if any(w in ALLOWED_INGREDIENT_HEADS for w in words):
            return True
    return False

def reject_reason(from_ing: str, to_ing: str) -> str | None:
    if not from_ing or not to_ing:
        return "empty_after_clean"
    if looks_fragmented(from_ing) or looks_fragmented(to_ing):
        return "fragmented"
    if from_ing in GENERIC_WORDS or to_ing in GENERIC_WORDS:
        return "generic_non_ingredient"
    if from_ing == to_ing:
        return "same_ingredient"
    if contains_bad_phrase(from_ing) or contains_bad_phrase(to_ing):
        return "contains_bad_phrase"
    if too_long_or_sentence_like(from_ing) or too_long_or_sentence_like(to_ing):
        return "too_long_or_sentence_like"
    if from_ing in {"fresh", "dried", "regular", "real", "green", "red", "white", "half"}:
        return "too_generic"
    if to_ing in {"fresh", "dried", "regular", "real", "green", "red", "white", "half"}:
        return "too_generic"
    if not ingredientish(from_ing) or not ingredientish(to_ing):
        return "not_ingredient_like"
    return None

def canonicalize(text: str) -> str:
    # Light canonicalization only; do not over-normalize yet
    text = re.sub(r"\beggbeaters\b", "egg beaters", text)
    text = re.sub(r"\bgf flour\b", "gluten free flour", text)
    text = re.sub(r"\bchoc\b", "chocolate", text)
    text = normalize_space(text)
    return text

def clean_pair(pair: dict) -> tuple[dict | None, dict | None]:
    raw_from = pair.get("fromIng", "")
    raw_to = pair.get("toIng", "")

    cleaned_from = canonicalize(basic_clean(raw_from))
    cleaned_to = canonicalize(basic_clean(raw_to))

    reason = reject_reason(cleaned_from, cleaned_to)
    if reason is not None:
        return None, {
            "fromIng_raw": raw_from,
            "toIng_raw": raw_to,
            "fromIng_clean": cleaned_from,
            "toIng_clean": cleaned_to,
            "reason": reason,
        }

    return {
        "fromIng": cleaned_from,
        "toIng": cleaned_to,
    }, None

def dedupe_pairs(pairs: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for p in pairs:
        key = (p["fromIng"], p["toIng"])
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out

def main() -> None:
    raw_data = load_data(INPUT_FILE)

    cleaned = []
    rejected = []

    for pair in raw_data:
        keep, reject = clean_pair(pair)
        if keep is not None:
            cleaned.append(keep)
        if reject is not None:
            rejected.append(reject)

    cleaned = dedupe_pairs(cleaned)

    # Optional: sort by frequency of source ingredient for easier inspection
    src_counts = Counter(p["fromIng"] for p in cleaned)
    cleaned.sort(key=lambda x: (-src_counts[x["fromIng"]], x["fromIng"], x["toIng"]))

    save_json(OUTPUT_FILE, cleaned)
    save_json(REJECTED_FILE, rejected)

    print(f"raw pairs: {len(raw_data)}")
    print(f"clean pairs: {len(cleaned)}")
    print(f"rejected pairs: {len(rejected)}")
    print("\nTop source ingredients:")
    for ing, count in src_counts.most_common(20):
        print(f"{ing}: {count}")

if __name__ == "__main__":
    main()