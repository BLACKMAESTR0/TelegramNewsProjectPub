from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm


async def scroll_down(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            WebDriverWait(driver, 3).until(
                lambda d: d.execute_script("return document.body.scrollHeight") > last_height
            )
        except:
            print(f"[dzen.Scroll]: No new content loaded")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


async def get_data():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get("https://dzen.ru/news")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.news-top-stories__other a'))
        )
    except:
        print(f"[dzen]: Error waiting for elements")

    await scroll_down(driver)

    data = []
    new_links = []

    news = driver.find_elements(By.CSS_SELECTOR, '.news-top-stories__other a')
    for oneNews in tqdm(news, desc="[dzen]: links_loading"):
        new_links.append(oneNews.get_attribute("href"))

    for link in tqdm(new_links, desc="[dzen]: news_loading"):
        try:
            driver.get(link)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "news-site--Story-desktop__digest-1o"))
            )
            linkForImg = driver.find_element(By.CSS_SELECTOR, "img.neo-image.neo-image_loaded")
            link = linkForImg.get_attribute("src")
            textAll = driver.find_element(By.CLASS_NAME, "news-site--Story-desktop__digest-1o").text
            article = driver.find_element(By.CLASS_NAME,
                                          "news-site--StoryHead-desktop__title-1t").text
            data.append({"title": article, "desc": textAll, "source": "dzen", "linkToImg": link})
        except:
            print(f"[dzen]: Error loading text")
    driver.quit()
    return data