# Telegram-Bot

#### LipoOut Official Telegram bot for Miniapp, uploading food photo and recording users' information
An intelligent Telegram bot that helps users track their nutrition and fitness goals using AI-powered image analysis and natural language processing. The bot can analyze food photos, provide nutritional information, and offer personalized health advice.

### Bot url:  [t.me/Fit_ioBot](https://t.me/Fit_ioBot)

## In-bot Usage
- Use `/start` command to start the bot.
- The bot will ask you to select your __health goal__.
- After selecting your health goal, the bot will ask you to upload a photo.
- The bot will analyze the photo and give you a report and a chart.
- *(Beta)* You can choose to store your photo and data in your record.
- *(Beta)* Use `/pay` command to pay for the service.
- Use `/cancel` command to cancel the current operation.
- You can also chat with the bot by sending messages and the bot will remember your conversation.

## How to run
### Installation
- Install python 3.11 or later.
- Install [poetry](https://python-poetry.org/docs/#installation).
- Use command `make install` to install all the dependancies in poetry.
- Use command `make run` to run the telegram bot.

## Key Features
- User goal setting and profile management
- Real-time food photo analysis
- Nutritional content estimation
- Visual nutrition charts
- Meal history tracking
- Interactive conversations about health and nutrition
- Payment integration

## Technical Architecture &Implementation
1. Main Bot Application (`main.py`)
   - Handles bot initialization and conversation flow
   - Manages user states and interactions
   - Implements command handlers and callbacks
2. Utilities Package (`utils/`)
   - `gpt4.py`: OpenAI GPT-4 integration for image and text analysis
   - `chart.py`: Nutrition visualization generation
   - `save_food_to_db.py`: Database operations for meal tracking
   - `health_rating.py`: Health rating calculations and formatting

### State Flow
```
graph TD
    A[Start] --> B[Health State]
    B --> C[Photo State]
    C --> D[Reply State]
    D --> E[End State]
```

### Key Classes and Functions
#### ConversationHandler States
```python
class State(Enum):
    HEALTH_STATE = 1
    PHOTO = 2
    REPLY_PHOTO = 3
    REPLY_TEXT = 4
    END = 5
```

### Main Handlers
1. Start Handler
   - Initializes user profile
   - Stores user information in database
   - Sets up conversation context
2. Health State Handler
   - Manages user health goal selection
   - Provides interactive goal buttons
   - Updates user profile with selected goal
3. Photo Handler
   - Processes uploaded food images
   - Triggers AI analysis
   - Generates nutrition charts
   - Offers meal saving options

## API Integration
### OpenAI GPT-4
- Used for image analysis and natural language understanding
- Custom prompts for consistent formatting
- Nutrition extraction and health scoring

### Backend API
- RESTful endpoints for user management
- Food entry storage and retrieval
- User profile updates

## Data Models
### User Profile
```python
user_data = {
    "name": str,
    "age": int,
    "height": float,
    "weight": float,
    "telegram_id": int,
    "goal": str
}
```


### Food Entry
```python
food_data = {
    "user_id": int,
    "food_analysis": str,
    "food_photo": bytes,
    "calories": float,
    "carb": float,
    "protein": float,
    "fat": float
}
```

## Setup and Configuration
### Environment Variables
```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
API_BASE_URL=your_backend_api_url
```
## Dependencies
```
python-telegram-bot
openai
Pillow
matplotlib
requests
python-dotenv
```

## Future Enhancements
1. Multi-language support
2. Progress tracking and analytics  
3. Social sharing features (ex. Instagram)
4. Integration with fitness tracking devices