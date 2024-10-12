# Импортируем Selenium для парсинга файлов
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Импортируем Pandas для обработки входных данных и формирования результата
import pandas as pd

# Дополнительные модули
import random


def query_to_url(query: str, user_agent: str, all: bool = False):
    """
    Функция принимает поисковый запрос (название товара) и
    возвращает сслыку или список ссылкок на найденные товары.

    :param query: Поисковый запрос
    :param user_agent: User-agent с которым происходит запрос
    :param all: Если all = True, возращает все полученные ссылки.
    """

    url = f"https://market.yandex.ru/search?text={query}"

    # Конструирование профиля для уменьшения вероятности блока
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", user_agent)

    options = webdriver.FirefoxOptions()
    options.profile = profile
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Окончание настройки драйвера

    driver = webdriver.Firefox(options)
    driver.get(url)
    try:
        products = WebDriverWait(driver, random.randint(3, 5)).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[class='EQlfk Gqfzd']"))
        )
        return [product.get_attribute('href') for product in products][:1]
    except Exception as err:
        return f"Произошла ошибка - {err}"
    finally:
        driver.quit()


def extract_params(query: str, user_agents: list):
    """
    Функция принимает поисковый запрос (название товара) и
    возвращает возможные характеристики.

    :param query: Поисковый запрос
    :param user_agent: Список доступных User-agent
    """

    user_agent = user_agents[random.randint(0, len(user_agents) - 1)]
    urls = query_to_url(query, user_agent)

    if type(urls) == str:
        print(urls)
        return
    elif len(urls) == 0:
        print("По данному запросу нашлось 0 предметов или возникла непредвиденная ошибка.")
        return

    # Конструирование профиля для уменьшения вероятности блока
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", user_agent)

    options = webdriver.FirefoxOptions()
    options.profile = profile
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Окончание настройки драйвера

    driver = webdriver.Firefox(options)
    for url in urls:
        driver.get(url)
        try:
            parameters = WebDriverWait(driver, random.randint(3, 5)).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='_2ZKgm']"))
            )

            print('|'.join([parameter.find_element(By.TAG_NAME, 'span').text for parameter in parameters]))
            return '|'.join([parameter.find_element(By.TAG_NAME, 'span').text.lower().rstrip().lstrip() for parameter in parameters])
        except Exception as err:
            return f"Ошибка обработки - {err}"
        finally:
            driver.quit()



if __name__=="__main__":

    # Подготавливаем user-agents, чтобы снизить вероятность блока
    with open("user-agents.txt", 'r') as file:
        user_agents = file.read().split("\n")


    df = pd.read_csv("itog_data_from_pars.csv")
    new_column = []

    for name in df["Наименование"].tolist():
        new_column.append(extract_params(query=name, user_agents=user_agents))
    
    df.loc[:, 'Параметры'] = new_column
    print(df)
    df.to_csv("new.csv", index=False)
