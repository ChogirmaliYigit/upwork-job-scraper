import asyncio
import signal
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .config import BOT_TOKEN, INTERVAL_SECONDS
from .db import initialize_db
from .parser import get_upwork_jobs


async def on_startup(bot: Bot, scheduler: AsyncIOScheduler) -> None:
    """Starts the scheduler and schedules the job."""
    scheduler.add_job(
        func=get_upwork_jobs,
        trigger="interval",
        seconds=INTERVAL_SECONDS,
        kwargs={"bot": bot},
        max_instances=5,
    )
    scheduler.start()
    print("scheduler started")


async def on_shutdown(scheduler: AsyncIOScheduler, **kwargs):
    scheduler.shutdown(wait=False)


def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    scheduler = AsyncIOScheduler()

    # Initialize database
    initialize_db()

    dp = Dispatcher()
    dp["scheduler"] = scheduler

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    asyncio.run(dp.start_polling(bot, close_bot_session=True))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Application shut down.")
