import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
GOOGLE_TOKEN = str(os.getenv("GOOGLE_TOKEN"))

host = os.getenv("PG_HOST")
port = os.getenv("PG_POR")
PG_USER = os.getenv("PG_USER")
PG_PASS = os.getenv("PG_PASS")
DB_NAME = os.getenv("DB_NAME")

END_LATITUDE = os.getenv('end_latitude')
END_LONGITUDE = os.getenv('end_longitude')
BIRTHDAY_NOTIFICATION_TIME = os.getenv('birthday_notification_time')
BEFORE_BIRTHDAY_DAYS = os.getenv('before_birthday_days')

# Ссылка подключения к базе данных
POSTGRES_URI = f"postgresql://{PG_USER}:{PG_PASS}@{host}/{DB_NAME}"


admins = [
    os.getenv("ADMIN_ID"),
]

ip = os.getenv("ip")

aiogram_redis = {
    'host': ip,
}

# job_stores = {
#     "default": RedisJobStore(
#         jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running",
#         # параметры host и port необязательны, для примера показано как передавать параметры подключения
#         host="localhost", port=6379
#     )
# }
