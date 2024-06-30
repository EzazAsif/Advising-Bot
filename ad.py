import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import time
from datetime import datetime
import pytz
import telegram.error

dhaka_tz = pytz.timezone('Asia/Dhaka')

# Get the current time in Dhaka

# Replace with your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = '7157423384:AAFmzfqrQHStRQKRTnA-XOKKWjI71fOnnVI'
TELEGRAM_CHAT_ID = '-1002137053797'
count = 0
flag=False
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
    global flag
    flag=False
    url = 'https://rds2.northsouth.edu/index.php/common/showofferedcourses'  # Replace with the actual URL of the page
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table row that contains the desired courses and check the seats available
        courses = ['CSE373', 'CSE273', 'CSE445','EEE141']
        table = soup.find('table', {'id': 'offeredCourseTbl'})
        rows = table.find_all('tr')
        
        for course in courses:
            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 0 and course in cells[1].text:
                    seats_available = int(cells[6].text.strip())
                    if seats_available > 0:
                        flag=True
                        message = f'Seats available for {course}.{cells[2].text.strip()}: {seats_available} '
                        print(message)
                        await send_telegram_message(bot, message)
                        await asyncio.sleep(3)
        if flag:                
            dhaka_time = datetime.now(dhaka_tz)
            await send_telegram_message(bot,f'{dhaka_time.strftime("%H:%M")} [Last Updated :3 ]' )
            
                        
    except Exception as e:
        print(f"Error retrieving data: {e}")

async def main():
    global count
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    while True:
        print("Running check...")
        await check_seats(bot)
        await asyncio.sleep(300)  # Wait for 300 seconds before checking again
        count += 1
        if count == 12:  # Check every 2 iterations (every 1 minute)
            dhaka_time = datetime.now(dhaka_tz)
            check= f'Server alive check {dhaka_time.strftime("%H:%M")}'
            await send_telegram_message(bot, check)
            count = 0

if __name__ == '__main__':
    asyncio.run(main())
