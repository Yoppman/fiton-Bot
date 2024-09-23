import sqlite3
import os
from datetime import datetime
from telegram import Bot
from openai import OpenAI


class UserTracker:
    def __init__(self, db_path: str, bot_token: str):
        # Initialize the database connection and the Telegram bot
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.bot = Bot(token=bot_token)
        self._create_table()

    def _create_table(self):
        """Create a table to store user interaction data."""
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                last_interaction TEXT
            )
            '''
        )
        self.conn.commit()

    def update_last_interaction(self, user_id: int):
        """Update the last interaction time for a user."""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(
            '''
            INSERT INTO users (user_id, last_interaction)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_interaction=excluded.last_interaction
            ''', (user_id, current_time)
        )
        self.conn.commit()

    def get_days_since_last_interaction(self, user_id: int) -> int:
        """Get the number of days since the user's last interaction."""
        self.cursor.execute('SELECT last_interaction FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()

        if result:
            last_interaction = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            days_inactive = (datetime.now() - last_interaction).days
            return days_inactive
        return None
    
    def generate_gpt_reminder(self, user_id: int, days_inactive: int) -> str:
        """Generate a reminder message using GPT based on inactivity."""
        messages= [
            {
                "role": "system", 
                "content": "你是一位帶點幽默和調皮的健康教練，目的是鼓勵使用者回到健康飲食的軌道。當使用者一段時間沒和你互動時，你會用輕微嘲諷的方式提醒他們可能因為沒有紀錄飲食而偏離了健康的生活方式。你的語氣可以幽默且直接，例如輕輕嘲笑他們可能胖了或偷偷吃了不健康的食物。同時，你也要在最後用積極正面的語氣鼓勵他們重新開始記錄飲食和回到健康生活。保持對話的輕鬆有趣，但要確保傳達健康飲食的重要性。"
            },
            {
                "role": "user", 
                "content": f"我已經 {days_inactive} 天沒有上傳飲食紀錄了."
            }
        ]

        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Generate response from OpenAI GPT
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=1.5,
            max_tokens=50,
        )
        
        return response.choices[0].message.content

    def send_reminder(self, user_id: int, days_inactive: int):
        """Send a reminder to the user"""
        reminder_message = self.generate_gpt_reminder(user_id, days_inactive)
        self.bot.send_message(chat_id=user_id, text=reminder_message)

    def check_inactive_users(self, inactivity_threshold: int = 3):
        """Check for inactive users and send reminders if they exceed the inactivity threshold."""
        self.cursor.execute('SELECT user_id FROM users')
        users = self.cursor.fetchall()

        for user in users:
            user_id = user[0]
            days_inactive = self.get_days_since_last_interaction(user_id)

            if days_inactive and days_inactive >= inactivity_threshold:
                self.send_reminder(user_id)

    def close(self):
        """Close the database connection."""
        self.conn.close()