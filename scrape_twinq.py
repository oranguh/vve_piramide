import os
import io 
import shutil
import time
import ast    
import platform

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller

from general_data import MOLUKKEN_GEBOUW, SUMATRAPLANTSOEN_GEBOUW, DAKAANBOUW, PORTIEKEN
from keys_and_passwords import username_twinq, password_twinq

def main():
    login_url = 'https://ymere.twinq.nl/apex/f?p=TPL:LOGIN_DESKTOP:::::TPL_APP:EPL'
    # login_url = 'YOUR_LOGIN_URL'

    chromedriver_autoinstaller.install()

    # Use appropriate driver for your browser (Chrome, Firefox, etc.)
    if True:
        driver = webdriver.Chrome()  # or webdriver.Firefox() depending on your browser
    else:
        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(options=options)

    driver.get(login_url)
    # Find login form elements and submit
    wait = WebDriverWait(driver, 15)  # Adjust the wait time as needed

    username_field = wait.until(EC.presence_of_element_located((By.ID, 'P101_USERNAME'))) 
    password_field = wait.until(EC.presence_of_element_located((By.ID, 'P101_PASSWORD'))) 
    submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'B286311067721006444')))

    # Fill in the login form
    username_field.send_keys(username_twinq)
    password_field.send_keys(password_twinq)

    # Submit the form
    submit_button.click()

    # Now you are logged in and can proceed with scraping data from subsequent pages.
    # Follow the previous scraping steps after this point using Selenium.

    # make the datasets which for all invoices which have been paid
    financien_Grootboekrekeningen_KleinOnderhoud(driver, wait) # will give error if the latest year is still empty
    parse_kleinonderhoud_facturen_link()
    
    
    # # make dataset for all the repair requests, some of which will be performed and have a corresponding invoice
    gebouwBeheer_reparatieverzoek_alle(driver, wait)
    parse_reparatieverzoek_link()

    driver.quit()

    merge_facturen_en_verzoeken()
    



