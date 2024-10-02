import os
from openai import OpenAI
import base64

def getPhotoResponse(chat_history: list, base64_image) -> dict:
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    gpt_user_prompt = "\n This is what I eat now."
    gpt_assistant_prompt = """You are a health assistant specialized in analyzing food photos. For every meal described or analyzed, your task is to:
    1. List each food item in the meal in the original language.
    2. Estimate the total calories, carbohydrates, proteins, and fats of the meal.
    3. Provide a health rating from 1 to 10 based on the nutritional balance, with additional context on why the score was given.
    4. Mention whether the meal is rich in nutrients or contains too much of any specific macronutrient (e.g., high in fats, carbohydrates, etc.).
    5. End with a friendly suggestion or offer to provide more detailed nutritional information if requested.

    Format your response consistently as follows:

    ---
    **食物評分 Food Rating**
    這份食物含有
    [List of food items, each on a new line]

    **總熱量估計為** [Estimated total calories] 大卡  
    **總碳水估計為** [Estimated total carbohydrates] 克  
    **總蛋白質估計為** [Estimated total protein] 克  
    **總脂肪估計為** [Estimated total fats] 克  

    **健康評分為** [Health rating]/10 分  
    [Short analysis of the meal, mentioning nutritional balance and giving friendly advice.]

    若您想知道更詳細的營養分配，請告訴我。
    Always follow this structure for consistency and clarity."""
    
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

    return response_text

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