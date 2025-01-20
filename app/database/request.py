from app.database.models import async_session
from app.database.models import User, rawNews, News, Note, Review
from app.parse import dzen, rbc
from sqlalchemy import select
from config import NOTES_SEP

from sqlalchemy import desc, or_
from datetime import datetime
from tqdm import tqdm
import app.llm_preprocessing.processing as llm
import pymorphy2



async def del_note(tg_id, article):
    async with async_session() as session:
        noteCheck = await session.scalar(select(Note).where(Note.tg_id == tg_id))
        articles = noteCheck.article.split(NOTES_SEP)
        notes = noteCheck.content.split(NOTES_SEP)
        for i, x in enumerate(articles):
            if f"{x}" == article:
                ind = i
        articles.pop(ind)
        notes.pop(ind)
        noteCheck.article = NOTES_SEP.join(articles)
        noteCheck.content = NOTES_SEP.join(notes)
        session.add(noteCheck)
        await session.commit()

async def add_note(tg_id, article, note):
    async with async_session() as session:
        note_all_info = await session.scalar(select(Note).where(Note.tg_id == tg_id))

        if note_all_info.article:
            notes_sep_articles = note_all_info.article.split(NOTES_SEP)
        else:
            notes_sep_articles = []

        if note_all_info.content:
            notes_sep_content = note_all_info.content.split(NOTES_SEP)
        else:
            notes_sep_content = []

        if article in notes_sep_articles:
            c = 1
            newArticle = f"{article} ({c})"
            while newArticle in notes_sep_articles:
                c += 1
                newArticle = f"{article} ({c})"
            article = newArticle
        notes_sep_articles.append(article)
        notes_sep_content.append(note)
        note_all_info.article = NOTES_SEP.join(notes_sep_articles)
        note_all_info.content = NOTES_SEP.join(notes_sep_content)
        session.add(note_all_info)
        await session.commit()

async def get_inactives(date):
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.active < date))
    return users

