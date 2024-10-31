import asyncio
import random

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from . import config
from .db import add_project, project_exists


async def get_upwork_jobs(bot: Bot) -> None:
    print("get_upwork_jobs started")
    async with async_playwright() as p:
        params = {
            "q": config.SEARCH_KEYWORDS,
            "sort": "recency",
            "page": 1,
            "per_page": 10,
        }
        url = f"{config.API_BASE_URL}?" + "&".join(
            f"{key}={val}" for key, val in params.items()
        )

        browser = await p.chromium.launch(headless=False)  # headless mode
        context = await browser.new_context()

        # Go to the page
        page = await context.new_page()
        await page.goto(url)

        # Wait for the page to load
        content = await page.content()  # Get the page content
        await context.close()
        await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        print("soup available")

        jobs_container = soup.find("section", {"class": "card-list-container", "data-test": "JobsList"})

        if not jobs_container:
            print("jobs_container not available")
            print(soup)
            return

        jobs = jobs_container.find_all_next("article")

        if not jobs:
            print("jobs not available", jobs)
            print(soup)
            return

        print("jobs available")

        for job in jobs:
            project_id = job["data-ev-job-uid"]
            if project_exists(project_id):
                continue

            title_container = job.find("div", {"class": "job-tile-header"})
            if not title_container:
                continue
            title_header = title_container.find(
                "div", {"data-test": "JobTileHeader"}
            )
            title_a = title_header.find_next("a", {"class": "up-n-link"})
            title = title_a.text
            link = "https://upwork.com" + title_a["href"]
            posted_time = title_header.find_all("span")[-1].text

            title_details_container = job.find("div", {"data-test": "JobTileDetails"})
            description = title_details_container.find("p", recursive=True).text
            ul = title_details_container.find("ul", recursive=True)
            job_type_li = ul.find("li", {"data-test": "job-type-label"})
            experience_li = ul.find("li", {"data-test": "experience-level"})
            duration_li = ul.find("li", {"data-test": "duration-label"})
            if not job_type_li or not experience_li or not duration_li:
                continue
            job_type_label = job_type_li.find("strong").text
            experience_level = experience_li.find("strong").text
            duration_label = " ".join([strong.text for strong in duration_li.find_all("strong")])

            await bot.send_message(
                chat_id=config.CHAT_ID,
                text=config.TEMPLATE.format(
                    title=title,
                    posted_time=posted_time,
                    job_type_label=job_type_label,
                    experience_level=experience_level,
                    duration_label=duration_label,
                    description=description[:3000],
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="Go to the job", url=link)
                        ],
                    ],
                ),
                parse_mode=ParseMode.HTML,
            )

            add_project(project_id)

            await asyncio.sleep(random.choice([1, 2, 3]))