def financien_Grootboekrekeningen_KleinOnderhoud(driver, wait):
    # Assuming you've located the element that triggers the appearance of the link on hover
    hover_element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Financiën')))

    # Hover over the element
    actions = ActionChains(driver)
    actions.move_to_element(hover_element).perform()

    link_to_grootboek = wait.until(EC.presence_of_element_located((By.LINK_TEXT , "Grootboekrekeningen")))
    # Extract the href attribute
    grootbook_link = link_to_grootboek.get_attribute("href")

    jaren = [f"jul-{i} - jun-{i+1}" for i in range(2016, 2024)]
    # jaren = ["jul-2018 - jun-2019", "jul-2023 - jun-2024"]
    # NOTE important to set dates! NOTE
    jaren = [f"jul-{i} - jun-{i+1}" for i in range(2022, 2024)]


    df_klein_onderhoud_totaal = pd.DataFrame() #make from scratch each time

    for jaar in jaren:
        print("JAAR: ", jaar)
        # Navigate to the grootboekrekeningen page
        if grootbook_link:
            driver.get(grootbook_link)
            # Now you've navigated to the link specified in the href attribute
        else:
            print(f"The href {grootbook_link} attribute is not available for the element.")

        wait = WebDriverWait(driver, 10)  # Adjust the wait time as needed

        jaar_dropdown_id = "P1420_BKJR_NR" #I guess this script is not very robust to changes in the website

        # click on dropdown for specified year
        dropdown = wait.until(EC.presence_of_element_located((By.ID , jaar_dropdown_id)))

        # Using the Select class to interact with the dropdown
        select = Select(dropdown)

        # Select a specific dropdown item by its value attribute
        # jaar = "jul-2016 - jun-2017"
        # jaar = "jul-2023 - jun-2024"
        select.select_by_visible_text(jaar)

        # go to relevant detail finances page
        detailed_page_name = "Dagelijks onderhoud - Klein onderhoud"
        # NOTE need to scroll down to find the link now...

        element = wait.until(EC.presence_of_element_located((By.XPATH, '//tr[@data-rownum=1]')))
    
        # click the element
        actions.click(element).perform()
        # actions.send_keys(Keys.PAGE_DOWN).perform()

        for j in range(5):
            print(f"scrolling: {j}")
            for i in range(40):
                actions.key_down(Keys.ARROW_DOWN).perform()
            time.sleep(5)

        link_to_detailed_page = wait.until(EC.presence_of_element_located((By.LINK_TEXT , detailed_page_name)))
        href_attribute = link_to_detailed_page.get_attribute("href")

        # Navigate to the link
        if href_attribute:
            driver.get(href_attribute)
            # Now you've navigated to the link specified in the href attribute
        else:
            print(f"The href {href_attribute} attribute is not available for the element.")

        download_table_xpath = '//*[@id="R203071684540571539_ig_toolbar_B160248707475608424"]/span[2]'
        download_table_button = wait.until(EC.presence_of_element_located((By.XPATH, download_table_xpath)))

        download_table_button.click()
        time.sleep(3)
        
        if platform.system() == "Windows":
            downloaded_file = "C:/Users/marco/Downloads/grootboekkaart.csv"
        else: 
            downloaded_file = "/Users/mah/Downloads/grootboekkaart.csv" # NOTE this is dangerous. Perhaps there's an alternative
        
        newfile = f"datasets/dagelijks_onderhoud_jaren/VvE_piramide__{detailed_page_name}_{jaar}.csv"
        shutil.move(downloaded_file, newfile)
        time.sleep(1)

        # we need to scroll down the table in order to be able to access all the data
        # scroll down to the bottom of the page

        if False:
            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'a-GV-table')))

            page_source = driver.page_source

            # find the table containing all financial info #NOTE THIS IS INCOMPLETE
            tables = pd.read_html(io.StringIO(page_source), attrs={"class": "a-GV-table"})

            # Access the first DataFrame from the filtered tables list (if found)
            if tables:
                if len(tables) > 1:
                    # If there are multiple tables, you can concatenate them into a single DataFrame    
                    df = pd.concat([tables[0], tables[1]], ignore_index=True)
                else:
                    df = tables[0]
            else:
                print("No table found with the specified class name.")
        df = pd.read_csv(newfile, sep=";", encoding="ISO-8859-1")
        df.set_index("Referentie", inplace=True)
        df["unique_id"] = [f"{jaar}_{i}" for i in range(len(df))]
        df["boekjaar"] = f"{jaar}"
        # loop through the table and click on the link to the detailed page

        # row_1 = f'//*[@id="R203071684540571539_ig_grid_vc"]/div[2]/div[4]/table/tbody/tr[1]'
        for row_index, reference in enumerate(df.index.to_list()):
            # element = wait.until(EC.presence_of_element_located((By.XPATH, row_1)))
            # # Use ActionChains to move the cursor to the element
            # actions = ActionChains(driver)
            # # click the element
            # actions.click(element).perform()
            # for click in range(row_index, row_index+5):
            #     actions.key_down(Keys.ARROW_DOWN).perform()

            # actions.send_keys(Keys.PAGE_DOWN).perform()

            if not reference: # some cells are empty? That seems weird
                continue
            if reference is None:
                continue
            if type(reference) == float: # why is it returning a float? html weird?
                print("ISNA")
                continue

            # use index to find the href link
            print("REFERENTIE", reference)
            reference = reference.strip()
            leverancier = reference.split("(")[0].strip()
            print("LEVERANCIER", leverancier)
            # find button to reference
            link_to_detailed_page = wait.until(EC.presence_of_element_located((By.LINK_TEXT , reference)))
            
            # press button
            link_to_detailed_page.click()

            # time.sleep(5)
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            new_iframe = iframes[-1]  # Assuming the new iframe is the last one in the list
            driver.switch_to.frame(new_iframe)

            dialog_box = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div/div[2]/div/div/div/div[1]/div/div/div[2]/div[2]/div')))
            desc_list = dialog_box.find_element(By.CLASS_NAME, "t-AVPList")


            detailed_list = desc_list.text.split("\n")
            for i in range(0, len(detailed_list), 2):
                if detailed_list[i] not in df.columns:
                    df[detailed_list[i]] = None
                if reference in df.index:
                    df.at[reference, detailed_list[i]] = detailed_list[i+1]
                else:
                    print(f"REFERENCE: {reference} NOT IN INDEX, using index instead")
                    # NOTE, using iat instead of at because the reference in the table does not match the reference in the download? 
                    df[detailed_list[i]].iat[row_index] = detailed_list[i+1]

            # time.sleep(1)
            # switch to default frame
            driver.switch_to.default_content()
                
            # Close the dialog
            close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ui-dialog-titlebar-close')))
            close_button.click()
            time.sleep(1) # wait to click on the next one. Site bugs if you do it too quickly

        df.set_index("unique_id", inplace=True)
        print(df)
        df.to_csv(newfile)
        df_klein_onderhoud_totaal = pd.concat([df_klein_onderhoud_totaal, df])
        
        df_klein_onderhoud_totaal.to_csv(f"datasets/VvE_piramide__{detailed_page_name}.csv")
        time.sleep(2)