async def set_active(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.active = datetime.now()
        session.add(user)
        await session.commit()


async def note_menu(tg_id):
    async with async_session() as session:
        noteCheck = await session.scalar(select(Note).where(Note.tg_id == tg_id))
        if not noteCheck:
            note = Note(tg_id=tg_id)
            session.add(note)
            await session.commit()
            return None
    return noteCheck.article

async def get_note_by_article(tg_id, article):
    async with async_session() as session:
        noteCheck = await session.scalar(select(Note).where(Note.tg_id == tg_id))
        articles = noteCheck.article.split(NOTES_SEP)
        notes = noteCheck.content.split(NOTES_SEP)
        for i, x in enumerate(articles):
            if f"notes_article_{x}" == article:
                return article, notes[i]

async def get_all_word_forms(morph, word):
    parsed = morph.parse(word)[0]
    forms = {parsed.normal_form}

    for lexeme in parsed.lexeme:
        forms.add(lexeme.word)

    return forms


async def search_data(word):
    morph = pymorphy2.MorphAnalyzer()
    word_forms = await get_all_word_forms(morph, word)

    async with async_session() as session:
        conditions = [News.text.ilike(f"%{form}%") for form in word_forms]
        news = (
            select(News).
            filter(
                or_(*conditions)
            ).
            order_by(desc(News.collected_at)).
            limit(50)
        )

        result = await session.scalars(news)
        data = []
        for item in result:
            data.append({"data": {"article": item.article, "text": item.text, "linkToImg": item.linkToImg}})
    return data


async def like_news(tg_id, page, listOfNews):
    START_CATEGORIES = ["политика", "экономика", "спорт", "технологии", "наука", "культура",
                        "здоровье", "образование", "развлечения", "путешествия", "автомобили",
                        "мода", "погода", "происшествия", "экология"]
    article = listOfNews[page]['data']['article']
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        news = await session.scalar(select(News).where(News.article == article))
        users_cat = user.best_cat
        news_cat = news.cat
        listOfCat = []

        for cat in START_CATEGORIES:
            if cat in users_cat or cat in news_cat:
                listOfCat.append(cat)
        user.best_cat = ";".join(listOfCat)
        await session.commit()


async def sortNewsPersonal(news, categories):
    data = []
    if categories:
        categories = categories.split(";")
    else:
        categories = []
    for item in news:
        try:
            markAll = int(item.mark)
        except:
            markAll = 0
            print("Something wrong with mark")
        for cat in categories:
            if cat in item.cat:
                markAll += 4
        data.append({"data": {"article": item.article, "text": item.text, "linkToImg": item.linkToImg}, "mark": markAll,
                     "collected_at": datetime.strptime(item.collected_at, "%Y-%m-%d %H:%M:%S")})
    return sorted(data, key=lambda x: (x["mark"], x["collected_at"]), reverse=True)


async def get_list_of_news(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        news = list(await session.scalars(select(News)))
        categories = user.best_cat
        data = await sortNewsPersonal(news, categories)
    return data


async def get_data_toReview(date):
    async with async_session() as session:
        reviewCheck = await session.scalars(select(Review).where(Review.collected_at < date))
        if reviewCheck:
            return reviewCheck
        else:
            return []

async def set_update_data_toReview(tg_id):
    async with async_session() as session:
        reviewCheck = await session.scalar(select(Review).where(Review.tg_id == tg_id))
        reviewCheck.collected_at = datetime.now()
        await session.commit()

async def set_info(tg_id, name=None, categories=None) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if tg_id and (not (name and categories)):
            user = User(tg_id=tg_id)
            session.add(user)
        else:
            Str_categories = ";".join(categories)
            if user:
                user.best_cat = Str_categories.lower()
                user.name = name
            else:
                user = User(tg_id=tg_id, name=name, best_cat=Str_categories.lower())
                session.add(user)
        reviewCheck = await session.scalar(select(Review).where(Review.tg_id == tg_id))
        if not reviewCheck:
            review = Review(tg_id=tg_id, collected_at=datetime.now())
            session.add(review)
        await session.commit()


async def parse_news():
    async with async_session() as session:
        dzen_data = await dzen.get_data()
        rbc_data = await rbc.get_data()
        data = rbc_data + dzen_data
        for item in tqdm(data, desc="[rawnews/news]: filling dataBase"):
            try:
                title = item.get("title")
                text = item.get("desc")
                source = item["source"]
                linkToImg = item["linkToImg"]

                if not title or not text:
                    continue

                existing_news = await session.scalar(select(rawNews).where(rawNews.article == title))
                if existing_news:
                    continue

                news = rawNews(article=title,
                               text=text,
                               collected_at=str(datetime.now()).split(".")[0])
                processedNews = News(article=title,
                                     collected_at=str(datetime.now()).split(".")[0],
                                     source=source,
                                     linkToImg=linkToImg
                                     )
                session.add(processedNews)
                session.add(news)
            except Exception as e:
                print(e)
        await session.commit()


async def get_index_point(text, zone):
    for i in range(zone, 0, -1):
        if text[i] == ".":
            return i
    return zone


async def process_news():
    async with async_session() as session:
        dataNews = list(await session.scalars(select(News).where(News.mark == None)))

        listOfArticles = []
        for item in dataNews:
            newsText = await session.scalar(select(rawNews).where(rawNews.article == item.article))
            listOfArticles.append({"article": item.article, "text": newsText.text})
        batch_size = 10
        if len(listOfArticles) > batch_size:
            batchReFill = True
        else:
            batchReFill = False

        if batchReFill:
            marks = []
            summary = []
            cats = []
            for i in tqdm(range(len(listOfArticles) // batch_size + 1), desc="[processingNews]:"):
                start = i * batch_size
                end = (i + 1) * batch_size
                if end > len(listOfArticles):
                    currentBatch = listOfArticles[start:len(listOfArticles)]
                else:
                    currentBatch = listOfArticles[start:end]
                summary += await llm.get_summary(currentBatch)
                cats += await llm.get_cats(currentBatch)
                currentMarks = await llm.get_marks(currentBatch)
                currentMarks = currentMarks.split("\n")
                if len(currentMarks) != batch_size:
                    marks += ['1.5' for _ in range(batch_size)]
                else:
                    marks += currentMarks
        else:
            summary = await llm.get_summary(listOfArticles)
            cats = await llm.get_cats(listOfArticles)
            currentMarks = await llm.get_marks(listOfArticles)
            marks = currentMarks.split("\n")
            if len(marks) != len(summary):
                marks = ["1.5" for _ in summary]

        for i, item in enumerate(dataNews):
            item.mark = marks[i].split(".")[1].lower()
            newText = summary[i].lower()
            if len(newText) > 900:
                ind = await get_index_point(newText, 900)
                item.text = newText[:ind + 1]
            else:
                item.text = summary[i].lower()
            item.cat = cats[i].lower()
            await session.commit()
        print("\n[processingNews]: Finished")
        await session.commit()

async def set_review(tg_id, pluses, minuses):
    async with async_session() as session:
        message = f"Плюсы: {pluses}\nНедостатки: {minuses}"
        review = await session.scalar(select(Review).where(User.tg_id == tg_id))
        review.content = message
        session.add(review)
        await session.commit()

async def get_profile(tg_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_profile(tg_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

