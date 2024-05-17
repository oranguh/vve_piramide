#%%
import ast    
import time

import pandas as pd
import seaborn as sns
import seaborn.objects as so
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, callback, dash_table
from dash import jupyter_dash

from general_data import MOLUKKEN_GEBOUW, SUMATRAPLANTSOEN_GEBOUW, PORTIEKEN


# %%

kleinonderhoud = pd.read_csv("datasets/klein_onderhoud_link.csv", index_col=0)
total_kost_klein_onderhoud = kleinonderhoud["Factuurbedrag"].sum()

# pie chart tags
ax = kleinonderhoud["tag"].value_counts().plot(kind="pie", autopct='%1.1f%%', figsize=(20, 20))
ax.set_title(f"AANTAL klein onderhoudjes per tag over 2016-2024\nTotale kosten: €{total_kost_klein_onderhoud:.2f}")
# %%
# pie chart weighted by cost/Factuurbedrag
ax = kleinonderhoud.groupby(['tag']).sum().plot(kind='pie', y='Factuurbedrag', autopct='%1.1f%%', figsize=(20, 20), legend=False)
ax.set_title(f"KOSTEN klein onderhoudjes per tag over 2016-2024\nTotale kosten: €{total_kost_klein_onderhoud:.2f}")
# %%
kleinonderhoud[["Datum", "Factuurbedrag", "tag"]]
# %%
fig, ax = plt.subplots(figsize=(40, 20))
sns.barplot(data=kleinonderhoud, x="Jaar", y="Factuurbedrag", hue="tag", ax=ax)

# %%
# sum Factuurbedrag per tag per year and plot
year_tag_sum = kleinonderhoud.groupby(["Jaar", "tag"])["Factuurbedrag"].sum().reset_index()


so.Plot(year_tag_sum, x="Jaar", y="Factuurbedrag", color="tag").layout(size=(40, 20)).add(so.Bar(), so.Stack())

# fig, ax = plt.subplots(figsize=(40, 20))
# sns.barplot(data=year_tag_sum, x="Jaar", y="Factuurbedrag", hue="tag", ax=ax)

# %%
year_sum = kleinonderhoud.groupby(["Jaar"])["Factuurbedrag"].sum().reset_index()
fig, ax = plt.subplots(figsize=(40, 20))
sns.barplot(data=year_sum, x="Jaar", y="Factuurbedrag", ax=ax)

# %%


so.Plot(year_tag_sum, "Jaar", "Factuurbedrag", color="tag").add(so.Area(), so.Stack())#.add(so.Area(alpha=.7), so.Stack()))

# %%
sns.set_theme()
fig, ax = plt.subplots(figsize=(40, 20))
pt = pd.pivot_table(year_tag_sum, columns=['tag'], index=['Jaar'], values=['Factuurbedrag'], fill_value=0)
pt.columns = pt.columns.droplevel()
pt.plot.area(ax=ax, colormap="tab20c", alpha=.7)
plt.show()

# %%
fig, ax = plt.subplots(figsize=(40, 20))
pt.plot.bar(ax=ax, colormap="tab20c", alpha=.7, stacked=True)
plt.show()


merged = pd.read_csv("datasets/klein_onderhoud_gekoppeld_met_verzoek.csv", index_col=0)

# %%
# plot barchart x as year y as Factuurbedrag, hue as Building
fig, ax = plt.subplots(figsize=(40, 20))

year_building_sum = merged.groupby(["Jaar", "Building"])["Factuurbedrag"].sum().reset_index()
pt = pd.pivot_table(year_building_sum, columns=['Building'], index=['Jaar'], values=['Factuurbedrag'], fill_value=0)
pt.columns = pt.columns.droplevel()
pt.plot.bar(ax=ax, colormap="tab20c", alpha=.7, stacked=False)
plt.show()

# %%

#bruekdeel_sumatra: 6396
# breukdeel_molukken: 9111
# breukdeel totaal 15507

pt_norm = pt.copy()
pt_norm["Molukken"] = pt_norm["Molukken"]/9111
pt_norm["Plantsoen"] = pt_norm["Plantsoen"]/6396
pt_norm["No building defined"] = pt_norm["No building defined"]/15507

fig, ax = plt.subplots(figsize=(40, 20))
pt_norm.plot.bar(ax=ax, colormap="tab20c", alpha=.7, stacked=False)
plt.show()

# %%

year_tag_building_sum = merged.groupby(["boekjaar", "Jaar", "tag", "Building"])["Factuurbedrag"].sum().reset_index()