def gebouwBeheer_reparatieverzoek_alle(driver, wait):
    # Assuming you've located the element that triggers the appearance of the link on hover
    hover_element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Gebouw beheer')))

    # Hover over the element
    actions = ActionChains(driver)
    actions.move_to_element(hover_element).perform()

    link_to_reparatieverzoek = wait.until(EC.presence_of_element_located((By.LINK_TEXT , "Reparatieverzoeken en opdrachten")))
    # Extract the href attribute
    reparatieverzoek_link = link_to_reparatieverzoek.get_attribute("href")

    # Navigate to the link
    if reparatieverzoek_link:
        driver.get(reparatieverzoek_link)
        # Now you've navigated to the link specified in the href attribute
    else:
        print(f"The href {reparatieverzoek_link} attribute is not available for the element.")

    wait = WebDriverWait(driver, 10)  # Adjust the wait time as needed

    # click on ALLE verzoeklen
    button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="P1140_IND_MIJN_VERZOEKEN"]/div/div/div[2]/label')))
    button.click()

    # wait for the first row in the table to load. Then start scrolling
    element = wait.until(EC.presence_of_element_located((By.XPATH, '//tr[@data-rownum=1]')))
    
    # Use ActionChains to move the cursor to the element
    actions = ActionChains(driver)
    # click the element
    actions.click(element).perform()
    # actions.send_keys(Keys.PAGE_DOWN).perform()

    for j in range(60):
        print(f"scrolling: {j}")
        for i in range(40):
            actions.key_down(Keys.ARROW_DOWN).perform()
        time.sleep(5)

    page_source = driver.page_source
    tables = pd.read_html(io.StringIO(page_source), attrs={"class": "a-GV-table"})
    if tables:
        if len(tables) > 1:
            # If there are multiple tables, you can concatenate them into a single DataFrame    
            df = pd.concat([tables[0], tables[1]], ignore_index=True)
        else:
            df = tables[0]
    else:
        print("No table found with the specified class name.")

    df.to_csv("datasets/VvE_piramide__Alle_Reparatieverzoeken_en_opdrachten.csv") #from scratch
    time.sleep(2)


