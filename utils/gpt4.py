import os
import re
from openai import OpenAI
from .chart import extract_nutrition_data, create_nutrition_chart
from .health_rating import extract_health_rating, generate_star_rating,replace_health_rating_with_stars

def escape_markdown_v2(text: str) -> str:
    # Escape all special characters for MarkdownV2 except asterisks (**) for bold
    special_chars = r'_[]()~`>#+-=|{}.!'  # Avoid escaping * so that bold formatting works
    return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)

def getPhotoResponse(chat_history: list, base64_image) -> dict:
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    gpt_user_prompt = "\n This is what I eat now."
    
    # Add emoji instructions to the system prompt
    gpt_assistant_prompt = """You are a health assistant specialized in analyzing food photos. For every meal described or analyzed, your task is to:
    1. List each food item in the meal in the original language, using relevant emojis for each item (e.g., 🍝 for pasta, 🍤 for shrimp, etc.).
    2. Estimate the total calories, carbohydrates, proteins, and fats of the meal, and include the following emojis next to each macronutrient:
        - 🔥 for calories
        - 🍞 for carbohydrates
        - 🍗 for proteins
        - 🥑 for fats
    3. Provide a health rating from 1 to 10, and represent it with stars (e.g., 🌟🌟🌟🌟🌟).
    4. Mention whether the meal is rich in nutrients or contains too much of any specific macronutrient (e.g., high in fats, carbohydrates, etc.).
    5. End with a friendly suggestion or offer to provide more detailed nutritional information if requested.

    Format your response consistently as follows, integrating emojis:

    
    **食物評分 Food Rating**
    這份食物含有
    [List of food items, each with an emoji]

    **總熱量估計為** 🔥 [Estimated total calories] 大卡  
    **總碳水估計為** 🍞 [Estimated total carbohydrates] 克  
    **總蛋白質估計為** 🍗 [Estimated total protein] 克  
    **總脂肪估計為** 🥑 [Estimated total fats] 克  

    **健康評分為** [Health rating] 🌟 (Out of 10)  
    [Short analysis of the meal, mentioning nutritional balance and giving friendly advice.]

    若您想知道更詳細的營養分配，請告訴我。
    Always follow this structure for consistency and clarity, and make the response visually engaging by integrating the appropriate emojis.
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
    
    # Call the GPT-4 API
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use correct model ID
        messages=messages,
        temperature=0.2,
        max_tokens=512,
        frequency_penalty=0.0
    )
    
    # Extract response text
    response_text = response.choices[0].message.content
    tokens_used = response.usage.total_tokens

    # Extract nutrient data from the GPT response
    nutrient_data = extract_nutrition_data(response_text)

    # Extract the health rating using the regex function
    health_rating = extract_health_rating(response_text)
    
    # Generate the dynamic star rating
    star_rating = generate_star_rating(health_rating)
    
    response_text_with_stars = replace_health_rating_with_stars(response_text, health_rating, star_rating)
    
    # Generate chart image (encoded in base64)
    chart_base64 = create_nutrition_chart(nutrient_data)
    
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