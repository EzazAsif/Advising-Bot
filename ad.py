import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import time

# Replace with your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = '7157423384:AAFmzfqrQHStRQKRTnA-XOKKWjI71fOnnVI'
TELEGRAM_CHAT_ID = '-1002137053797'
count=0
async def send_telegram_message(bot, message, retries=3):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending message: {e}")
        if isinstance(e, telegram.error.RetryAfter):
            retry_delay = e.retry_after
            print(f"Retrying after {retry_delay} seconds.")
            await asyncio.sleep(retry_delay)
            retries -= 1
            if retries > 0:
                await send_telegram_message(bot, message, retries=retries)
            else:
                print("Maximum retry attempts reached. Skipping message.")
        else:
            # Log other exceptions for further analysis
            print(f"Unhandled exception: {e}")

async def check_seats(bot):
    url = 'https://rds2.northsouth.edu/index.php/common/showofferedcourses'  # Replace with the actual URL of the page
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table row that contains the desired courses and check the seats available
        courses = ['CSE373', 'CSE273', 'CSE445']
        table = soup.find('table', {'id': 'offeredCourseTbl'})
        rows = table.find_all('tr')
        
        for course in courses:
            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 0 and course in cells[1].text:
                    seats_available = int(cells[6].text.strip())
                    if seats_available > 0:
                        message = f'Seats available for {course}.{cells[2].text.strip()}: {seats_available}'
                        print(message)
                        await send_telegram_message(bot, message)
                        await asyncio.sleep(3)  # Add a small delay between messages to avoid flood control
                        
    except Exception as e:
        print(f"Error retrieving data: {e}")

async def main():
    if count=2:
        await send_telegram_message(bot, 'Sever alive check')
        count=0
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    while True:
        print("Running check...")
        await check_seats(bot)
        await asyncio.sleep(300)  # Wait for 300 seconds (5 minutes) before checking again
        count++
if __name__ == '__main__':
    asyncio.run(main())
