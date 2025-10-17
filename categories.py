"""
Fashion App - Category and Tag Definitions

This file contains all category structures and tag vocabularies used throughout the app.
All categories and tags are gender-neutral.
"""

# Wardrobe item categories (main + subcategories)
CATEGORIES = {
    "top": [
        "t-shirt",
        "shirt",
        "blouse",
        "sweater",
        "hoodie",
        "tank-top",
        "polo",
        "cardigan",
    ],
    "bottom": [
        "jeans",
        "pants",
        "shorts",
        "skirt",
        "leggings",
        "joggers",
        "dress-pants",
    ],
    "outerwear": [
        "jacket",
        "coat",
        "blazer",
        "vest",
        "parka",
        "windbreaker",
        "trench-coat",
    ],
    "footwear": [
        "sneakers",
        "boots",
        "sandals",
        "heels",
        "flats",
        "loafers",
        "dress-shoes",
    ],
    "fullbody": [
        "dress",
        "jumpsuit",
        "romper",
        "overalls",
        "coveralls",
        "suit",
    ],
    "accessory": [
        "hat",
        "scarf",
        "belt",
        "bag",
        "sunglasses",
        "jewelry",
        "watch",
        "tie",
    ],
    "misc": [
        "underwear",
        "socks",
        "swimwear",
        "sleepwear",
        "other",
    ],
}

# Tag categories (controlled vocabulary)
TAG_CATEGORIES = {
    "colors": [
        "black",
        "white",
        "navy",
        "red",
        "blue",
        "green",
        "yellow",
        "pink",
        "purple",
        "brown",
        "gray",
        "grey",
        "beige",
        "orange",
        "cream",
        "tan",
        "maroon",
        "burgundy",
    ],
    "patterns": [
        "solid",
        "striped",
        "floral",
        "plaid",
        "polka-dot",
        "checkered",
        "geometric",
        "animal-print",
        "paisley",
        "tie-dye",
        "camo",
    ],
    "fit": [
        "slim-fit",
        "regular-fit",
        "loose-fit",
        "oversized",
        "tight",
        "relaxed",
        "athletic-fit",
        "tailored",
    ],
    "style": [
        "casual",
        "formal",
        "sporty",
        "vintage",
        "minimalist",
        "streetwear",
        "bohemian",
        "preppy",
        "grunge",
        "chic",
        "edgy",
        "classic",
    ],
    "material": [
        "cotton",
        "denim",
        "leather",
        "silk",
        "wool",
        "polyester",
        "linen",
        "cashmere",
        "suede",
        "velvet",
        "satin",
        "nylon",
        "spandex",
        "fleece",
    ],
    "details": [
        "v-neck",
        "crew-neck",
        "button-down",
        "zip-up",
        "sleeveless",
        "long-sleeve",
        "short-sleeve",
        "hooded",
        "pockets",
        "distressed",
        "ripped",
        "embroidered",
        "pleated",
    ],
    "season": [
        "summer",
        "winter",
        "spring",
        "fall",
        "all-season",
    ],
    "occasion": [
        "work",
        "party",
        "athletic",
        "casual",
        "formal",
        "date-night",
        "lounge",
        "beach",
        "wedding",
        "interview",
    ],
}

# Gender style preferences (for filtering recommendations)
GENDER_STYLES = [
    "mens",
    "womens",
    "unisex",
    "all",
]

# Helper functions
def get_all_categories():
    """Get list of all main categories"""
    return list(CATEGORIES.keys())


def get_subcategories(category):
    """Get subcategories for a given main category"""
    return CATEGORIES.get(category, [])


def is_valid_category(category, subcategory=None):
    """Validate category and optional subcategory"""
    if category not in CATEGORIES:
        return False
    if subcategory and subcategory not in CATEGORIES[category]:
        return False
    return True


def get_all_tags():
    """Get all available tags across all categories"""
    all_tags = []
    for tags in TAG_CATEGORIES.values():
        all_tags.extend(tags)
    return all_tags


def get_tags_by_category(tag_category):
    """Get tags for a specific tag category (e.g., 'colors', 'patterns')"""
    return TAG_CATEGORIES.get(tag_category, [])


def validate_tags(tags):
    """Check if provided tags are valid"""
    all_valid_tags = get_all_tags()
    return all(tag in all_valid_tags for tag in tags)


# Example usage and documentation
if __name__ == "__main__":
    print("Fashion App - Category Structure\n")

    print("Main Categories:")
    for category, subcategories in CATEGORIES.items():
        print(f"  {category}:")
        for subcat in subcategories:
            print(f"    - {subcat}")

    print("\nTag Categories:")
    for tag_cat, tags in TAG_CATEGORIES.items():
        print(f"  {tag_cat}: {len(tags)} tags")

    print(f"\nGender Styles: {', '.join(GENDER_STYLES)}")

    # Validation examples
    print("\nValidation Examples:")
    print(f"  is_valid_category('top', 't-shirt'): {is_valid_category('top', 't-shirt')}")
    print(f"  is_valid_category('top', 'invalid'): {is_valid_category('top', 'invalid')}")
    print(f"  validate_tags(['black', 'casual', 'cotton']): {validate_tags(['black', 'casual', 'cotton'])}")
    print(f"  validate_tags(['invalid-tag']): {validate_tags(['invalid-tag'])}")