for building in ["Molukken", "Plantsoen", "No building defined"]:
    year_tag_building_sum_ = year_tag_building_sum.loc[year_tag_building_sum["Building"]==building, :]
    pt = pd.pivot_table(year_tag_building_sum_, columns=['tag'], index=['Jaar'], values=['Factuurbedrag'], fill_value=0)
    pt.columns = pt.columns.droplevel()

    fig, ax = plt.subplots(figsize=(40, 20))
    pt.plot.bar(ax=ax, colormap="tab20c", alpha=.7, stacked=True)
    ax.set_title(f"Gebouw: {building}")
    # fig.update_xaxes(type='category', categoryorder='array', categoryarray=sorted(year_tag_building_sum_['Jaar'].unique()))

    plt.show()


# %%
value = "Plantsoen"
year_tag_building_sum_ = year_tag_building_sum.loc[year_tag_building_sum["Building"]==value, :]
pt = pd.pivot_table(year_tag_building_sum_, columns=['tag'], index=['Jaar'], values=['Factuurbedrag'], fill_value=0)
pt.columns = pt.columns.droplevel()

fig = px.bar(year_tag_building_sum_, x='Jaar', y='Factuurbedrag', color="tag", hover_data=['tag', 'Building', 'Factuurbedrag', 'Jaar'])
fig.update_xaxes(type='category', categoryorder='array', categoryarray=sorted(year_tag_building_sum_['Jaar'].unique()))


# %%


merged = pd.read_csv("datasets/klein_onderhoud_gekoppeld_met_verzoek.csv", index_col=0)

jaar = "boekjaar"
# jaar = "Jaar"

year_tag_building_sum = merged.groupby([jaar, "tag", "Building"])["Debet"].agg(['sum', 'count']).reset_index()
year_tag_building_sum.rename(columns={"sum": "Debet"}, inplace=True)


app = dash.Dash(__name__)

# add html components and figure to app

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(["Molukken", "Plantsoen", "No building defined", "Building", "tag"], 'Building', id='building-dropdown'),
        html.H1(),
    ]),
    dcc.Loading(
        children=[dcc.Graph(figure=None, id="barplot-building")]
    )
])

@callback(
    Output('barplot-building', 'figure'),
    Input('building-dropdown', 'value')
)
def update_output(value):
    fig = create_reparatie_fig(year_tag_building_sum, value)
    return fig


# run app inline
# app.run(jupyter_mode='inline')
# app.run(jupyter_mode='tab')
app.run(jupyter_mode="external")



def create_reparatie_fig(year_tag_building_sum, value="Building", jaar="boekjaar"):
    if value in ["Building", "tag"]:
      year_tag_building_sum_ = year_tag_building_sum.copy()
      color = value
      fig = px.bar(year_tag_building_sum_, x=jaar, y='Debet', color=color, hover_data=['tag', 'Building', 'Debet', jaar, 'count'])

    else:
      year_tag_building_sum_ = year_tag_building_sum.loc[year_tag_building_sum["Building"]==value, :].copy()

      fig = px.bar(year_tag_building_sum_, x=jaar, y='Debet', color="tag", hover_data=['tag', 'Building', 'Debet', jaar, 'count'])
    # fig.update_xaxes(type='category', categoryorder='array', categoryarray=sorted(year_tag_building_sum_[jaar].unique()))
    
    # make x-axis ticks always visible, even with missing data
    
    fig.update_xaxes(
        type='category',
        categoryorder='array',
        categoryarray=sorted(year_tag_building_sum_[jaar].unique()),
        tickvals=list(range(len(sorted(year_tag_building_sum_[jaar].unique())))),
        ticktext=sorted(year_tag_building_sum_[jaar].unique())
        )

    return fig

# %%

merged = pd.read_csv("datasets/klein_onderhoud_gekoppeld_met_verzoek.csv", index_col=0)

jaar = "boekjaar"
# jaar = "Jaar"

year_tag_building_sum = merged.groupby([jaar, "tag", "Building"])["Debet"].agg(['sum', 'count']).reset_index()
year_tag_building_sum.rename(columns={"sum": "Debet"}, inplace=True)

for value in ["Molukken", "Plantsoen", "No building defined", "Building", "tag"]:
    fig = create_reparatie_fig(year_tag_building_sum, value=value, jaar="boekjaar")
    fig.write_html(f"htmls/reparaties_{value}.html")
    print(value)

# %%
