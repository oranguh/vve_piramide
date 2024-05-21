
#%%
import os
import ast
import re
from pathlib import Path

import pandas as pd
import numpy as np
import seaborn as sns
import seaborn.objects as so
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from tabulate import tabulate

import pdfplumber
from general_data import MOLUKKEN_GEBOUW, SUMATRAPLANTSOEN_GEBOUW, DAKAANBOUW, PORTIEKEN

#%%
### NOTE Dit is alleen een dataset met HUIDIGE eigenaren. Dus niet de historie van alle verkopen.
### private verkoop tussen particulieren zouden dan hier onderbelicht worden. 
### bijv. als een woning 3x verkocht is tussen particulieren, dan staat alleen de laatste eigenaar in deze dataset.

encoding = "ISO-8859-1"
appartementen_df = pd.read_csv("datasets/overzicht_eigenaarsregister.csv", sep=";", encoding=encoding)
appartementen_df["Appartement"] = appartementen_df["Appartementsrecht"].str.replace(" (Woning met berging en tuin)", "", regex=False).str.replace(" (Woning met berging)", "", regex=False)
appartementen_df["Tuin aanwezig"] = appartementen_df["Appartementsrecht"].str.contains(" tuin", case=False, regex=False)
appartementen_df["Bezit Ymere"] = appartementen_df["Eigenaar"].str.contains("Ymere", case=False, regex=False)
# %%
totale_breukdeel = appartementen_df["Breukdeel"].sum()

Ymere_breukdeel = appartementen_df.loc[appartementen_df["Eigenaar"]=="Stichting Ymere", "Breukdeel"].sum()

print(f"Ymere heeft {Ymere_breukdeel/totale_breukdeel*100:.2f}% van de woningen in bezit.")

# %%

bruekdeel_sumatra = 0
for x in SUMATRAPLANTSOEN_GEBOUW:
    bruekdeel_sumatra += appartementen_df.loc[appartementen_df["Appartement"]==x, "Breukdeel"].values[0]
    # print(appartementen_df.loc[appartementen_df["Appartement"]==x, "Breukdeel"])

breukdeel_molukken = 0
for x in MOLUKKEN_GEBOUW:
    breukdeel_molukken += appartementen_df.loc[appartementen_df["Appartement"]==x, "Breukdeel"].values[0]
    # print(appartementen_df.loc[appartementen_df["Appartement"]==x, "Breukdeel"])
breukdeel_totaal = bruekdeel_sumatra + breukdeel_molukken
print(f"bruekdeel_sumatra: {bruekdeel_sumatra}")
print(f"breukdeel_molukken: {breukdeel_molukken}")
print(f"breukdeel totaal {breukdeel_totaal}")
# for x in MOLUKKEN_GEBOUW:
#     print(x)
# %%


def parse_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        all_text = ""
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]

            # Extract text
            text = page.extract_text()
            all_text += text
            # print(f"Text from Page {page_number + 1}:\n{text}\n")

        address_list = [x for x in all_text.split("\n") if "VvE-bijdrage" in x]

        pattern = re.compile(r' - (.+?) \(Woning')

        # Extract information using regex
        address_list = [pattern.search(entry).group(1) if pattern.search(entry) else None for entry in address_list]
        return address_list

appartementen_df.set_index("Appartement", inplace=True, drop=True) # here we drop the original index, since it is not useful
appartementen_df.rename(columns={"Index": "Appartementsindex"}, inplace=True)
# address_data = pd.DataFrame(index=[*MOLUKKEN_GEBOUW, *SUMATRAPLANTSOEN_GEBOUW])

appartementen_df["Gebouw"] = appartementen_df.index.map(lambda x: "Molukken" if x in MOLUKKEN_GEBOUW else "Sumatra" if x in SUMATRAPLANTSOEN_GEBOUW else None)
appartementen_df["Dakaanbouw"] = appartementen_df.index.map(lambda x: True if x in DAKAANBOUW else False)

