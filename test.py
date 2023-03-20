import aiocron
import asyncio

@aiocron.crontab('*/30 * * * *')
async def attime():
    print('run')

asyncio.get_event_loop().run_forever()