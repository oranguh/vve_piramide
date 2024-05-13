# %%

import os
import requests
import time
import pandas as pd

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
# import chromedriver_autoinstaller


# %%
test_key = "l7f4724a678ad3446e9bbef9b0179f7bd3"
# prod_key = "l7e2bdd200b9d4495db5d695aea52ddc74"

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_KEY = test_key
if API_KEY is None:
    raise ValueError("API_KEY environment variable is not set")
print(API_KEY)



# %%
def call_API_BAG(postcode, huisnummer, huisletter):
    exacteMatch = "true"
    url = f"https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/adressenuitgebreid"
    url = url + f"?postcode={postcode}"
    url = url + f"&huisnummer={huisnummer}"
    if not pd.isna(huisletter):
        url = url + f"&huisletter={huisletter}"
    url = url + f"&exacteMatch={exacteMatch}"
    url = url + f"&page=1"
    url = url + f"&pageSize=20"
    url = url + f"&inclusiefEindStatus=true"

    # response = requests.get(url)
    # epsg:28992 is the RD coordinate system, Amersfoort central point
    headers = {"X-Api-Key": API_KEY,
                "content-type": "application/json",
                "Accept-Crs": "epsg:28992",
                "accept": "application/hal+json"}
            #    "Accept": "application/json"}    
    response = requests.get(url, headers=headers)
    oppervlakte = response.json()["_embedded"]["adressen"][0]["oppervlakte"]
    locatie = response.json()["_embedded"]["adressen"][0]["adresseerbaarObjectGeometrie"]["punt"]["coordinates"]
    adresseerbaarObjectIdentificatie = response.json()["_embedded"]["adressen"][0]["adresseerbaarObjectIdentificatie"]
    nummeraanduidingIdentificatie = response.json()["_embedded"]["adressen"][0]["nummeraanduidingIdentificatie"]

    time.sleep(1)
    return oppervlakte, locatie, adresseerbaarObjectIdentificatie, nummeraanduidingIdentificatie


df = pd.read_excel("datasets/appartementen_df.xlsx", index_col=0)

df[["postcode", "huisnummer", "huisletter"]]

df[["oppervlakte", "locatie", "adresseerbaarObjectIdentificatie", "nummeraanduidingIdentificatie"]] = df.apply(lambda x: call_API_BAG(x["postcode"], x["huisnummer"], x["huisletter"]), axis=1, result_type="expand")


df[["oppervlakte", "locatie", "adresseerbaarObjectIdentificatie", "nummeraanduidingIdentificatie"]]
# %%
def rd_to_wgs(x, y): # from https://github.com/djvanderlaan/rijksdriehoek/blob/master/Python/rijksdriehoek.py
    """
    Convert rijksdriehoekcoordinates into WGS84 cooridnates. Input parameters: x (float), y (float). 
    """

    X0      = 155000
    Y0      = 463000
    PHI0    = 52.15517440
    LAM0    = 5.38720621


    if isinstance(x, (list, tuple)):
        x, y = x

    pqk = [(0, 1, 3235.65389),
        (2, 0, -32.58297),
        (0, 2, -0.24750),
        (2, 1, -0.84978),
        (0, 3, -0.06550),
        (2, 2, -0.01709),
        (1, 0, -0.00738),
        (4, 0, 0.00530),
        (2, 3, -0.00039),
        (4, 1, 0.00033),
        (1, 1, -0.00012)]

    pql = [(1, 0, 5260.52916), 
        (1, 1, 105.94684), 
        (1, 2, 2.45656), 
        (3, 0, -0.81885), 
        (1, 3, 0.05594), 
        (3, 1, -0.05607), 
        (0, 1, 0.01199), 
        (3, 2, -0.00256), 
        (1, 4, 0.00128), 
        (0, 2, 0.00022), 
        (2, 0, -0.00022), 
        (5, 0, 0.00026)]

    dx = 1E-5 * ( x - X0 )
    dy = 1E-5 * ( y - Y0 )
    
    phi = PHI0
    lam = LAM0

    for p, q, k in pqk:
        phi += k * dx**p * dy**q / 3600

    for p, q, l in pql:
        lam += l * dx**p * dy**q / 3600

    return [phi,lam]

df["locatie"] = df["locatie"].apply(lambda x: rd_to_wgs(x[0], x[1]))
df["locatie"]
# %%
df.to_excel("datasets/appartementen_df_BAG.xlsx")
df.to_csv("datasets/appartementen_df_BAG.csv")

# %%
pand_ids = ["0363100012062297", "0363100012107335", "0363100012147093", "0363100012061643", 
            "0363100012069115", "0363100012116534", "0363100012154583", "0363100012090247", 
            "0363100012070634", "0363100012072436"]

def make_geometries_panden(pand_ids):
    pand_id = pand_ids[0]
    url = f"https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/panden/"
    url = url + f"{pand_id}"
    url = url + f"?geldigOp=2019-11-23"
    url = url + f"&huidig=false"

    headers = {"X-Api-Key": API_KEY,
            "content-type": "application/json",
            "Accept-Crs": "epsg:28992",
            "accept": "application/hal+json"}
        #    "Accept": "application/json"}    
    
# # 

# %%

    



