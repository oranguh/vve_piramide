import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import os

import chromedriver_autoinstaller

import time

def main():
    # scrape_energielabel()
    parse_energietext()


def scrape_energielabel():
    # load data to input energielabel

    if os.path.exists("datasets/appartementen_df_energielabel.xlsx"):
        df = pd.read_excel("datasets/appartementen_df_energielabel.xlsx", index_col=0)
        df_ = df[df["energielabel_text"].isna()].copy()
    else:
        df = pd.read_excel("datasets/appartementen_df.xlsx", index_col=0)
        df["energielabel_text"] = ""
        df_ = df.copy()
    energielabel_url = 'https://www.energielabel.nl/woningen/zoek-je-energielabel/'

    chromedriver_autoinstaller.install()

    # Use appropriate driver for your browser (Chrome, Firefox, etc.)
    driver = webdriver.Chrome()  # or webdriver.Firefox() depending on your browser

    driver.get(energielabel_url)

    wait = WebDriverWait(driver, 10)  # Adjust the wait time as needed
    
    
    
    residence_dropdown = wait.until(EC.presence_of_element_located((By.ID, 'residence_type')))
    # all residences can be found using huurwoning option
    # Using the Select class to interact with the dropdown
    select = Select(residence_dropdown)
    select.select_by_visible_text("Huurwoning")

    # Find login form elements and submit
    time.sleep(2)
    for index, row in df_.iterrows():
        print(index)
        # Fill in the login form
        postcode_field = wait.until(EC.presence_of_element_located((By.ID, 'postcode')))
        huisnummer_field = wait.until(EC.presence_of_element_located((By.ID, 'house_nr')))
        huisletter_dropdown = wait.until(EC.presence_of_element_located((By.ID, 'house_nr_addition')))
        #clear previous input
        postcode_field.clear()
        postcode_field.send_keys(row["postcode"])
        huisnummer_field.clear()
        huisnummer_field.send_keys(row["huisnummer"])

        if pd.notna(row["huisletter"]):
            time.sleep(5)
            select = Select(huisletter_dropdown)
            select.select_by_visible_text(row["huisletter"])
        
        submit_xml = "/html/body/main/div/div[2]/div/div[2]/div/div[1]/div[2]/form/fieldset/div/button/span"
        time.sleep(5)
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, submit_xml)))
        submit_button.click()
        time.sleep(4)
        text_field = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/p")))
        text_field = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-label__result-text")))
        df.at[index, "energielabel_text"] = text_field.text
        df.to_excel("appartementen_df_energielabel.xlsx")


def parse_energietext():
    df = pd.read_excel("datasets/appartementen_df_energielabel.xlsx", index_col=0)

    df["energielabel"] = df["energielabel_text"].str.extract(r"energielabel\s(\w)")
    df["WWS"] = df["energielabel_text"].str.extract(r"WWS\s(\d\.\d+)").astype(float)
    df["energie_geldig_tot"] = df["energielabel_text"].str.extract(r"geldig\stot\s(\d\d-\d\d-\d\d\d\d)")
    # df.drop(columns=["energielabel_text"], inplace=True)
    df.to_excel("datasets/appartementen_df_energielabel.xlsx")
    df.to_csv("datasets/appartementen_df_energielabel.csv")   
    
    print(df["energielabel"].value_counts(dropna=False).to_frame().sort_index())
    print(df["WWS"].value_counts(dropna=False, bins=8).to_frame())
    
    df["test"] = df["bijdrage_algnw_2023"] / df["Breukdeel"]
    for row in df["test"]:
        print(row)
if __name__ == "__main__":
    main()


