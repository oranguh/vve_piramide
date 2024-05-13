#%%
import ast

import pandas as pd
import seaborn as sns
import seaborn.objects as so
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt

# DEPRECATED NOW INSIDE SCRAPE TWINQ CODE

#%%

### Dataset containing all reparatieverzoeken. We can use this for many different things
# for example find out how many houses have been sold by ymere by looking at the FIRST mention of a repair
# request by a non-ymere owner for that particular house.

#%%
# load the data

df = pd.read_csv("datasets/VvE_piramide__Alle_Reparatieverzoeken_en_opdrachten.csv", sep=",", encoding="ISO-8859-1")

""" 
columns:

'Verzoek Sorted Descending', 'Omschrijving',
'Gemeld door', 'Type', 'Status', 'Datum', 'Opdracht',
'Appartementsrecht(en)', 'Eigenaar(s)'


1/04/2024: missing Gemeld door?

"""
# %%
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

print(df["appartement_simple"].unique())

# list of all unique addresses
# according to site: Naam volgens akte
# """
# Vereniging van Eigenaars van het gebouw Piramide, gelegen aan het 
# Sumatraplantsoen 20 t/m 38 (even nrs)
# Sumatrastraat 217 t/m 231 (oneven nrs)
# Tidorestraat 58 t/m 128 (even nrs)
# Molukkenstraat 411 t/m 545 (oneven nrs)
# """

# %%

#each apartment should get its own column

# Get unique tags from all rows

addresses = set(apartment for apartments in df['appartement_simple_list'] for apartment in apartments)

addresses = sorted(list(addresses))
# Create a new boolean column for each unique tag
for tag in addresses:
    df[tag] = df['appartement_simple_list'].apply(lambda tags: tag in tags)

df.head()


# %%

addresses

for y in addresses:
    print(y)

print(len(addresses))
# %%
# data_columns = ["Verzoek Sorted Descending", "Omschrijving", "Gemeld door", "Type", "Status"
#                 , "Datum", "Opdracht", "Appartementsrecht(en)", "Eigenaar(s)"]
# NOTE 'Gemeld door' has been removed in 2024?

data_columns = ["Verzoek Sorted Descending", "Omschrijving", "Type", "Status"
                , "Datum", "Opdracht", "Appartementsrecht(en)", "Eigenaar(s)"]

small = ["Datum"]
df.loc[df["Tidorestraat 94"]][data_columns]
# %%

df.loc[df["Eigenaar(s)"]=="M. Heuvelman"]
# %%

owners = df["Eigenaar(s)"].unique()
for owner in owners:
    print(owner)
    print()
    print(df.loc[df["Eigenaar(s)"]==owner][small])
    
# %%

df.loc[df["count of apartments in row"]==3][["appartement_simple_list", "Eigenaar(s)"]]
# %%
df["count of apartments in row"].unique()
# %%

df.loc[df["Verzoek Sorted Descending"]==63921]
# %%

df.to_csv("datasets/reparaties_link.csv")
# %%