#portiek
appartementen_df["Portiek"] = appartementen_df.index.map(lambda x: PORTIEKEN[x] if x in PORTIEKEN else None)
# appartementen_df["breukdeel"] = appartementen_df.index.map(lambda x: appartementen_df.loc[appartementen_df["Appartement"]==x, "Breukdeel"].values[0])

# weird situation where kpn finance amersfoort pays for vve of some ymere apartments. in 2017, so I remove 2017
years = [2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

for year in years:
        
    file_path = f"vve_contributie_facturen/ymere_{year}.pdf"
    address_list = parse_pdf(file_path)
    if year == 2017:
        # Molukkenstraat 493-545 was paid by KPN Finance Amersfoort in 2017
        # probably also other addresses, but invoices are incorrect
        continue
    
    appartementen_df[year] = appartementen_df.index.map(lambda x: "Ymere" if x in address_list else "Particulier")

appartementen_df.head(3)

appartementen_df['non-ymere from'] = None

# Iterate over each row to check for ownership changes
for address in appartementen_df.index:
    previous_owner = "Ymere"

    # Iterate over each year column
    for year in years:
        if year == 2017:
            continue
        current_owner = appartementen_df.loc[address, year]

        # Check if the owner has changed
        if current_owner != previous_owner:
            appartementen_df.at[address, 'non-ymere from'] = year
            previous_owner = current_owner

def vve_contribute_berekening(appartementen_df):
    alle_contributie_columns = []
    for file in Path("vve_contributie_berekening").glob("*.csv"):
        df = pd.read_csv(file, sep=";", encoding=encoding)
        df = df[["Datum", "Omschrijving", "Credit"]]
        df["Appartement"] = df["Omschrijving"].apply(lambda x: x.split(" - ")[-1].replace(" (Woning met berging en tuin)", "").replace(" (Woning met berging)", ""))
        df["Credit"] = df["Credit"].str.replace("", "").str.replace(",", ".").astype(float)
        # get Credit value into appartementen_df, match on appartement
        appartementen_df[file.stem] = 0
        mapping = dict(df[['Appartement', 'Credit']].values)
        appartementen_df[file.stem] = appartementen_df.index.map(mapping)
        appartementen_df[file.stem] = appartementen_df[file.stem].fillna(0)
        alle_contributie_columns.append(file.stem)
        if "lift" in str(file.stem):
            appartementen_df["Betaalt_voor_lift"] = appartementen_df[file.stem].apply(lambda x: True if x > 0 else False)

    # add up all the columns
    appartementen_df["Totale contributie"] = appartementen_df[alle_contributie_columns].sum(axis=1)
    # appartementen_df["Totale contributie"] = appartementen_df.sum({col: alle_contributie_files}, axis=1)

    return appartementen_df
appartementen_df = vve_contribute_berekening(appartementen_df)

# %%
#straat, postcode, huisnummer, huisletter, huisnummertoevoeging toevoegen

appartementen_df["straat"] = appartementen_df.index.map(lambda x: x.split(" ")[0])
appartementen_df["huisnummer"] = appartementen_df.index.map(lambda x: x.split(" ")[1])
appartementen_df["huisnummer"] = appartementen_df["huisnummer"].apply(lambda x: x.split("-")[0] if "-" in x else x)
appartementen_df["huisletter"] = appartementen_df.index.map(lambda x: x.split("-")[1] if "-" in x else "")

# Tidorestraat 88-A/B, Molukkenstraat 463-A/B/C, Molukkenstraat 471-A/B/C
# are not official huisletters. Removed for working with BAG/Kadaster
appartementen_df["huisletter"] = appartementen_df["huisletter"].apply(lambda x: "" if x in ["A/B", "A/B/C"] else x)

# appartementen_df["adres_officieel"] = appartementen_df.index
# appartementen_df["adres_officieel"] = appartementen_df["adres_officieel"].apply(lambda x: x.split("-")[0] if "/" in x else x)

# postcodes, https://allecijfers.nl/postcode/1095HN/
# 1095 HN if Sumatrastraat 217 - 223
# 1095 HP if Sumatrastraat 225 - 231

# 1095 HM if Tidorestraat 58 - 98
# 1095 HK if Tidorestraat 100 - 128

# 1095 BJ if Molukkenstraat 411 - 545

# 1095 JA if Sumatraplantsoen 18 - 22
# 1095 JB if Sumatraplantsoen 24 - 38

def generate_postal_code(straat, nummer):

    if straat == "Molukkenstraat":
        return "1095 BJ"
    elif straat == "Sumatrastraat":
        if 217 <= int(nummer) <= 223:
            return "1095 HN"
        elif 225 <= int(nummer) <= 231:
            return "1095 HP"
        else:
            return "Unknown"
    elif straat == "Tidorestraat":
        if 58 <= int(nummer) <= 98:
            return "1095 HM"
        elif 100 <= int(nummer) <= 128:
            return "1095 HK"
        else:
            return "Unknown"
    elif straat == "Sumatraplantsoen":
        if 18 <= int(nummer) <= 22:
            return "1095 JA"
        elif 24 <= int(nummer) <= 38:
            return "1095 JB"
        else:
            return "Unknown"
    else:
        return "Unknown"

appartementen_df["postcode"] = appartementen_df.apply(lambda x: generate_postal_code(x["straat"], x["huisnummer"]), axis=1)

# for row in appartementen_df[["postcode"]].iterrows():
#     print(row)
# %%
# set floor for every apartment based off column named index

floor_0 = ["A-" + str(x).zfill(3) for x in range(1,32)]
floor_1 = ["A-" + str(x).zfill(3) for x in range(32,70)]
floor_2 = ["A-" + str(x).zfill(3) for x in range(70,108)]
floor_3 = ["A-" + str(x).zfill(3) for x in range(108,158)]
floor_4 = ["A-" + str(x).zfill(3) for x in range(158,178)]

# NOTE EXCEPTIONS, these appartmenindexes have been changed over time, no idea why?
renamed = {
    "A-092": "A-178",
    "A-091": "A-179",
    "A-019": "A-180",
    "A-093": "A-181",
    "A-053": "A-182",
    "A-140": "A-183",
    "A-054": "A-184",
    "A-142": "A-185",
    "A-090": "A-186",
    "A-055": "A-187",
}
inv_renamed = {v: k for k, v in renamed.items()}

# we use the old index to use as a key to match with the geodata. Which is based off of old blueprints which use the old index
appartementen_df["Appartementsindex_oud"] = appartementen_df["Appartementsindex"].apply(lambda x: inv_renamed[x] if x in inv_renamed else x)

floor_0 = [renamed[x] if x in renamed else x for x in floor_0]
floor_1 = [renamed[x] if x in renamed else x for x in floor_1]
floor_2 = [renamed[x] if x in renamed else x for x in floor_2]
floor_3 = [renamed[x] if x in renamed else x for x in floor_3]
floor_4 = [renamed[x] if x in renamed else x for x in floor_4]


appartementen_df.reset_index(inplace=True) 
appartementen_df.set_index("Appartementsindex", inplace=True)

appartementen_df["verdieping"] = None
appartementen_df.loc[floor_0, "verdieping"] = 0
appartementen_df.loc[floor_1, "verdieping"] = 1
appartementen_df.loc[floor_2, "verdieping"] = 2
appartementen_df.loc[floor_3, "verdieping"] = 3
appartementen_df.loc[floor_4, "verdieping"] = 4

# for row in appartementen_df[["verdieping"]].iterrows():
#     print(row)


# %%





# %%

# NOTE NOTE SAVE EXCEL HERE NOTE NOTE
appartementen_df_ = appartementen_df.drop(columns=appartementen_df.columns.intersection(years)).copy()
appartementen_df_.reset_index(inplace=True)
appartementen_df_.set_index("Appartement", inplace=True)
appartementen_df_.sort_index(inplace=True)
appartementen_df_.to_csv("datasets/appartementen_df.csv")

print("saved appartementen_df")

# %%

# Merge various data sources together

# Merge energielabel

appartementen_df = pd.read_csv("datasets/appartementen_df.csv").set_index("Appartement")

df_energie = pd.read_excel("datasets/appartementen_df_energielabel.xlsx", index_col=0)
cols_to_use = df_energie.columns.difference(appartementen_df.columns)
appartementen_df = pd.merge(appartementen_df, df_energie[cols_to_use], left_index=True, right_index=True, how="left")
# Merge BAG
df_BAG = pd.read_excel("datasets/appartementen_df_BAG.xlsx", index_col=0)
cols_to_use = df_BAG.columns.difference(appartementen_df.columns)
appartementen_df = pd.merge(appartementen_df, df_BAG[cols_to_use], left_index=True, right_index=True, how="left")
# Merge WOZ
df_WOZ = pd.read_excel("datasets/appartementen_df_WOZ.xlsx", index_col=0)
cols_to_use = df_WOZ.columns.difference(appartementen_df.columns)
appartementen_df = pd.merge(appartementen_df, df_WOZ[cols_to_use], left_index=True, right_index=True, how="left")
# Merge GeoData
#TODO

# calcualte WOZ per m2 per year
columns_WOZ = [x for x in appartementen_df.columns if "WOZ_" in x]
for col in columns_WOZ:
    appartementen_df[f"{col}_per_m2"] = appartementen_df[col]/appartementen_df["oppervlakte"]
    appartementen_df[f"{col}_per_m2"] = appartementen_df[f"{col}_per_m2"].round(2)


####################################
#save values
appartementen_df.to_csv("datasets/appartementen_df_complete.csv")
appartementen_df.to_excel("datasets/appartementen_df_complete.xlsx")

print("saved appartementen_df_complete.csv")


###################################

# %%
columns_WOZ = [x for x in appartementen_df.columns if "_per_m2" in x]

appartementen_df[columns_WOZ]

mean_woz = {}

for col in columns_WOZ:
    print(col)
    year = int(col.split("_")[1])
    mean = appartementen_df[col].mean()
    std = appartementen_df[col].std()
    # print(f"{year}: mean: {mean:.2f}, std: {std:.2f}")
    mean_woz[col] = f"{year}: mean: {mean:.0f}, std: {std:.0f}"

print(mean_woz)
# %%
longform_df = appartementen_df[columns_WOZ].stack().reset_index()
longform_df.rename(columns={"level_1": "year", 0: "WOZ_per_m2"}, inplace=True)
longform_df = longform_df.join(appartementen_df[["Tuin aanwezig", "Bezit Ymere", "verdieping"]], on="Appartement")
longform_df["title"] = longform_df["year"].apply(lambda x: str(mean_woz[x]))
fig, ax = plt.subplots(figsize=(20, 10))
sns.histplot(data=longform_df, x="WOZ_per_m2", kde=True, hue="title", element="step", stat="density", ax=ax)
# longform_df

# %%
latest_year = "2023"
longform_df_ = longform_df[longform_df["year"]==f"WOZ_{latest_year}_per_m2"].copy()

fig, ax = plt.subplots(figsize=(20, 10))
sns.histplot(data=longform_df_, x="WOZ_per_m2", kde=True, hue="Tuin aanwezig", element="step", stat="density", ax=ax)

fig, ax = plt.subplots(figsize=(20, 10))
sns.histplot(data=longform_df_, x="WOZ_per_m2", kde=True, hue="Bezit Ymere", element="step", stat="density", ax=ax)


# %%
# the column "year" is weird here and a misnomer, but whatever it works.

longform_df_ = longform_df[longform_df["year"]==f"WOZ_{latest_year}_per_m2"]
desc_df = longform_df_[["WOZ_per_m2", "year", "Tuin aanwezig"]].groupby(["year", "Tuin aanwezig"]).describe().astype(int)
print(desc_df)
desc_df = longform_df_[["WOZ_per_m2", "year", "Bezit Ymere"]].groupby(["year", "Bezit Ymere"]).describe().astype(int)
print(desc_df)
desc_df = longform_df_[["WOZ_per_m2", "year", "verdieping"]].groupby(["year", "verdieping"]).describe().astype(int)
print(desc_df)


desc_df = longform_df[["WOZ_per_m2", "year"]].groupby("year").describe().astype(int)
print(desc_df.loc[:,(slice(None),['count','mean', 'std', 'min', 'max'])])


# %%
# plot scatterplot
fig, ax = plt.subplots(figsize=(20, 10))
hue = "Bezit Ymere"
hue = "verdieping"
sns.scatterplot(data=appartementen_df, x="oppervlakte", y="Breukdeel", hue=hue, ax=ax, palette="deep")





# %%

#TODO https://amsterdam.mijndak.nl/verhuurd verhuizingen binnen social huur
#done Which apartments have dakopbouw en tuinaanbouw. 
#DONE gather data on apartment locations e.g. which apartment is on which floor, 
#Done which apartments are neighbours, portieken
#TODO locate which apartments are associated with sewage problems
#DONE link appartment information with kadaster
#DONE link apartment with WOZ data
#TODO apartments and their vergunningen (omgevingsvergunningen)
#DONE energielabel
#DONE add postcode, huisnummer, and huisnummertoevoeging to appartementen_df (and eventueleel huisletter)
#DONE get plots into plotly on google collab or something
#DONE servicekosten berekening doen

#NOTE BAG/Kadaster woonoppervlakte is niet altijd correct. 
# https://vkmakelaars.nl/blog/informatie-over-taxaties/de-oppervlakte-van-mijn-woning-klopt-niet-in-de-bag-kadaster-en-of-woz-aanslag-hoe-kan-ik-dat-laten-aanpassen/

# https://ymere.docufiller.nl/docupage/view/ZHBhZzo1ODcw/ce5fd34420efce57bb2fcf6808c7be2b#page/6
# omgevingsvergunningen onze buurt.
# https://zoek.officielebekendmakingen.nl/gmb-2024-184283.html?utm_campaign=20240514&utm_medium=email&utm_source=boub_mo&utm_term=0363
# https://zoek.officielebekendmakingen.nl/gmb-2021-393488.html
# per postcode 
# https://zoek.officielebekendmakingen.nl/resultaten?svel=Publicatiedatum&svol=Aflopend&pg=10&q=(c.product-area==%22officielepublicaties%22)and((((w.organisatietype==%22gemeente%22)and(dt.creator==%22Amsterdam%22))))and(((w.publicatienaam==%22Tractatenblad%22))or((w.publicatienaam==%22Staatsblad%22))or((w.publicatienaam==%22Staatscourant%22))or((w.publicatienaam==%22Gemeenteblad%22))or((w.publicatienaam==%22Provinciaal%20blad%22))or((w.publicatienaam==%22Waterschapsblad%22))or((w.publicatienaam==%22Blad%20gemeenschappelijke%20regeling%22)))and(cql.textAndIndexes=%221095hm%22)&zv=1095hm&col=AlleBekendmakingen&pagina=1

# https://aandeslagmetdeomgevingswet.nl/ontwikkelaarsportaal/api-register/api/uitvoeren-services/
# https://bagviewer.kadaster.nl/
# https://kadastralekaart.com/kaart/perceel/ASD19/W/7270
# https://www.wozwaardeloket.nl/
# https://opendata.cbs.nl/
# https://data.overheid.nl/
# https://www.energielabel.nl/woningen/zoek-je-energielabel/
# https://docs.3dbag.nl/en/
# https://omgevingswet.overheid.nl/
# 
# https://www.kadaster.nl/zakelijk/datasets/open-datasets
# https://zoek.officielebekendmakingen.nl/gmb-2021-393488.html

# https://data.amsterdam.nl/data/bouwdossiers/bouwdossier/SU29447/?center=52.359335%2C4.94151&zoom=14
# postcodes sumatra: 1095 JA; 1095 JB; 1095 HP; 1095 HK
# postcode molukken: 1095 BJ; 1095 HN; 1095 HM





## % 
#### PLOTTINGS #####
# plot histogram non-ymere ownership
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(data=appartementen_df, x="non-ymere from", ax=ax, discrete=True)
# rename 2016 xlabel to 1980-2016
ax.set_xticklabels(["", "1981-2016", "2018", "2021", "2022", "2023", "2024"]) #too hacky and hardcoded
# %%
jaar = 2024
gebouw_eigenaar_breukdeel = appartementen_df[["Gebouw", jaar, "Breukdeel"]].groupby(["Gebouw", jaar]).sum()
gebouw_eigenaar_breukdeel["aantal apartementen"] = appartementen_df[["Gebouw", jaar]].groupby("Gebouw").value_counts().sort_index().to_frame()
gebouw_eigenaar_breukdeel["Breukdeel percent van totaal"] = gebouw_eigenaar_breukdeel["Breukdeel"]/gebouw_eigenaar_breukdeel["Breukdeel"].sum()*100
gebouw_eigenaar_breukdeel["Breukdeel percent van gebouw"] = gebouw_eigenaar_breukdeel["Breukdeel"]/gebouw_eigenaar_breukdeel.groupby("Gebouw")["Breukdeel"].transform("sum")*100

# format as %
gebouw_eigenaar_breukdeel["Breukdeel percent van totaal"] = gebouw_eigenaar_breukdeel["Breukdeel percent van totaal"].map("{:.2f}%".format)
gebouw_eigenaar_breukdeel["Breukdeel percent van gebouw"] = gebouw_eigenaar_breukdeel["Breukdeel percent van gebouw"].map("{:.2f}%".format)
print(gebouw_eigenaar_breukdeel)
# %%

#Breukdeel increase per year non-ymere

non_ymere_from = appartementen_df["non-ymere from"].value_counts().sort_index()


print("Breukdeel niet-ymere per jaar")
for year in years:
    if year in [2017, 2019, 2020]:
        continue

    breukdeel = appartementen_df.loc[appartementen_df[year]=="Particulier", "Breukdeel"].sum()
    bruekdeel_perc = breukdeel / breukdeel_totaal * 100
    print(f"Tot {year}, Breukdeel {breukdeel}/{breukdeel_totaal}, aantal verkocht {non_ymere_from[year]} percentage: {bruekdeel_perc:.2f}%")

# %%
appartementen_df.loc[appartementen_df["Eigenaar"]=="Stichting Ymere", ["Eigenaar", "Breukdeel"]]
# %%



# %%
# interpolate percentage into the future
df = appartementen_df.groupby("non-ymere from").sum()["Breukdeel"].cumsum()
df = df.to_frame()
X = df.index.values.reshape(-1, 1)
y = df["Breukdeel"].values
model = LinearRegression()
model.fit(X, y)

years_to_interpolate = np.arange(2016, 2035)
interpolated_values = model.predict(years_to_interpolate.reshape(-1, 1))
interpolation_df = pd.DataFrame({'Year': years_to_interpolate, 'Predicted_Value': interpolated_values})
# convert breukdeel into percentage
interpolation_df["Predicted_Value"] = interpolation_df["Predicted_Value"]/breukdeel_totaal*100
df["Breukdeel"] = df["Breukdeel"]/breukdeel_totaal*100

# %%


# plot line graph for actual data and interpolated data

fig, ax = plt.subplots(figsize=(20, 10))
sns.lineplot(data=interpolation_df, x="Year", y="Predicted_Value", ax=ax, linestyle='--')
sns.lineplot(data=df, x="non-ymere from", y="Breukdeel", ax=ax)
ax.axhline(50, ls='--', color='r')
ax.axvline(2032, ls='--', color='r')
ax.set_title("Projectie breukdeel % niet-ymere eigenaren over jaren (2032 passeren wij 50%)")
ax.set_ylabel("Breukdeel %")
ax.set_xlabel("Jaar")
plt.show()
# %%

# for row in appartementen_df[["Eigenaar", "Breukdeel"]].iterrows():
#     print(row)
    
# %%
