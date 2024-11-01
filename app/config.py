from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
CHAT_ID = env.str("CHAT_ID")
SEARCH_KEYWORDS = env.str("SEARCH_KEYWORDS")
INTERVAL_SECONDS = env.int("INTERVAL_SECONDS", 20)

TEMPLATE = (
    "☘️ <b>{title}</b>\n\n"
    "<u>Posted {posted_time}</u>\n"
    "<code>{job_type_label}</code>\n"
    "<u>Experience level: {experience_level}\n"
    "{duration_label}</u>\n\n"
    "{description}"
)
API_BASE_URL = "https://www.upwork.com/nx/search/jobs/"
