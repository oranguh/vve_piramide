#%%
import geopandas as gpd
import numpy as np
import os
from pathlib import Path
import seaborn as sns
import pandas as pd
import json
import time

from general_data import PORTIEKEN, invert_dict

#%%

portiek_inverted = invert_dict(PORTIEKEN)
portiek_inverted

#%%

def make_portiek_dataset(years: list = None):
    # initial dataset, including non defined portieken and additional row for cases where mutliple portieken are defined (which really should not be allowed)
    portiek_df = pd.DataFrame(index=[*set(PORTIEKEN.values()), "Multiple portieken", "No portiek defined"])
    portiek_df["Portiek"] = portiek_df.index

    # prepare connection dataset

    # apartments dataset is fine as is
    appartments_df = pd.read_csv('datasets/appartementen_df_complete.csv')

    # klein dagelijks onderhoud needs to be adjusted for multipel portieken entries
    klein_onderhoud = pd.read_excel('datasets/klein_onderhoud_gekoppeld_met_verzoek.xlsx', index_col=0)
    klein_onderhoud["Portiek"] = klein_onderhoud["Portiek"].apply(lambda x: "Multiple portieken" if "['" in x else x)
    
    if years:
        print(f"Filtering on years: {years}")
        # we only have data from 2016 onwards
        current_year = time.localtime().tm_year
        valid_years = list(range(2016, current_year+1))

        if all(year not in valid_years for year in years):
            print(f"Years {years} not in valid range of {valid_years} skipping filtering")

        else:
            klein_onderhoud = klein_onderhoud.loc[klein_onderhoud["Jaar"].isin(years), :]
        # if year not in valid_years:
        #     print(f"Year {year} not in valid range of {valid_years} skipping filtering")
        # else:
        #     klein_onderhoud = klein_onderhoud.loc[klein_onderhoud["Jaar"]==year, :]


    portiek_df["Reparatie_counts"] = klein_onderhoud["Portiek"].value_counts().astype(int)
    portiek_df["reparatie_kosten_totaal"] = klein_onderhoud.groupby("Portiek")["Factuurbedrag"].sum()
    onderhoud_id_dict = klein_onderhoud.groupby('Portiek')['unique_id'].apply(list).to_dict()
    portiek_df["reparatie_ids"] = portiek_df["Portiek"].apply(lambda x: onderhoud_id_dict[x] if x in onderhoud_id_dict else np.nan)

    portiek_df["apartments"] = portiek_df["Portiek"].apply(lambda x: portiek_inverted[x] if x in portiek_inverted else np.nan)
    groupby_breukdeel_sum = appartments_df[["Portiek", "Breukdeel"]].groupby("Portiek").sum()
    portiek_df["Breukdeel_portiek"] = portiek_df["Portiek"].apply(lambda x: groupby_breukdeel_sum.loc[x, "Breukdeel"] if x in groupby_breukdeel_sum.index else np.nan)
    portiek_df["apartments_count"] = portiek_df["Portiek"].apply(lambda x: len(portiek_inverted[x]) if x in portiek_inverted else 0)

    groupby_ymere_count = appartments_df.loc[appartments_df["Bezit Ymere"],["Portiek", "Bezit Ymere"]].groupby("Portiek").count()
    portiek_df["Bezit_Ymere_count"] = portiek_df["Portiek"].apply(lambda x: groupby_ymere_count.loc[x, "Bezit Ymere"] if x in groupby_ymere_count.index else 0)
    portiek_df["percentage_Ymere"] = portiek_df["Bezit_Ymere_count"]/portiek_df["apartments_count"]*100

    groupby_gebouw = appartments_df[["Portiek", "Gebouw"]].groupby("Portiek").first()
    portiek_df["Gebouw"] = portiek_df["Portiek"].apply(lambda x: groupby_gebouw.loc[x, "Gebouw"] if x in groupby_gebouw.index else np.nan)

    groupby_oppervlakte = appartments_df[["Portiek", "oppervlakte"]].groupby("Portiek").sum()
    portiek_df["Totale_oppervlakte"] = portiek_df["Portiek"].apply(lambda x: groupby_oppervlakte.loc[x, "oppervlakte"] if x in groupby_oppervlakte.index else np.nan)

    groupby_woz_2022_sum = appartments_df[["Portiek", "WOZ_2022"]].groupby("Portiek").sum()
    groupby_woz_2022_mean = appartments_df[["Portiek", "WOZ_2022"]].groupby("Portiek").mean()

    portiek_df["Totale_WOZ_2022"] = portiek_df["Portiek"].apply(lambda x: groupby_woz_2022_sum.loc[x, "WOZ_2022"] if x in groupby_woz_2022_sum.index else np.nan)
    portiek_df["Gemiddelde_WOZ_2022"] = portiek_df["Portiek"].apply(lambda x: groupby_woz_2022_mean.loc[x, "WOZ_2022"] if x in groupby_woz_2022_mean.index else np.nan)

    portiek_df["Reparatiekosten_per_breukdeel"] = portiek_df["reparatie_kosten_totaal"]/portiek_df["Breukdeel_portiek"]
    portiek_df["Reparatiekosten_per_appartement"] = portiek_df["reparatie_kosten_totaal"]/portiek_df["apartments_count"]
    portiek_df["Reparatie_aantal_per_breukdeel"] = portiek_df["Reparatie_counts"]/portiek_df["Breukdeel_portiek"]
    portiek_df["Reparatie_aantal_per_appartement"] = portiek_df["Reparatie_counts"]/portiek_df["apartments_count"]

    return portiek_df


# %%

# NOTE The data used for reparatieverzoeken is ALL DATES. If you want to further filter on year then we would need a different/more comprehensive dataset.

years = None

df = make_portiek_dataset(years = [2022, 2016])
df
# df.to_csv("portieken_met_reparatie_ids.csv", encoding="utf-8-sig")
# df.to_excel("portieken_met_reparatie_ids.xlsx")
# %%
