from aiogram.fsm.state import State, StatesGroup

class Review(StatesGroup):
    pluses = State()
    minuses = State()

class Register(StatesGroup):
    name = State()
    categories = State()


class News(StatesGroup):
    scrollingNews = State()
    page = State()
    listOfNews = State()


class Search(StatesGroup):
    listOfNews = State()
    page = State()
    key = State()


class Notes(StatesGroup):
    page = State()
    article = State()
    content = State()
