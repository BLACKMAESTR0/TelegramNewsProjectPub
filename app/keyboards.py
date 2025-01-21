from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import START_CATEGORIES, SPECIFIC_CYMBALS

register_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пройти регистрацию', callback_data='start_reg')]
])

rebuild_profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Редактировать', callback_data='start_reg')]
])

keyboard_scrolling = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Лайк ❤️', callback_data="like")],
    [InlineKeyboardButton(text="← Назад", callback_data="go_backward"),
     InlineKeyboardButton(text="Далее →", callback_data="go_forward")],
    [InlineKeyboardButton(text="Обновить 🔄", callback_data="reload")],
    [InlineKeyboardButton(text="В меню 📌", callback_data="back_to_menu")]
])

keyboard_scrolling_searched = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Лайк ❤️', callback_data="like")],
    [InlineKeyboardButton(text="← Назад", callback_data="go_backward_searched"),
     InlineKeyboardButton(text="Далее →", callback_data="go_forward_searched")],
    [InlineKeyboardButton(text="В меню 📌", callback_data="back_to_menu")]
])


async def notes_builder(listOfArticles, page=0, maxOnPage=5):

    keyboard = InlineKeyboardBuilder()
    start = page * maxOnPage
    end = (page + 1) * maxOnPage
    for i, article in enumerate(listOfArticles[start:end]):
        newOne = f"{(i+1)+page*maxOnPage}. {article.replace('*','')}"
        if len(newOne) > 30:
            newOne = newOne[:30] + "..."

        keyboard.add(InlineKeyboardButton(text=newOne, callback_data="notes_article_" + article))

    navi_buttons = []
    if page > 0:
        navi_buttons.append(InlineKeyboardButton(text="Назад", callback_data="notes_backward"))
    if end < len(listOfArticles):
        navi_buttons.append(InlineKeyboardButton(text="Далее", callback_data="notes_forward"))

    if navi_buttons:
        keyboard.row(*navi_buttons)

    keyboard.add(InlineKeyboardButton(text="Добавить заметку", callback_data="add_note"))
    keyboard.add(InlineKeyboardButton(text="В меню 📌", callback_data="back_to_menu"))

    return keyboard.adjust(1).as_markup()

keyboard_back_from_add_note = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Удалить", callback_data="delete_note")],
    [InlineKeyboardButton(text="Назад", callback_data="menu_notes")]
])

keyboard_back_from_add_note_sec = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="menu_notes")]
])

keyboard_add_or_no_not = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить', callback_data="add_note_bd"), InlineKeyboardButton(text='Отмена', callback_data="menu_notes")]
])

keyboard_to_start_review = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Заполнить', callback_data='start_review'), InlineKeyboardButton(text='Отмена', callback_data="close_call_toMenu")]
])
async def keyboard_categories(listOfCat: list):
    categories_keyboard = InlineKeyboardBuilder()
    correct = SPECIFIC_CYMBALS['correct']
    for category in START_CATEGORIES:
        nameCat = category.split(" ")[0]
        if nameCat in listOfCat:
            s = correct + " "
        else:
            s = ''
        categories_keyboard.add(InlineKeyboardButton(text=s + category, callback_data="category_" + nameCat))
    categories_keyboard.add(InlineKeyboardButton(text='Подтвердить', callback_data="confirm_cat"))
    return categories_keyboard.adjust(3).as_markup()


main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Читать новости 📰")],
    [KeyboardButton(text="Поиск по ключу 🔍")],
    [KeyboardButton(text="Заметки ✒️")],
    [KeyboardButton(text="Профиль 🙃")]
], resize_keyboard=True)

keyboard_result = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть 👀", callback_data="get_result")],
    [InlineKeyboardButton(text="В меню 📌", callback_data="back_to_menu")]
])

keyboard_bad_result = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="В меню 📌", callback_data="back_to_menu")],
])
