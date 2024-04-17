import time
import json
import sys
from datetime import datetime
from argparse import ArgumentParser

# import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup as Soup


def fetch_answers(my_url):
    req = requests.get(my_url)

    page_soup = Soup(req.content, "html.parser")
    main_box = page_soup.findAll("script", {"type": "application/ld+json"})[0].text

    data = json.loads(main_box)
    answers = []
    try:
        answers += [x["text"] for x in data["mainEntity"]["acceptedAnswer"]]
    except:
        pass
    answers += [x["text"] for x in data["mainEntity"]["suggestedAnswer"]]
    for i in range(len(answers)):
        print(f"\n\n\n\n Answers #{i+1}\n\n")
        print(answers[i])
    try:
        if "-txt" in sys.argv:
            with open(
                rf"answers\{datetime.now().strftime('%H%M_%Y%m%d')}.txt",
                "a+",
                newline="",
                encoding="UTF-8",
            ) as f:
                for answer in answers:
                    f.write(answer)
                    f.write("\n\n\n\n\n\n")

        if "-json" in sys.argv:
            with open(
                rf"answers\{datetime.now().strftime('%H%M_%Y%m%d')}.json",
                "a+",
                newline="",
                encoding="UTF-8",
            ) as f:
                answers_json = {i + 1: answers[i] for i in range(len(answers))}
                json.dump(answers_json, f)
    except IOError:
        print("IO Error")



def args():
    args = ArgumentParser()
    args.add_argument('-l', '--mail', required=True, help='Email for Quora')
    args.add_argument('-g', '--password', required=True, help='password for Quora')
    args.add_argument('-b', '--disease', required=True, help='disease name for the search')
    args.add_argument('-p', '--path', type=str, help='chromium-chromedriver path')


    return args.parse_args()

if __name__ == '__main__':
    arguments = args()

    try:

        options = webdriver.ChromeOptions()
        options.add_argument('--disable-dev-shm-usage')
        #options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')

        # Initializing webdriver for Chrome with our options
        driver = webdriver.Chrome(service=Service(arguments.path), options=options)
        driver.get('https://www.quora.com/')

        # Typing email/password
        driver.find_element(By.XPATH, '// *[ @ id = "email"]').send_keys(arguments.mail)
        driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(arguments.password)
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[4]/button').click()
        time.sleep(5)


        # Typing disease
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/form/div/div/div/div/div/input').send_keys(arguments.disease)
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/form/div/div/div/div/div/input').send_keys(Keys.ENTER)
        time.sleep(8)

        # Printing data
        # data = driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div[1]/span/a/div/div/div/div/span/span[1]').text
        # base = driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div/div[2]/div[1]/span/a/div/div/div/div/span/span[2]').text

        # Extracting URLs
        urls = []
        i = '1'
        for x in range(1, 6):
            temp = driver.find_element(By.XPATH, f'//*[@id="mainContent"]/div/div/div[2]/div[{i}]/span/a').get_attribute("href")
            urls.append(temp)
            i = str(int(i) + 1)

        # Fetching answers for each URL
        for url in urls:
            print(f"\n\nFetching answers for URL: {url}\n")
            fetch_answers(url)

    finally:
        # Closing the browser session
        driver.quit()