def parse_reparatieverzoek_link():

    # load the data

    df = pd.read_csv("datasets/VvE_piramide__Alle_Reparatieverzoeken_en_opdrachten.csv")

    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)
    if 'Verzoek Sorted Descending' in df.columns:
        df.rename(columns={'Verzoek Sorted Descending': 'Verzoek'}, inplace=True)
    """ 
    columns:

    'Verzoek', 'Omschrijving',
    'Gemeld door', 'Type', 'Status', 'Datum', 'Opdracht',
    'Appartementsrecht(en)', 'Eigenaar(s)'


    1/04/2024: missing Gemeld door?

    """
    # replace all Appartementsrecht(en) with easier to read address and use ; as separator if multiple

    # print(df["Appartementsrecht(en)"].unique())
    df["appartement_simple"] = df["Appartementsrecht(en)"].copy()
    df["appartement_simple"] = df["appartement_simple"].str.replace(" (Woning met berging en tuin)", ";", regex=False)
    df["appartement_simple"] = df["appartement_simple"].str.replace(" (Woning met berging)", ";", regex=False)
    df["appartement_simple"] = df["appartement_simple"].str.replace(" (Vervallen wegens wijziging akte)", ";", regex=False)
    # df["appartement_simple"] = df["appartement_simple"].str.replace("(", "").str.replace(")", "", regex=False)
    df['appartement_simple_list'] = None
    df["appartement_simple_list"] = df["appartement_simple"].apply(lambda x: [y.strip() for y in x.split(";")[:-1]])

    df["count of apartments in row"] = df["appartement_simple_list"].apply(lambda x: len(x))

    # print(df["appartement_simple"].unique())

    # list of all unique addresses
    # according to site: Naam volgens akte
    # """
    # Vereniging van Eigenaars van het gebouw Piramide, gelegen aan het 
    # Sumatraplantsoen 20 t/m 38 (even nrs)
    # Sumatrastraat 217 t/m 231 (oneven nrs)
    # Tidorestraat 58 t/m 128 (even nrs)
    # Molukkenstraat 411 t/m 545 (oneven nrs)
    # """
    df.to_csv("datasets/reparaties_link.csv")


def parse_kleinonderhoud_facturen_link():

    """
    GROOTBOEKREKENING dagelijksonderhoud/kleinonderhoud analysis

    Data has been scraped off twinq and presented in usable format. 

    """
    kleinonderhoud = pd.read_csv("datasets/VvE_piramide__Dagelijks onderhoud - Klein onderhoud.csv")
    
    kleinonderhoud["Factuurbedrag"] = kleinonderhoud["Factuurbedrag"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).str.replace("€", "", regex=False).astype(float)
    kleinonderhoud["Debet"] = kleinonderhoud["Debet"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).str.replace("", "", regex=False).astype(float)

    #convert Datum Sorted Ascending to timestamp ! NOTE now just Datum not Datum Sorted Ascending
    kleinonderhoud["Datum"] = pd.to_datetime(kleinonderhoud["Datum"], format="%d-%m-%Y")
    kleinonderhoud["Jaar"] = kleinonderhoud["Datum"].dt.year
    kleinonderhoud["tag"] = kleinonderhoud["Opdracht/contract gegevens"].apply(lambda x: x.split("|")[0] if "|" in str(x) else "no tag")
    kleinonderhoud["tag"]
    # kleinonderhoud["ATD related"] = kleinonderhoud["Opdracht/contract gegevens"].apply(lambda x: "ATD" in str(x))
    total_kost_klein_onderhoud = kleinonderhoud["Factuurbedrag"].sum()

    # REGEX expression to fish out the verzoeknummer. We use this later to link to reparatieverzoeken.

    kleinonderhoud["verzoeknummer1"] = kleinonderhoud["Omschrijving"].str.extract(r'(\d+)-\d\)') # pattern e.g.: (79969-1)
    kleinonderhoud["verzoeknummer2"] = kleinonderhoud["Omschrijving"].str.extract(r'bon\s+(\d+)') # pattern e.g.: bon 79969
    kleinonderhoud["verzoeknummer3"] = kleinonderhoud["Omschrijving"].str.extract(r'b\son\s+(\d+)') # pattern e.g.: b on 79969
    kleinonderhoud["verzoeknummer4"] = kleinonderhoud["Omschrijving"].str.extract(r'fact\.\s+(\d+)') # pattern e.g.: fact. 131314
    kleinonderhoud["verzoeknummer5"] = kleinonderhoud["Omschrijving"].str.extract(r'\s(\d+)-\d$') # pattern e.g.: fact. 87458-2


    # merge all the regex finds into one column
    kleinonderhoud["verzoeknummer_link"]  = kleinonderhoud['verzoeknummer1'].fillna('') + kleinonderhoud['verzoeknummer2'].fillna('') + kleinonderhoud['verzoeknummer3'].fillna('') + kleinonderhoud['verzoeknummer4'].fillna('') + kleinonderhoud['verzoeknummer5'].fillna('')
    kleinonderhoud.drop(columns=["verzoeknummer1", "verzoeknummer2", "verzoeknummer3", "verzoeknummer4", "verzoeknummer5"], inplace=True)


    kleinonderhoud["verzoeknummer_link"] = kleinonderhoud["verzoeknummer_link"].apply(lambda x: "MISSING" if x == "" else str(x))
    kleinonderhoud.loc[kleinonderhoud["verzoeknummer_link"].isna()]

    kleinonderhoud.to_csv("datasets/klein_onderhoud_link.csv", encoding="utf-8-sig")

  

