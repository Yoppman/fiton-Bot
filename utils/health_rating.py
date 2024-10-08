import re

# Function to generate stars based on the health rating
def generate_star_rating(health_rating: int, max_rating: int = 10) -> str:
    filled_stars = '🌟' * health_rating
    empty_stars = '⚫' * (max_rating - health_rating)
    return filled_stars + empty_stars

# Function to replace health rating with stars using regex
def replace_health_rating_with_stars(response_text: str, health_rating: int, star_rating: str) -> str:
    # Adjust regex pattern to optionally match "**" before and after "健康評分為"
    # Also handle optional spaces and the optional star emoji 🌟 after the rating number
    rating_pattern = re.compile(rf"\*\*?健康評分為\*\*?\s*{health_rating}\s*🌟?")

    # Replace the matched pattern with the full health rating and the star rating
    return rating_pattern.sub(f"**健康評分為** {health_rating}/10 {star_rating}", response_text)


def extract_health_rating(response_text: str) -> int:
    # Use regex to find the health rating pattern that accounts for optional "**" markers and variations
    rating_pattern = re.compile(r"\*\*?健康評分為\*\*?\s*(\d+)\s*🌟")
    
    # Search for the rating in the text
    match = rating_pattern.search(response_text)
    if match:
        # Return the extracted rating as an integer
        return int(match.group(1))
    
    # Default to 0 if no rating is found
    return 0