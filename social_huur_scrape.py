import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import numpy as np
import chromedriver_autoinstaller
import json

import time

# https://amsterdam.mijndak.nl/verhuurd
# this site only lets you get data from the past year. So doing it every so often is wise if you want tu to date data.


if False: #make the dataset. Manually setting dates required.
    kvk_page = "https://amsterdam.mijndak.nl/verhuurd"


    appartments_df = pd.read_csv("appartementen_df_complete.csv")
    kvk_dict = {}



    chromedriver_autoinstaller.install()

    # Use appropriate driver for your browser (Chrome, Firefox, etc.)
    driver = webdriver.Chrome()  # or webdriver.Firefox() depending on your browser

    driver.get(kvk_page)

    # Find login form elements and submit
    wait = WebDriverWait(driver, 10)  # Adjust the wait time as needed

    privacy_button = '//*[@id="cookiescript_accept"]'
    privacy_button = wait.until(EC.element_to_be_clickable((By.XPATH, privacy_button)))

    privacy_button.click()


    time.sleep(30)

    table_path = "/html/body/div[1]/div/div/div/div/div[1]/div/div/div/div[3]/div[2]/div[2]/div/div/table"
    table = wait.until(EC.presence_of_element_located((By.XPATH, table_path)))

    table_html = table.get_attribute('outerHTML')
    df = pd.read_html(table_html)[0]

    today = time.strftime("%Y%m%d")
    df.to_csv("datasets/mijndak_verhuurd_{today}.csv", index=False)
    # df.to_excel("datasets/mijndak_verhuurd_{today}.xlsx", index=False)

    print(df)



# analysis
if True:
    # enter dataset with date here
    df = pd.read_csv("datasets/mijndak_verhuurd.csv")
    df["kamers"] = df["Woning"].apply(lambda x: int(x.split(" ")[-2]))
    df["Voorrang"] = df["Verantwoording"].apply(lambda x: "Voorrang" if "Voorrang" in x else "directe bemiddeling" if "directe bemiddeling" in x else "Loting" if "Loting" in x else "Normaal")

    print(df.columns)
    df = df.loc[df["Woonplaats"] == "Amsterdam"]

    print(df["Publicatiemodel"].value_counts().to_frame())
    print(df["Voorrang"].value_counts().to_frame())

    # print(df["Woonplaats"].value_counts().to_frame())
    print(df["Woning"].value_counts().to_frame())
    print(df["kamers"].value_counts().to_frame())

