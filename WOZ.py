# WOZ https://www.linkedin.com/pulse/howto-wozwaardeloket-met-python-peter-wieringa/?originalSubdomain=nl
# https://www.wozwaardeloket.nl/?locatie=1095HM%0092
# %%
from collections import namedtuple
import requests
from urllib.parse import urlencode, urljoin
import logging
from requests.exceptions import RequestException
import pandas as pd
import time
import json
import os
import datetime
import numpy as np
# %%
# https://github.com/wpeterw/wozpy/blob/main/wozpy/woz.py
# Is this how you are supposed to code? I find it difficult to read and understand

class WoZ:
    def __init__(self):
        self.session_url = "https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/session/start"

    
    @property
    def __get_session(self):
        """get session key"""
        # result = requests.get(url=self.session_url)

        # print(result.cookies.get_dict())
        print(self.__get_cookie())
        lb_sticky = self.__get_cookie().get("LB_STICKY")
        session = self.__get_cookie().get("SESSION")

        return session, lb_sticky
    
    def __get_cookie(self, timeout=5) -> dict:
        """Get a cookie for the WOZ web service."""
        url = self.session_url
        try:
            response = requests.post(url=url, timeout=timeout)
            # x = response.cookies.get_dict()
            response.raise_for_status()
            return response.cookies.get_dict()
        except RequestException as exception:
            logging.exception(
                "Error while getting cookie from wozwaardeloket.nl: %s", exception
            )
            return None

    # https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/wozwaarde/nummeraanduiding/0377200000000030127

    def get_woz_value(self, nummeraanduiding):
        """get woz value"""
        session, lb_sticky = self.__get_session

        headers = {"Cookie": f"LB_STICKY={lb_sticky}; SESSION={session}"}
        url = f"https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/wozwaarde/nummeraanduiding/{nummeraanduiding}"

        print(headers)
        woz = requests.get(url=url, headers=headers, timeout=5)
        return woz
    


# url = f"https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/wozwaarde/nummeraanduiding/{nummeraanduiding}"



# print(woz.json())
# LB_STICKY=38ef4dc6a5b6e95d; SESSION=7E4159778E260126DA478AA138AA1620


def get_woz_value(nummeraanduiding):
    """get woz value"""
    time.sleep(1)
    if True:
        session = "B3CC04897DB132573D80B1B5760B9017" 
        lb_sticky = "45b96085e515fb1b"

        nummeraanduiding = "0" + str(nummeraanduiding)

        headers = {"Cookie": f"LB_STICKY={lb_sticky}; SESSION={session}"}
        url = f"https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/wozwaarde/nummeraanduiding/{nummeraanduiding}"

        woz = requests.get(url=url, headers=headers, timeout=5)
    if False:

        woz_object = WoZ()
        woz = woz_object.get_woz_value(nummeraanduiding)

    return woz
    




if os.path.exists("appartementen_df_WOZ.xlsx"):
    df = pd.read_excel("datasets/appartementen_df_WOZ.xlsx", index_col=0)
    if "woz_value" not in df.columns:
        df["woz_value"] = ""
    else:
        df_ = df[df["woz_value"].isna()].copy()
    df_ = df.copy()
else:
    df = pd.read_excel("datasets/appartementen_df_BAG.xlsx", index_col=0)
    df["woz_value"] = ""
    df_ = df.copy()

for index, row in df_.iterrows():
    print(index)
    nummeraanduiding = row["nummeraanduidingIdentificatie"]
    print(nummeraanduiding)
    woz = get_woz_value(nummeraanduiding)
    if woz.status_code == 200:
        
        print(json.dumps(woz.json(), indent=4))
        df.at[index, "woz_value"] = json.dumps(woz.json()['wozWaarden'])
        df.to_excel("appartementen_df_WOZ.xlsx")
    else:
        print(f"status code: {woz.status_code}")
        print(json.dumps(woz.json(), indent=4))
        break
    time.sleep(5)
    
    # TODO load the data and only do values that are missing. Also check if status was 400 otherwise it is not a valid request




# %%
df = pd.read_excel("datasets/appartementen_df_WOZ.xlsx", index_col=0)
# parsing the text into data, i.e. WOZ values per year
for index, row in df.iterrows():
    woz_text = json.loads(row["woz_value"])
    for woz_year in woz_text:
        year_in_question = datetime.datetime.strptime(woz_year["peildatum"], "%Y-%m-%d").year
        woz_value = woz_year["vastgesteldeWaarde"]
        if f"WOZ_{year_in_question}" not in df.columns:
            df[f"WOZ_{year_in_question}"] = np.nan
        df.at[index, f"WOZ_{year_in_question}"] = woz_value

df.drop(columns=["woz_value"], inplace=True)
df.to_excel("datasets/appartementen_df_WOZ.xlsx")
# %%
