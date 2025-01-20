import app.database.request as rq
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import app.keyboards as kb

async def notify_inactive_users(bot):
    twoDaysAgo = datetime.now() - timedelta(days=2)

    inactive_users = await rq.get_inactives(twoDaysAgo)

    try:
        for item in inactive_users:
            try:
                await bot.send_message(chat_id=item.tg_id,
                                       text="Давно не было от Вас вестей. :(\nНовости окружают нас, а Вы всё пропускаете!")
                await rq.set_active(item.tg_id)
            except Exception as e:
                print(f"Не удалость отправить сообщение пользователю {item.tg_id}: {e}")
    except:
        print(f"Inactive users weren't found")


async def notify_toReview(bot):
    tenDaysAgo = datetime.now() - timedelta(days=10)

    user_toReview = await rq.get_data_toReview(tenDaysAgo)

    try:
        for item in user_toReview:
            try:
                await bot.send_message(chat_id=item.tg_id,
                                       text="Вы с нами уже 10 дней!. :)\nНапиши, что тебе нравится, а что хотел бы "
                                            "изменить!", reply_markup=kb.keyboard_to_start_review)
                await rq.set_update_data_toReview(item.tg_id)
            except Exception as e:
                print(f"Не удалость отправить сообщение пользователю {item.tg_id}: {e}")
    except:
        print(f"Users to review weren't found")

def start_scheduler(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify_inactive_users, "interval", hours=1, args=(bot,))
    scheduler.add_job(notify_toReview, "interval", hours=1, args=(bot,))
    scheduler.start()