def merge_facturen_en_verzoeken():
    reparaties = pd.read_csv("datasets/reparaties_link.csv", index_col=0)
    kleinonderhoud = pd.read_csv("datasets/klein_onderhoud_link.csv", index_col=0)

    # convert appartement_simple_list to actual list
    reparaties['appartement_simple_list'] = reparaties['appartement_simple_list'].apply(ast.literal_eval)

    if "Verzoek Sorted Descending" in reparaties.columns:
        reparaties.rename(columns={'Verzoek Sorted Descending': 'Verzoek'}, inplace=True)

    data_columns = ["Verzoek", "Omschrijving", "Type", "Status"
                    , "Datum", "Opdracht", "Appartementsrecht(en)", "Eigenaar(s)",
                    "appartement_simple_list", "count of apartments in row"]
    # NOTE column "gemeld door" missing in 2024 twinq site?
    reparaties = reparaties[data_columns]

    # link column: Verzoek
    reparaties["Verzoek"] = reparaties["Verzoek"].astype(str)

    merged = kleinonderhoud.set_index("verzoeknummer_link").join(reparaties.set_index("Verzoek"), rsuffix="_reparatie")
    
    # link column: verzoeknummer_link
    merged.index.name = 'Verzoeknummer'
    merged.reset_index(inplace=True)
    merged[["Verzoeknummer", "appartement_simple_list"]]


    # set all values in merged["appartement_simple_list"] to a list if nan
    merged["appartement_simple_list"] = merged["appartement_simple_list"].apply(lambda x: [] if type(x) == float else x)

    # create new column Building to define which building the adress is located in
    merged["Building"] = merged["appartement_simple_list"].apply(lambda x: "No building defined" if len(x) == 0 else "Plantsoen" if any([y in SUMATRAPLANTSOEN_GEBOUW for y in x]) else "Molukken" if any([y in MOLUKKEN_GEBOUW for y in x]) else "Other")
    merged["Building"].value_counts()

    #PORTIEKEN

    # NOTE this is dangerous as it assumed any combination of complaints is ALWAYS part of ONE portiek. This dataset even contains instances of multiple portieken for one complaint, which is weird. 
    # NOTE also note that not all portieken are purely vertical blocks, the 4th floor is notorious for being its own portiek while covering many other portieken.

    # behold this monster of a list comprehension
    merged["Portiek"] = merged["appartement_simple_list"].apply(lambda x: "No portiek defined" if len(x) == 0 else PORTIEKEN[x[0]] if any([y in PORTIEKEN for y in x]) and len(x) == 1 else list(set(PORTIEKEN[y] for y in x)) if len(list(set(PORTIEKEN[y] for y in x))) > 1 else list(set(PORTIEKEN[y] for y in x))[0])
    merged["Portiek"].value_counts()

    print("Saving merged verzoek with facturen...")
    merged.to_csv("datasets/klein_onderhoud_gekoppeld_met_verzoek.csv", encoding="utf-8")
    merged.to_excel("datasets/klein_onderhoud_gekoppeld_met_verzoek.xlsx")
    print("Done saving merged verzoek with facturen...")
    print("Files can be found as datasets/klein_onderhoud_gekoppeld_met_verzoek.xlsx")


def harmonize_missing_values():
    pass

if __name__ == '__main__':
    main()