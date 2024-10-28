# save_food_to_db.py

import requests
import base64
from .chart import extract_nutrition_data

API_BASE_URL = "http://127.0.0.1:8000"  # Adjust this URL to your backend

def write_food_photo_to_db(telegram_id: int, photo: bytes, response_text: str):
    # Step 1: Get the user by telegram_id
    user_response = requests.get(f"{API_BASE_URL}/users/?telegram_id={telegram_id}")
    
    if user_response.status_code == 404 or not user_response.json():
        print("User not found.")
        return  # Optionally handle user not found by creating a new user or raising an error
    elif user_response.status_code != 200:
        print("Failed to fetch user:", user_response.json())
        return

    # Extract user_id from the response (assuming the first result)
    user_data = user_response.json()[0]  # Access the first item in the list
    user_id = user_data["id"]

    # Step 2: Extract nutrition data
    nutrition_data = extract_nutrition_data(response_text)
    
    # Prepare data for the POST request
    food_data = {
        "user_id": user_id,
        "food_analysis": response_text,
        "food_photo": base64.b64encode(photo).decode("utf-8"),  # Encode photo in base64
        "calories": nutrition_data["calories"],
        "carb": nutrition_data["carbohydrates"],
        "protein": nutrition_data["protein"],
        "fat": nutrition_data["fats"]
    }

    # Step 3: Make the POST request to create a food entry
    response = requests.post(f"{API_BASE_URL}/foods/", json=food_data)
    
    # Check if the request was successful
    if response.status_code == 201:
        print("Photo and analysis successfully stored in the database.")
    else:
        print("Failed to store photo and analysis:", response.json())