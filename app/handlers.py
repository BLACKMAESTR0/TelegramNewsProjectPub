from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from app.states import Register, News, Search, Notes, Review
import app.keyboards as kb
import app.database.request as rq
from config import *
import re
import asyncio

main_photo_path = MAIN_PHOTO_PATH
router = Router()


async def excape_markdownV2(text):
    special_characters = r'[_*[\]()~`>#+\-=|{}.!]'

    return re.sub(f"({special_characters})", r"\\\1", text)


async def special_message(text, message: Message):
    s = text
    for _ in range(2):
        for i in range(1, 6):
            await message.edit_text(s + i * ".")
            await asyncio.sleep(0.1)
        for i in range(4, -1, -1):
            await message.edit_text(s + i * ".")
            await asyncio.sleep(0.1)

async def notes_menu(event, data, page):

    listOfArticles = []
    if data:
        listOfArticles = data.split(NOTES_SEP)
    if isinstance(event, Message):
        await event.answer(text='Доступные заметки:', reply_markup=await kb.notes_builder(listOfArticles, page=page))
        return
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text='Доступные заметки:', reply_markup=await kb.notes_builder(listOfArticles,
                                                                                                     page=page))
        await event.answer()
        return

@router.message(Review.minuses)
async def rev_to_bd(message: Message, state: FSMContext):
    data = await state.get_data()
    pluses = data.get("pluses", '')
    minuses = message.text
    await rq.set_review(message.from_user.id, pluses, minuses)
    await state.clear()
    await message.answer("Спасибо! Анкета заполнена.")
    await message.answer("Выберите интересующий пункт меню.", reply_markup=kb.main_keyboard)

@router.message(Review.pluses)
async def cont_rev(message: Message, state: FSMContext):
    await state.update_data(pluses=message.text)
    await state.set_state(Review.minuses)
    await message.answer(text='Пожалуйста, введите то, что Вы хотели бы изменить. :(')
@router.callback_query(F.data == "start_review")
async def start_rev(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Review.pluses)
    await callback.message.answer(text='Пожалуйста, введите то, что Вам особенно нравится при работе с нами. :)')
