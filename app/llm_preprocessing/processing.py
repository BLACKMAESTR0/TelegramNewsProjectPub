import json
import os

import requests
from gigachat import GigaChat, exceptions
from random import randint
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

auth_key = os.getenv("AUTHORIZATIONKEY")
url = os.getenv("GIGAAPI")
def refreshable(func):
    async def wrapper(self, *args):
        try:
            return await func(self, *args)
        except exceptions.AuthenticationError as e:
            if e.args[1] == 401:
                await self.refresh_token()
                return await func(self, *args)

    return wrapper


payload = {
    'scope': 'GIGACHAT_API_PERS'
}


class AI_Engine:
    access_token = None

    def get_headers(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': "f33f5540-f387-42f6-b40d-bec49f575a62",
            'Authorization': f'Basic {auth_key}'
        }

    async def refresh_token(self):
        print('refresh token')
        response = json.loads(
            requests.request("POST", url, headers=self.get_headers(), data=payload, verify=False).text)
        self.access_token = response['access_token']

    async def init(self):
        await self.refresh_token()

    @refreshable
    async def paraphrase_event_desc_marks(self, text_to_paraphrase):
        with GigaChat(access_token=self.access_token, verify_ssl_certs=False, model='GigaChat') as giga:
            response = giga.chat(f"Экзамен по обществознанию. Твоя задача дать баллы от 1 до 9 по важности новости в "
                                 f"газете гос-ства Y. ФОРМАТ ОТВЕТА. НИКАКОГО ТЕКСТА В ОТВЕТЕ: Номер новости.Балл\nНомер новости.Балл\nНомер новости.Балл: {text_to_paraphrase}")
            return response.choices[0].message.content

    @refreshable
    async def paraphrase_event_desc_summaries(self, text_to_paraphrase):
        with GigaChat(access_token=self.access_token, verify_ssl_certs=False, model='GigaChat') as giga:
            response = giga.chat(f"Суммаризируй до 400 символов МАКСИМУМ, сохрани все микротемы: {text_to_paraphrase}")
            return response.choices[0].message.content

    @refreshable
    async def paraphrase_event_desc_cat(self, text_to_paraphrase):
        with GigaChat(access_token=self.access_token, verify_ssl_certs=False, model='GigaChat') as giga:
            response = giga.chat(
                f"Я даю тебе название новости, тебе нужно выделить 1 или несколько категорий из списка. ТОЛЬКО ИЗ "
                f"СПИСКА ДАЛЕЕ. ПЕРЕФРАЗИРОВАТЬ НЕЛЬЗЯ."
                f"'Политика ️Экономика Спорт Технологии Наука Культура Здоровье Образование Развлечения Путешествия ️Автомобили"
                f"Мода Погода Происшествия Экология'"
                f"ФОРМАТ ОТВЕТА ТОЛЬКО КАТЕГОРИИ. НИКАКОГО БОЛЕЕ ТЕКСТА В ОТВЕТЕ: категория1;категория2...{text_to_paraphrase}")
            return response.choices[0].message.content


ai_instance = AI_Engine()

stopResults = ["Что-то в вашем вопросе меня смущает. Может, поговорим на другую тему?",
               "Не люблю менять тему разговора, но вот сейчас тот самый случай.",
               "Как у нейросетевой языковой модели у меня не может быть настроения, но почему-то я совсем не хочу говорить на эту тему."]

async def get_cats(listOfArticles):
    cats = []
    for i in tqdm(range(len(listOfArticles)), desc="[processing]: getting cat.s"):
        print(f"[processing]: Start of marking {len(listOfArticles)} news.")
        result = await ai_instance.paraphrase_event_desc_cat(listOfArticles[i]['article'])
        if result in stopResults:
            cats.append('Политика')
        else:
            cats.append(result)
    return cats

async def get_marks(listOfArticles):
    s = ''
    for i, x in enumerate(listOfArticles):
        s += f"{i + 1}. {listOfArticles[i]['article']}"

    print(f"[processing]: Start of marking {len(listOfArticles)} news.")
    result = await ai_instance.paraphrase_event_desc_marks(s)
    if result in stopResults:
        s = ''
        for i, x in enumerate(listOfArticles):
            if i == len(listOfArticles) - 1:
                s += f"{i + 1}.{randint(1, 10)}"
            else:
                s += f"{i + 1}.{randint(1, 10)}\n"
        return s
    else:
        print(f"[processing]: End of marking {len(listOfArticles)} news.")
        return result


async def get_summary(listOfNews):
    summaries = []
    for i in tqdm(range(len(listOfNews)), desc="[processing]: getting summaries"):
        text = listOfNews[i]['text']
        result = await ai_instance.paraphrase_event_desc_summaries(text)
        if result in stopResults:
            result = listOfNews[i]['text'].split("\n")
            if len(result) == 1:
                summaries.append(listOfNews[i]['text'])
            else:
                summaries.append("\n".join(result[:-1]))
        else:
            summaries.append(result)
    return summaries