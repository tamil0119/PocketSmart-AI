from urllib.parse import quote_plus

PLATFORM_BASE = {
    "Amazon": "https://www.amazon.in/s?k=",
    "Flipkart": "https://www.flipkart.com/search?q=",
    "IKEA": "https://www.ikea.com/in/en/search/?q=",
    "Swiggy": "https://www.swiggy.com/search?query=",
    "Zomato": "https://www.zomato.com/search?q=",
    "OYO": "https://www.oyorooms.com/search?location=",
}

def search_url(platform: str, query: str) -> str:
    return PLATFORM_BASE.get(platform, "https://www.google.com/search?q=") + quote_plus(query)