@router.callback_query(F.data.startswith("notes_article_"))
async def open_note(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_reply_markup(reply_markup=None)

    article = callback.data
    article, note = await rq.get_note_by_article(callback.from_user.id, article)
    article = callback.data.replace("notes_article_", "")
    mess = f"{article}\n{note}"
    await state.update_data(article=article)
    await callback.message.answer(mess, parse_mode="MarkdownV2", reply_markup=kb.keyboard_back_from_add_note)


@router.callback_query(F.data == "delete_note")
async def del_note(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    article = data.get("article")
    await rq.del_note(callback.from_user.id, article)
    await notes_menu_some(callback, state)

@router.message(F.text == "Заметки ✒️")
async def notes_menu_first(message: Message, state: FSMContext):
    data = await rq.note_menu(message.from_user.id)
    page = 0
    await notes_menu(message, data, page)

@router.callback_query(F.data == "notes_backward")
async def notes_go_back(callback: CallbackQuery, state: FSMContext):
    stateData = await state.get_data()
    currPage = stateData.get("page", 0)
    await state.update_data(page=currPage-1)
    data = await rq.note_menu(callback.from_user.id)
    page = currPage-1
    await notes_menu(callback, data, page)

@router.callback_query(F.data == "notes_forward")
async def notes_go_forward(callback: CallbackQuery, state: FSMContext):
    stateData = await state.get_data()
    currPage = stateData.get("page", 0)
    await state.update_data(page=currPage + 1)
    data = await rq.note_menu(callback.from_user.id)
    page = currPage + 1
    await notes_menu(callback, data, page)

@router.callback_query(F.data == "menu_notes")
async def notes_menu_some(callback: CallbackQuery, state: FSMContext):
    stateData = await state.get_data()
    page = stateData.get("page", 0)
    if state:
        await state.clear()
    data = await rq.note_menu(callback.from_user.id)
    await notes_menu(callback, data, page)
@router.callback_query(F.data == "close_call_toMenu")
async def close_call_toMenu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выберите интересующий пункт меню.", reply_markup=kb.main_keyboard)

@router.callback_query(F.data == "add_note")
async def add_note(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Notes.article)
    await callback.message.answer("Введите заголовок:", reply_markup=kb.keyboard_back_from_add_note)


@router.message(Notes.article)
async def add_content(message: Message, state: FSMContext):
    await state.update_data(article=message.text)
    await state.set_state(Notes.content)
    await message.answer("Введите заметку:")

@router.message(Notes.content)
async def demo_add(message: Message, state: FSMContext):

    data = await state.get_data()
    content = message.text
    article = data.get("article")
    contentForMess = await excape_markdownV2(content)
    articleForMess = f"*{await excape_markdownV2(article)}*"

    await state.update_data(content=contentForMess, article=articleForMess)

    mess = f"{articleForMess}\n{contentForMess}"
    await message.answer(mess, parse_mode="MarkdownV2", reply_markup=kb.keyboard_add_or_no_not)

@router.callback_query(F.data == "add_note_bd")
async def add_note_bd(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    article = data.get("article")
    content = data.get("content")
    page = data.get("page", 0)
    if state:
        await state.clear()

    await rq.add_note(tg_id=callback.from_user.id,
                      article=article,
                      note=content)
    data = await rq.note_menu(callback.from_user.id)
    await notes_menu(callback, data, page)


@router.callback_query(F.data == "go_backward_searched")
async def go_backward_searched(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    listOfNewsSearched = data.get("listOfNews")
    page = data.get("page", 0)

    if page == 0:
        await state.update_data(page=len(listOfNewsSearched) - 1)
        await serched_on_page(callback, state)
    else:
        await state.update_data(page=page - 1)
        await serched_on_page(callback, state)


@router.callback_query(F.data == "go_forward_searched")
async def go_backward_searched(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    listOfNewsSearched = data.get("listOfNews")
    page = data.get("page", 0)

    if page == len(listOfNewsSearched) - 1:
        await state.update_data(page=0)
        await serched_on_page(callback, state)
    else:
        await state.update_data(page=page + 1)
        await serched_on_page(callback, state)


@router.callback_query(F.data == "get_result")
async def serched_on_page(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Загружаем результаты")
    data = await state.get_data()
    listOfNewsSearched = data.get("listOfNews")
    page = data.get("page", 0)

    article = f"*{await excape_markdownV2(listOfNewsSearched[page]['data']['article'])}*"
    caption = f"{article}\n{await excape_markdownV2(listOfNewsSearched[page]['data']['text'])}"

    pathToImg = listOfNewsSearched[page]["data"]["linkToImg"] if listOfNewsSearched[page]["data"][
        "linkToImg"] else main_photo_path
    await callback.message.edit_media(
        media=InputMediaPhoto(media=pathToImg, caption=caption,
                              parse_mode="MarkdownV2"),
        reply_markup=kb.keyboard_scrolling_searched
    )


@router.message(Search.key)
async def search(message: Message, state: FSMContext):
    word = message.text.split(" ")[0]
    if state:
        await state.clear()
    text = f"Выполняю поиск по слову {word}"
    logging_message = await message.answer(text)
    await special_message(text, logging_message)
    await logging_message.delete()
    dataSearched = await rq.search_data(word)
    if dataSearched:
        await state.update_data(listOfNews=dataSearched)
        await message.answer(f"Найдено {len(dataSearched)} результатов.", reply_markup=kb.keyboard_result)
    else:
        await message.answer(f"Найдено {len(dataSearched)} результатов.", reply_markup=kb.keyboard_bad_result)


@router.message(F.text == "Поиск по ключу 🔍")
async def search(message: Message, state: FSMContext):
    if state:
        await state.clear()
    await state.set_state(Search.key)
    await message.answer("Введите ключ-слово для поиска.")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    if state:
        await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выберите интересующий пункт меню.", reply_markup=kb.main_keyboard)


@router.callback_query(F.data == "like")
async def add_category(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await rq.like_news(callback.from_user.id, data.get("page"), data.get("listOfNews"))
    await callback.answer("Новость была лайкнута!")


@router.callback_query(F.data == "go_backward")
async def go_backward(callback: CallbackQuery, state: FSMContext):
    stateData = await state.get_data()
    currentPage = stateData.get("page", 1) - 1
    await state.update_data(page=currentPage)
    listOfNews = stateData.get("listOfNews", [])

    if currentPage < 0:
        await state.update_data(page=len(listOfNews) - 3)
        await go_forward(callback, state)
        return

    else:
        article = f"*{await excape_markdownV2(listOfNews[currentPage]['data']['article'])}*"
        caption = f"{article}\n{await excape_markdownV2(listOfNews[currentPage]['data']['text'])}"

        if listOfNews[currentPage]["data"]["linkToImg"]:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=listOfNews[currentPage]["data"]["linkToImg"], caption=caption,
                                      parse_mode="MarkdownV2"),
                reply_markup=kb.keyboard_scrolling
            )
        else:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=main_photo_path, caption=caption, parse_mode="MarkdownV2"),
                reply_markup=kb.keyboard_scrolling
            )


@router.callback_query(F.data == "go_forward")
async def go_forward(callback: CallbackQuery, state: FSMContext):
    stateData = await state.get_data()
    currentPage = stateData.get("page", 0) + 1

    await state.update_data(page=currentPage)
    listOfNews = stateData.get("listOfNews", [])

    if currentPage > len(listOfNews) - 2:
        await reload(callback, state)
        return

    else:
        article = f"*{await excape_markdownV2(listOfNews[currentPage]['data']['article'])}*"
        caption = f"{article}\n{await excape_markdownV2(listOfNews[currentPage]['data']['text'])}"

        if listOfNews[currentPage]["data"]["linkToImg"]:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=listOfNews[currentPage]["data"]["linkToImg"], caption=caption,
                                      parse_mode="MarkdownV2"),
                reply_markup=kb.keyboard_scrolling
            )
        else:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=main_photo_path, caption=caption, parse_mode="MarkdownV2"),
                reply_markup=kb.keyboard_scrolling
            )


