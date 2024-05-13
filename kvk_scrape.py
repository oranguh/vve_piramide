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


# API possible but costs money https://developers.kvk.nl/nl/apply-for-apis?step=api-overview
# data from kvk https://www.kvk.nl/zoeken/


def main():
    kvk_page = "https://www.kvk.nl/zoeken/"


    appartments_df = pd.read_csv("datasets/appartementen_df_complete.csv")
    kvk_dict = {}



    chromedriver_autoinstaller.install()

    # Use appropriate driver for your browser (Chrome, Firefox, etc.)
    driver = webdriver.Chrome()  # or webdriver.Firefox() depending on your browser

    driver.get(kvk_page)

    # Find login form elements and submit
    wait = WebDriverWait(driver, 10)  # Adjust the wait time as needed

    privacy_button = '//*[@id="cookie-consent"]/div/button'
    privacy_button = wait.until(EC.element_to_be_clickable((By.XPATH, privacy_button)))

    privacy_button.click()


    search_field_ = "/html/body/div/div/div/main/section/div[2]/div/div/section/div/div[1]/div[1]/div/div[1]/div/div[2]/input"
    search_field = wait.until(EC.presence_of_element_located((By.XPATH, search_field_))) 
    search_button_ = "/html/body/div/div/div/main/section/div[2]/div/div/section/div/div[1]/div[1]/div/div[2]/button"
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, search_button_)))
    time.sleep(3)

    for idx, appartement in appartments_df.iterrows():
        # straat	huisnummer	huisletter	postcode    plaats
        if pd.isnull(appartement['huisletter']):
            huisletter = ""
        else:
            huisletter = appartement['huisletter']

        postcode = appartement['postcode'].replace(" ", "")
        plaats = "Amsterdam"

        search_string = f"{appartement['straat']} {appartement['huisnummer']}, {huisletter} {postcode} {plaats}"
        # search_string = "Tidorestraat 94,  1095HM Amsterdam"
        search_field.send_keys(search_string)
        search_button.click()
        time.sleep(1)
        results_xpath = "/html/body/div/div/div/main/section/div[2]/div/div/section/div/div[1]/div[4]/ul"

        try:
            results = driver.find_element(By.XPATH, results_xpath)
        except NoSuchElementException:
            search_field.clear()
            time.sleep(1)
            continue

        results.text.split("Bestel nu")

        
        time.sleep(1)
        search_field.clear()

        text_split = results.text.split("Bestel nu")
        kvk_numbers = []
        kvk_names = []
        print(appartement["Appartement"])
        for i in text_split[:-1]:
            splits = i.split("\n")
            splits = [x for x in splits if x != ""]
            print(splits)

            if splits[3] in ["Vereniging", "Stichting"]:
                entry_dict = {
                    "name": splits[0],
                    "description": splits[1],
                    "KVK number": splits[2].split(": ")[1],
                    "business type": splits[3],
                    "Hoofdvestiging": "",
                    "Vestigingsnummer": "",
                    "Rechtspersoon": splits[4],
                    "Adres": splits[5],
                    "Handelsnaam": splits[6].split(":")[1],
                }
            else:
                entry_dict = {
                    "name": splits[0],
                    "description": splits[1],
                    "KVK number": splits[2].split(": ")[1],
                    "business type": splits[3],
                    "Hoofdvestiging": splits[4],
                    "Vestigingsnummer": splits[5].split(": ")[1],
                    "Rechtspersoon": "",
                    "Adres": splits[6],
                    "Handelsnaam": splits[7].split(":")[1],
                }

            kvk_dict[splits[2]] = entry_dict
            kvk_numbers.append(splits[2])
            kvk_names.append(splits[0])
            print(entry_dict)

        appartments_df.at[idx, "kvk_numbers"] = json.dumps(kvk_numbers)
        appartments_df.at[idx, "kvk_names"] = json.dumps(kvk_names)
        

    
    kvk_df = pd.DataFrame(kvk_dict).T
    appartments_kvk_df = appartments_df[["Appartement", "Appartementsindex", "Eigenaar", "kvk_numbers", "kvk_names"]]

    appartments_kvk_df.to_csv("datasets/appartementen_kvk.csv")
    appartments_kvk_df.to_excel("datasets/appartementen_kvk.xlsx")
    kvk_df.to_csv("datasets/kvk_register_pyramide.csv")
    kvk_df.to_excel("datasets/kvk_register_pyramide.xlsx")

    driver.quit()




if __name__ == '__main__':

    main()