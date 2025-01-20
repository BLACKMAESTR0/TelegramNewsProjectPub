from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import asyncio
import time


async def get_data():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.rbc.ru/")
    print("[rbc]: Connected")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".main__feed a.main__feed__link"))
        )
    except:
        print(f"[rbc]: Error waiting for elements")

    block = driver.find_elements(By.CSS_SELECTOR, ".main__feed a.main__feed__link")

    news_data = []
    for element in tqdm(block, "[rbc]: links_loading"):
        title = element.find_element(By.CSS_SELECTOR, ".main__feed__title").text  # Извлечение названия
        link = element.get_attribute("href")  # Извлечение ссылки
        news_data.append({"title": title, "link": link})

    data = []
    for i in tqdm(range(len(news_data)), "[rbc]: news_loading"):
        curr_link = news_data[i]["link"]
        driver.get(curr_link)
        try:
            linkPath = driver.find_element(By.CSS_SELECTOR, "picture img")
            linkToImg = linkPath.get_attribute("src")
            allTxt = driver.find_element(By.CLASS_NAME, "article__text.article__text_free").text
            data.append({"title": news_data[i]['title'], "desc": allTxt, "source": "rbc", "linkToImg": None})
        except:
            print("[rbc]: data doesn't found")

    # Закрытие браузера
    driver.quit()
    return data