@router.callback_query(F.data == "reload")
async def reload(callback: CallbackQuery, state: FSMContext):
    listOfNews = await rq.get_list_of_news(callback.from_user.id)
    await state.update_data(listOfNews=listOfNews, page=0)

    article = f"*{await excape_markdownV2(listOfNews[0]['data']['article'])}*"
    caption = f"{article}\n{await excape_markdownV2(listOfNews[0]['data']['text'])}"

    await callback.answer(text='Обновление')

    if listOfNews[0]["data"]["linkToImg"]:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=listOfNews[0]["data"]["linkToImg"], caption=caption, parse_mode="MarkdownV2"),
            reply_markup=kb.keyboard_scrolling
        )
    else:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=main_photo_path, caption=caption, parse_mode="MarkdownV2"),
            reply_markup=kb.keyboard_scrolling
        )


@router.message(F.text == "Читать новости 📰")
async def news_reading(message: Message, state: FSMContext):
    if state:
        await state.clear()
    await state.set_state(News.scrollingNews)

    listOfNews = await rq.get_list_of_news(message.from_user.id)
    await state.update_data(listOfNews=listOfNews, page=0)

    article = f"*{await excape_markdownV2(listOfNews[0]['data']['article'])}*"
    caption = f"{article}\n{await excape_markdownV2(listOfNews[0]['data']['text'])}"

    if listOfNews[0]["data"]["linkToImg"]:

        await message.answer_photo(
            caption=caption,
            parse_mode="MarkdownV2",
            photo=listOfNews[0]["data"]["linkToImg"],
            reply_markup=kb.keyboard_scrolling
        )
    else:
        await message.answer(
            text=caption,
            parse_mode="MarkdownV2",
            reply_markup=kb.keyboard_scrolling
        )


@router.message(F.text == "Профиль 🙃")
async def profile(message: Message):
    data = await rq.get_profile(message.from_user.id)
    await message.answer(text=f"Ваше имя: *{data.name}*\nВаши предпочтения: *{data.best_cat.replace(';', ', ')}*",
                         parse_mode="MarkdownV2", reply_markup=kb.rebuild_profile_keyboard)


async def categoryIn(state: FSMContext):
    data = await state.get_data()
    return data, data.get('categories', [])


@router.callback_query(F.data == "confirm_cat", Register.categories)
async def confirm_cat(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await rq.set_info(name=data.get("name", ""), tg_id=callback.from_user.id, categories=data.get("categories", []))
    if state:
        await state.clear()
    await callback.answer("Данные обновлены")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Профиль заполнен! Выберите интересующий пункт меню.", reply_markup=kb.main_keyboard)


@router.message(Command('profile'))
async def profile_print(message: Message):
    data = await rq.get_profile(message.from_user.id)
    await message.answer(text=f"Ваше имя: *{data.name}*\nВаши предпочтения: *{data.best_cat.replace(';', ', ')}*",
                         parse_mode="MarkdownV2")


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        text='Добро пожаловать\\! \nЭто новостной бот *ExtremeNews*, адаптирующийся к вашим предпочтениям\\.'
             '\nДля начала \\- *пройдите регистрацию*\\.', reply_markup=kb.register_keyboard, parse_mode="MarkdownV2")


@router.callback_query(F.data == 'start_reg')
async def start_reg(callback: CallbackQuery, state: FSMContext):
    if state:
        await state.clear()
    await callback.answer("Начало регистрации")
    await state.set_state(Register.name)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Как мы можем называть Вас?")


@router.message(Register.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.categories)
    data, listOfCat = await categoryIn(state)
    await message.answer(f"Выберите интересующие категории, {data['name']}.",
                         reply_markup=await kb.keyboard_categories(listOfCat))


@router.message(Register.categories)
async def categ_reg(message: Message, state: FSMContext):
    data, listOfCat = await categoryIn(state)
    await message.answer(f"Выберите интересующие категории, {data['name']}.",
                         reply_markup=await kb.keyboard_categories(listOfCat))


@router.callback_query(F.data.startswith("category_"))
async def add_or_delete_cat(callback: CallbackQuery, state: FSMContext):
    data, listOfCat = await categoryIn(state)
    category = callback.data.split('_')[1]
    if category in listOfCat:
        listOfCat.remove(category)
    else:
        listOfCat.append(category)
    await state.update_data(categories=listOfCat)

    if "name" in data:
        cat_names = data["name"]
    else:
        cat_names = []
    if listOfCat:
        await callback.message.edit_text(
            text=f"Выберите интересующие категории, {cat_names}\\.\nВыбранные: *{', '.join(listOfCat)}*\\.",
            parse_mode="MarkdownV2", reply_markup=await kb.keyboard_categories(listOfCat))
    else:
        await callback.message.edit_text(text=f"Выберите интересующие категории, {cat_names}.",
                                         reply_markup=await kb.keyboard_categories(listOfCat))


####################################################################################################################


@router.message()
async def fallback_handler(message: Message):
    await message.answer("Извините, я не понимаю, что вы имеете ввиду.\nВыберите интересующий пункт меню.",
                         reply_markup=kb.main_keyboard)
