import os
import re
from openai import OpenAI
from .chart import extract_nutrition_data, create_nutrition_chart, is_food
from .health_rating import extract_health_rating, generate_star_rating,replace_health_rating_with_stars

def escape_markdown_v2(text: str) -> str:
    # Escape all special characters for MarkdownV2 except asterisks (**) for bold
    special_chars = r'_[]()~`>#+-=|{}.!'  # Avoid escaping * so that bold formatting works
    return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)

def getPhotoResponse(chat_history: list, base64_image) -> dict:
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    gpt_user_prompt = "\n This is what I eat or drink now."
    
    # Add emoji instructions to the system prompt
    gpt_assistant_prompt = """You are a health assistant specialized in analyzing food photos. For every meal described or analyzed, your task is to:
    1. List each **dish** or **beverage** in the meal in the original language, using relevant emojis for each item (e.g., 🍝 for pasta, 🍔 for hamburger, ☕ for coffee, 🫖 for tea, etc.). **You do not need to list individual ingredients within the dish** (e.g., for a hamburger, list "hamburger" instead of "tomato, lettuce, beef, etc.").
    2. Estimate the total calories, carbohydrates, proteins, and fats of the meal, and include the following emojis next to each macronutrient:
        - 🔥 for calories
        - 🍞 for carbohydrates
        - 🍗 for proteins
        - 🥑 for fats
    3. Provide a health rating from 1 to 10, and represent it with stars (e.g., 🌟🌟🌟🌟🌟).
    4. Mention whether the meal is rich in nutrients or contains too much of any specific macronutrient (e.g., high in fats, carbohydrates, etc.).
    5. If the meal only contains drinks like water, coffee, tea, you still need to analyze and include them, even if they have minimal or no macronutrients. Highlight their contribution (e.g., hydration, low-calorie nature) in the analysis.
    6. End with a friendly suggestion or offer to provide more detailed nutritional information if requested.

    Format your response consistently as follows, integrating emojis:

    **Food Rating**
    This meal contains:
    [List of food items (dishes and beverages), each with an emoji, including drinks like coffee, tea, or water. Do not list individual ingredients.]

    **Total calories** 🔥 [Estimated total calories] kcal  
    **Total carbohydrates** 🍞 [Estimated total carbohydrates] grams  
    **Total protein** 🍗 [Estimated total protein] grams  
    **Total fats** 🥑 [Estimated total fats] grams  

    **Health rating** [Health rating] 🌟 (Out of 10)  
    [Short analysis of the meal, mentioning nutritional balance, including the contribution of drinks like coffee, tea, or water, and giving friendly advice.]

    If you would like more detailed nutritional information, please let me know.

    Always follow this structure for consistency and clarity, and make the response visually engaging by integrating the appropriate emojis.

    If you think there is no food or drink in the image, reply with one of the following:
    1. "Hmm... this doesn't look like a delicious dish! How about trying to send another food photo? 🤡"
    2. "This isn't something you'd want to eat! My stomach only recognizes food! How about trying a pizza or sushi? 🤡🍕🍣"
    3. "Wow, this surely isn't tonight's dinner! 🤡 I can only help you analyze food—how about sending a picture of a meal?"
    4. "Looks cool, but I can only recognize food... I guess you didn't want to eat this, right? 🤡 How about sending another food picture?"
    5. "This picture is unique! But as a food expert, I can only identify meals 🤡 Want to send a tasty food photo instead?"
    6. "Hey, this is testing my intelligence! This isn't food, is it? 🤡 Send another food photo; I'm getting hungry!"
    7. "This seems inedible! How about sending a picture of something that looks tastier? I can't wait to analyze it! 🤡"
    8. "Hmm... I only recognize food! How about considering sending a photo that'll make me hungry? 🤡"
    """
    
    # Construct messages including the image as base64
    messages = [{"role": "system", "content": gpt_assistant_prompt}] + chat_history
    messages += [
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": gpt_user_prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]
        }
    ]
    
    chart_base64 = None
    response_text_with_stars = None
    # Call the GPT-4 API
    response = client.chat.completions.create(
        model="gpt-4o",  # Use correct model ID
        messages=messages,
        temperature=0.2,
        max_tokens=512,
        frequency_penalty=0.0
    )
    
    # Extract response text
    response_text = response.choices[0].message.content
    tokens_used = response.usage.total_tokens

    if is_food(response_text):
        # Extract nutrient data from the GPT response
        nutrient_data = extract_nutrition_data(response_text)

        # Extract the health rating using the regex function
        health_rating = extract_health_rating(response_text)
        
        # Generate the dynamic star rating
        star_rating = generate_star_rating(health_rating)
        
        response_text_with_stars = replace_health_rating_with_stars(response_text, health_rating, star_rating)
        # Generate chart image (encoded in base64)
        chart_base64 = create_nutrition_chart(nutrient_data)
    else:
        chart_base64 = None
        response_text_with_stars = response_text

    return {
        "text_response": response_text_with_stars,
        "chart_image_base64": chart_base64
    }

    
def getTextResponse(chat_history: list) -> str:
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    gpt_assistant_prompt = """
    You are a professional health assistant. 
    
    Your sole purpose is to provide expert advice and information related to health, nutrition, and wellness. 
    
    You must ensure that all responses are strictly related to health topics, including but not limited to food, nutrition, exercise, and overall well-being.

    You are not allowed to engage in casual conversation or respond to prompts unrelated to health. 
    
    If the user asks questions that fall outside the scope of health, gently remind them that you can only assist with health-related topics.

    Maintain a professional, informative, and respectful tone at all times.

    Your answer should not exceed 500 words.
    """
    
    # Construct the messages with the chat history
    messages = [{"role": "system", "content": gpt_assistant_prompt}] + chat_history
    
    # Call the GPT-4 API with the complete chat history
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use correct model ID
        messages=messages,
        temperature=0.2,
        max_tokens=1024,
        frequency_penalty=0.0
    )
    
    # Extract response text
    response_text = response.choices[0].message.content
    return response_text