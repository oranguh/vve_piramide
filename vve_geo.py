from itertools import cycle
import base64
import time

import plotly.graph_objects as go
import plotly.express as px
import rasterio
import branca

# from rasterio.plot import reshape_as_image
# from ipyleaflet import Map, basemaps, basemap_to_tiles, TileLayer, Marker
# import ipywidgets as widgets
from shapely.geometry import Point, shape

import geopandas as gpd
import folium
from folium.raster_layers import ImageOverlay

import seaborn as sns
import pandas as pd
import json

from general_data import PORTIEKEN, invert_dict, KOLOMMEN, DAKAANBOUW
from portieken_create import make_portiek_dataset

from keys_and_passwords import mapbox_api_key

def main():
    
    # https://deparkes.co.uk/2016/06/10/folium-map-tiles/
    # https://leaflet-extras.github.io/leaflet-providers/preview/
    # https://docs.mapbox.com/api/maps/styles/

    current_year = time.localtime().tm_year

    tileset_ID_str = "streets-v11"
    tilesize_pixels = "256"

    tilset_ID_str_sat = "satellite-streets-v12"


    tiles_mapbox = f"https://api.mapbox.com/styles/v1/mapbox/{tileset_ID_str}/tiles/{tilesize_pixels}/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_api_key}"
    attr_mapbox = "Mapbox attribution"

    tiles_mapbox_sat = f"https://api.mapbox.com/styles/v1/mapbox/{tilset_ID_str_sat}/tiles/{tilesize_pixels}/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_api_key}"

    attr_mapbox = "Mapbox attribution"

    tiles_sat = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    attr_sat = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'

    

    latest_year = "2023"

    # Open the GeoTIFF file
    tiff_path = f'geo_features/verdieping_0.tif'

    dataset = rasterio.open(tiff_path)

    # Get the bounding box coordinates
    gdf = gpd.GeoDataFrame(
        geometry=[Point(dataset.bounds.left, dataset.bounds.bottom), Point(dataset.bounds.right, dataset.bounds.top)],
        crs=f"EPSG:{dataset.crs.to_epsg()}",
    )
    # Create a Folium map centered around the bounding box
    map_center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]

    verdieping = 3

    # make_verdiepingen_html(map_center, tiles_sat, attr_sat, tiles_mapbox, attr_mapbox, tiles_mapbox_sat, dataset, verdieping, latest_year)

    # make_portieken_html(current_year, use_fiscal, merged, map_center, tiles_sat, attr_sat, tiles_mapbox, attr_mapbox, tiles_mapbox_sat, dataset)

    make_kolommen_html(current_year, map_center, tiles_sat, attr_sat, tiles_mapbox, attr_mapbox, tiles_mapbox_sat, dataset)

def make_verdiepingen_html(map_center, tiles_sat, attr_sat, tiles_mapbox, attr_mapbox, tiles_mapbox_sat, dataset, verdieping, latest_year):
    m = folium.Map(location=map_center, zoom_start=20, max_zoom = 25)

    sattelite = folium.TileLayer(tiles=tiles_sat, attr=attr_sat, name="Satellite")
    mapbox = folium.TileLayer(tiles=tiles_mapbox, attr=attr_mapbox, name="Mapbox")
    open_streetmap = folium.TileLayer('openstreetmap')
    mapbox_sattelite = folium.TileLayer(tiles=tiles_mapbox_sat, attr=attr_mapbox, name="Mapbox Satellite")

    sattelite.add_to(m)
    # mapbox.add_to(m)
    open_streetmap.add_to(m)
    # mapbox_sattelite.add_to(m)

    # Add the GeoTIFF as an image overlay
    image_overlay = ImageOverlay(
        image=dataset.read(1),  # Read the first band of the GeoTIFF
        # image=dataset.read(),
        # image=tiff_path,
        bounds=[(dataset.bounds.bottom, dataset.bounds.left), (dataset.bounds.top, dataset.bounds.right)],
        opacity=.6,
        colormap=lambda x: (x, x, x, x),  # Transparent colormap
        name="Plattegrond: BG"
    ).add_to(m)


    #TODO FIX THE PLATTEGRONDEN BOUNDS
    tiff_path = f'geo_features/verdieping_{verdieping}.tif'

    other_floor = rasterio.open(tiff_path)

    image_overlay = ImageOverlay(
        image=other_floor.read(1),  # Read the first band of the GeoTIFF
        # image=dataset.read(),
        # image=tiff_path,
        bounds=[(other_floor.bounds.bottom, other_floor.bounds.left), (other_floor.bounds.top, other_floor.bounds.right)],
        opacity=.6,
        colormap=lambda x: (x, x, x, x),  # Transparent colormap
        name=f"Plattegrond verdieping: {verdieping}"
    ).add_to(m)

    tiff_path_dakopbouw = f'geo_features/dakopbouw.tif'

    dakopbouw = rasterio.open(tiff_path_dakopbouw)

    # image_overlay = ImageOverlay(
    #     image=dakopbouw.read(1),  # Read the first band of the GeoTIFF
    #     # image=dataset.read(),
    #     # image=tiff_path,
    #     bounds=[(dakopbouw.bounds.bottom, dakopbouw.bounds.left), (dakopbouw.bounds.top, dakopbouw.bounds.right)],
    #     opacity=.9,
    #     colormap=lambda x: (x, x, x, x),  # Transparent colormap
    #     name=f"Plattegrond dakopbouw"
    # ).add_to(m)


    # TODO interactive plotting https://geopandas.org/en/stable/docs/user_guide/interactive_mapping.html

    # load the geometries of the apartments, created in QGIS manually
    apartment_polygons = None

    for verdieping_ in range(0, 5):
        print(verdieping_)
        goejson_filepath = f"geo_features/apartments_verdieping_{verdieping_}.geojson"
        geojson = gpd.read_file(goejson_filepath)
        if apartment_polygons is None:
            apartment_polygons = geojson
        else:
            apartment_polygons = apartment_polygons.merge(geojson, how="outer")
    apartment_polygons["Appartementsindex"] = apartment_polygons["id"].apply(lambda x: "A-" + str(x).zfill(3))
    apartment_polygons.set_index("Appartementsindex", inplace=True)


    df_complete = pd.read_excel("datasets/appartementen_df_complete.xlsx", index_col=0)

    df_complete.reset_index(inplace=True)
    df_complete.set_index("Appartementsindex", inplace=True, drop=False)
    df_complete.sort_index(inplace=True)

    apartment_polygons = apartment_polygons.merge(df_complete, left_index=True, right_index=True, how="left")
    apartment_polygons.sort_index(inplace=True)

    categorical_palette = cycle(sns.color_palette("Set1", n_colors=10).as_hex())

    gdf = apartment_polygons.loc[apartment_polygons["verdieping"] == verdieping].copy()
    # gdf["energielabel"] = gdf["energielabel"].fillna("Niet Aanwezig")
    for choropeth_var in ["WOZ_2022_per_m2"]:
        # choropeth_var = "WOZ_2021"
        # feature.id should be same as index. So have a duplicated column of index
        popup = folium.GeoJsonPopup(
            fields=["Appartement", "Bezit Ymere"],
            aliases=["Appartement: ", "Bezit Ymere"],
            localize=True,
            labels=True,
            style="background-color: yellow;",
            )

        tooltip = folium.GeoJsonTooltip(
            fields=["Appartement", f"WOZ_{latest_year}", f"WOZ_{latest_year}_per_m2", "Bezit Ymere"],
            aliases=["Appartement:", "WOZ:", "WOZ per m2:", "Bezit Ymere: "],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
            )
        colormap = branca.colormap.LinearColormap(
            vmin=apartment_polygons[choropeth_var].quantile(0.0),
            vmax=apartment_polygons[choropeth_var].quantile(1),
            colors=["red", "orange", "lightblue", "green", "darkgreen"],
            caption=choropeth_var,
        ).add_to(m)

        if False:
            g = folium.GeoJson(
                    gdf,
                    style_function=lambda x: {
                        "fillColor": colormap(x["properties"][choropeth_var])
                        if x["properties"][choropeth_var] is not None
                        else "transparent",
                        "color": "black",
                        "fillOpacity": 0.4,
                    },
                    tooltip=tooltip,
                    show=False,
                    # popup=popup,
                    name=f"Choropleth {choropeth_var}",
                ).add_to(m)

            # colormap.add_to(m)

        else:
            folium.Choropleth(
                geo_data=gdf,
                data=gdf,
                fill_color="YlGn",
                columns=["Appartement", choropeth_var],
                key_on="feature.properties.Appartement",
                name=f"Choropleth {choropeth_var}",
                legend_name=choropeth_var,
                use_jenks=(choropeth_var == f"WOZ_{latest_year}_per_m2"),
                show=False).add_to(m)


    fg = folium.FeatureGroup(name="Individual apartments")
    m.add_child(fg)
    for idx, row in apartment_polygons.iterrows():
        if row["verdieping"] == verdieping:
            pass
        else:
            continue
        color = next(categorical_palette)
        geo_j = folium.GeoJson(data=row["geometry"], 
                               style={"fillColor": color}, 
                               name=f"{row['Appartement']}", 
                               zoom_on_click=True,
                               control=False)
        
        html = f"""
        <h1> {row['Appartement']}</h1>
        <table>
            <tr>
                <td>WOZ-{latest_year}</td>
                <td>{row[f'WOZ_{latest_year}']} €</td>
            </tr>
            <tr>
                <td>WOZ_per_m2</td>
                <td>{row[f'WOZ_{latest_year}_per_m2']:.2f} €</td>
            </tr>
            <tr>
                <td>WWS</td>
                <td>{row['WWS']}</td>
            </tr>
            <tr>
                <td>Woonoppervlakte</td>
                <td>{row['oppervlakte']} m2</td>
            </tr>
            <tr>
                <td>Verdieping</td>
                <td>{row['verdieping']}</td>
            </tr>
            <tr>
                <td>Index</td>
                <td>{row['Appartementsindex']}</td>
            </tr>
            <tr>
                <td>Bezit Ymere</td>
                <td>{row['Bezit Ymere']}</td>
            </tr>
            <tr>
                <td>Energielabel</td>
                <td>{row['energielabel']}</td>
            </tr>
            <tr>
                <td>Postcode</td>
                <td>{row['postcode']}</td>
            </tr>
            <tr>
                <td>Breukdeel</td>
                <td>{row['Breukdeel']}</td>
            </tr>
            <tr>
                <td>Betaalt_voor_lift</td>
                <td>{row['Betaalt_voor_lift']}</td>
            </tr>
        </table>
        """


        iframe = branca.element.IFrame(html=html, width=500, height=300)
        folium.Popup(iframe, max_width=500).add_to(geo_j)
        geo_j.add_to(fg)#.add_to(m)


    #breukdeel bijdrage_kosten2nw_2023	bijdrage_liftnw_2023	bijdrage_kostennw_2023	Totale contributie 
    # Bezit Ymere postcode energielabel


    folium.LayerControl(collapsed=False).add_to(m)
    m.save(f"htmls/Pyramide_verdieping_{verdieping}.html")

def make_portieken_html(current_year, use_fiscal, merged, map_center, tiles_sat, attr_sat, tiles_mapbox, attr_mapbox, tiles_mapbox_sat, dataset):
    merged = pd.read_csv("datasets/klein_onderhoud_gekoppeld_met_verzoek.csv", index_col=0)

    #make portieken geo html. Combined with the reparations data, filtered by year

    # NOTE currently only works with years not with fiscal year
    # NOTE redo with fiscal year

    #fiscal years have the form jul-{year} - jun-{year+1}
    use_fiscal = True
    for year in list(range(2016, 2024)) + ["All_years"]:
        fiscal_year = f"jul-{year} - jun-{year+1}"
        
        goejson_filepath = f"geo_features/portieken.geojson"
        portieken_polygons = gpd.read_file(goejson_filepath)

        portieken = portieken_polygons[["name", "geometry"]].set_index("name")
        # NOTE portieken have the portieken as the index.

        # portieken_ = pd.read_csv("portieken_met_reparatie_ids.csv", index_col=0)
        if use_fiscal:
            portieken_ = make_portiek_dataset(years = [fiscal_year], current_year = current_year, use_fiscal=use_fiscal)
        else:
            portieken_ = make_portiek_dataset(years = [year], current_year = current_year)


        portieken = portieken.merge(portieken_, left_index=True, right_index=True, how="left")
        # portieken["geometry"] = portieken["Portiek"].apply(lambda x: portieken_polygons.loc[x, "geometry"] if x in portieken_polygons.index else None)

        portieken = portieken.loc[~portieken["Portiek"].isin(["Multiple portieken", "No portiek defined"])].copy()
        portieken

        m = folium.Map(location=map_center, zoom_start=19, max_zoom = 22)

        sattelite = folium.TileLayer(tiles=tiles_sat, attr=attr_sat, name="Satellite")
        mapbox = folium.TileLayer(tiles=tiles_mapbox, attr=attr_mapbox, name="Mapbox")
        open_streetmap = folium.TileLayer('openstreetmap')
        mapbox_sattelite = folium.TileLayer(tiles=tiles_mapbox_sat, attr=attr_mapbox, name="Mapbox Satellite")

        sattelite.add_to(m)
        # mapbox.add_to(m)
        open_streetmap.add_to(m)
        # mapbox_sattelite.add_to(m)

        # Add the GeoTIFF as an image overlay
        image_overlay = ImageOverlay(
            image=dataset.read(1),  # Read the first band of the GeoTIFF
            # image=dataset.read(),
            # image=tiff_path,
            bounds=[(dataset.bounds.bottom, dataset.bounds.left), (dataset.bounds.top, dataset.bounds.right)],
            opacity=.6,
            colormap=lambda x: (x, x, x, x),  # Transparent colormap
            name="Plattegrond: BG"
        ).add_to(m)




        fg = folium.FeatureGroup(name="Portieken info")
        m.add_child(fg)
        categorical_palette = cycle(sns.color_palette("Set1", n_colors=10).as_hex())

        for idx, row in portieken.iterrows():
            if row["Portiek"] in ["No portiek defined", "Multiple portieken"]:
                continue
            color = next(categorical_palette)
            geo_j = folium.GeoJson(data=row["geometry"], 
                                    style={"fillColor": color}, 
                                    name=f"{row['Portiek']}", 
                                    zoom_on_click=True,
                                    control=False)
            
            # NOTE portieken_reparaties have the repairs as index. So we can filter on the portiek and year if year is specified
            if use_fiscal:
                portiek_reparaties = merged.loc[(merged["boekjaar"] == fiscal_year) & (merged["Portiek"] == row["Portiek"]), :].copy()
            elif type(year) == int:
                portiek_reparaties = merged.loc[(merged["Jaar"] == year) & (merged["Portiek"] == row["Portiek"]), :].copy()
            else:
                portiek_reparaties = merged.loc[merged["Portiek"] == row["Portiek"], :].copy()

            #make pie chart of the reparatie tag costs
            fig = px.pie(portiek_reparaties, values='Debet', names='tag')
            fig.update_layout(
                legend=dict(
                    orientation="h",  # Set orientation to horizontal
                    yanchor="top",    # Anchor to the top
                    y=1.5            # Adjust the position vertically
                ),
                margin=dict(
                    l=0,  # Left margin
                    r=0,  # Right margin
                    t=50,  # Top margin
                    b=50   # Bottom margin
                ),
                autosize=True,  # Automatically resize the figure
                width=450,      # Set the width of the figure
                height=700,      # Set the height of the figure
            )


            # Convert the figure to a JSON string
            image_bytes = fig.to_image(format="png")

            # Encode the image as base64
            fig_base64 = base64.b64encode(image_bytes).decode()

            if use_fiscal:
                title = fiscal_year
            else:
                title = year
            html = f"""
            <h1> {title}</h1>
            <h1> {row['Portiek']}</h1>
            <img src="data:image/png;base64,{fig_base64}" style="margin-left: 0px;">
            <table>
                <tr>
                    <td>Reparatie counts</td>
                    <td>{row['Reparatie_counts']}</td>
                </tr>
                <tr>
                    <td>Reparatie kosten totaal</td>
                    <td>{row[f'reparatie_kosten_totaal']:.2f} €</td>
                </tr>
                <tr>
                    <td>Apartementen in portiek</td>
                    <td>{row['apartments']}</td>
                </tr>
                <tr>
                    <td>Totale oppervlakte portiek</td>
                    <td>{row['Totale_oppervlakte']:.0f} m2</td>
                </tr>
                <tr>
                    <td>Total breukdeel portiek</td>
                    <td>{row['Breukdeel_portiek']:.0f}</td>
                </tr>
                <tr>
                    <td>Aantal apartementen in portiek</td>
                    <td>{row['apartments_count']}</td>
                </tr>
                <tr>
                    <td>Aantal bezit Ymere</td>
                    <td>{row['Bezit_Ymere_count']}</td>
                </tr>
                <tr>
                    <td>Percentage bezit Ymere</td>
                    <td>{row['percentage_Ymere']:.0f}%</td>
                </tr>
                <tr>
                    <td>Totale WOZ {current_year-1}</td>
                    <td>{row[f'Totale_WOZ_{current_year-1}']:.0f} €</td>
                </tr>
                <tr>
                    <td>Gemiddelde WOZ {current_year-1}</td>
                    <td>{row[f'Gemiddelde_WOZ_{current_year-1}']:.2f} €</td>
                </tr>
                <tr>
                    <td>REPARATIE IDS</td>
                    <td>{row['reparatie_ids']}</td>
                </tr>
            </table>

            """

            iframe = branca.element.IFrame(html=html, width=500, height=700)
            folium.Popup(iframe, max_width=500, max_height=1000).add_to(geo_j)
            geo_j.add_to(fg)#.add_to(m)

        #Add chloropeths
        if True:
            # gdf["energielabel"] = gdf["energielabel"].fillna("Niet Aanwezig")
            # for choropeth_var in ["Reparatiekosten_per_breukdeel", "Reparatiekosten_per_appartement", "Reparatie_aantal_per_breukdeel", "Reparatie_aantal_per_appartement"]:
            for choropeth_var in ["Reparatiekosten_per_breukdeel"]:
            
                # choropeth_var = "WOZ_2021"
                # feature.id should be same as index. So have a duplicated column of index

                # popup = folium.Popup(iframe, max_width=500, max_height=1000)

                tooltip = folium.GeoJsonTooltip(
                    fields=["Portiek", f"Reparatiekosten_per_breukdeel", f"Reparatiekosten_per_appartement", "Reparatie_aantal_per_appartement", "percentage_Ymere", "Reparatie_counts", "apartments_count"],
                    aliases=["Portiek:", "Reparatiekosten per breukdeel:", "Reparatiekosten per appartement:", "Reparatie aantal per appartement: ", "percentage bezit Ymere: ", "Reparatie counts: ", "Aantal appartementen in portiek: "],
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                    """,
                    max_width=800,
                    )
                colormap = branca.colormap.LinearColormap(
                    vmin=portieken[choropeth_var].quantile(0.0),
                    vmax=portieken[choropeth_var].quantile(1),
                    # colors=["red", "orange", "lightblue", "green", "darkgreen"],
                    colors=["darkgreen", "lightblue", "yellow", "orange", "red"],
                    caption=choropeth_var,
                ).add_to(m)

                if True:
                    g = folium.GeoJson(
                            portieken,
                            style_function=lambda x: {
                                "fillColor": colormap(x["properties"][choropeth_var])
                                if x["properties"][choropeth_var] is not None
                                else "transparent",
                                "color": "black",
                                "fillOpacity": 0.4,
                            },
                            tooltip=tooltip,
                            show=False,
                            # popup=popup,
                            name=f"Choropleth {choropeth_var}",
                        ).add_to(m)



        folium.LayerControl(collapsed=False).add_to(m)
        m.save(f"htmls/portieken_{title}.html")

def make_kolommen_html(current_year, map_center, tiles_sat, attr_sat, tiles_mapbox, attr_mapbox, tiles_mapbox_sat, dataset):

    #make kolommen geo html. Combined with the reparations data, filtered by year
        
    kolommen_filepath = f"geo_features/apartments_verdieping_2.geojson" #just use second floor since it represents it the best
    kolommen_polygons = gpd.read_file(kolommen_filepath)

    kolommen = kolommen_polygons[["id", "geometry"]]
    # NOTE floor 2 has the floor 2 apt ids as the index. We will eventually change this to kolommen

    df_complete = pd.read_excel("datasets/appartementen_df_complete.xlsx", index_col=0)

    df_complete.reset_index(inplace=True)
    df_complete.set_index("Appartementsindex", inplace=True, drop=False)
    df_complete.sort_index(inplace=True)

    kolommen["Appartementsindex"] = kolommen["id"].apply(lambda x: "A-" + str(x).zfill(3))
    kolommen.set_index("Appartementsindex", inplace=True)

    kolommen = kolommen.merge(df_complete, left_index=True, right_index=True, how="left")
    kolommen.set_index("Kolom", inplace=True)
    kolommen.sort_index(inplace=True)

    # invert kolommen dict to get the apartments in the kolom. 
    KOLOMMEN_inverted = invert_dict(KOLOMMEN)

    kolommen["apartments_in_kolom"] = kolommen.index.map(KOLOMMEN_inverted)

    df_complete.set_index("Appartement", inplace=True, drop=False)

    m = folium.Map(location=map_center, zoom_start=19, max_zoom = 22)

    sattelite = folium.TileLayer(tiles=tiles_sat, attr=attr_sat, name="Satellite")
    mapbox = folium.TileLayer(tiles=tiles_mapbox, attr=attr_mapbox, name="Mapbox")
    open_streetmap = folium.TileLayer('openstreetmap')
    mapbox_sattelite = folium.TileLayer(tiles=tiles_mapbox_sat, attr=attr_mapbox, name="Mapbox Satellite")

    sattelite.add_to(m)
    # mapbox.add_to(m)
    open_streetmap.add_to(m)
    # mapbox_sattelite.add_to(m)

    # Add the GeoTIFF as an image overlay
    image_overlay = ImageOverlay(
        image=dataset.read(1),  # Read the first band of the GeoTIFF
        # image=dataset.read(),
        # image=tiff_path,
        bounds=[(dataset.bounds.bottom, dataset.bounds.left), (dataset.bounds.top, dataset.bounds.right)],
        opacity=.6,
        colormap=lambda x: (x, x, x, x),  # Transparent colormap
        name="Plattegrond: BG"
    ).add_to(m)


    fg = folium.FeatureGroup(name="Portieken info")
    m.add_child(fg)
    categorical_palette = cycle(sns.color_palette("Set1", n_colors=10).as_hex())

    for idx, row in kolommen.iterrows():

        color = next(categorical_palette)
        geo_j = folium.GeoJson(data=row["geometry"], 
                                style={"fillColor": color}, 
                                name=f"{idx}", 
                                zoom_on_click=True,
                                control=False)
        floor_0 = []
        floor_1 = []
        floor_2 = []
        floor_3 = []
        floor_4 = []
        dakaanbouw = []
        for apt in row['apartments_in_kolom']:
            if apt in df_complete.index:
                if df_complete.loc[apt, "Bezit Ymere"]:
                    apt_ = f"{apt} (Ymere)"
                else:
                    apt_ = apt
                if df_complete.loc[apt, "verdieping"] == 0:
                    floor_0.append(apt_)
                elif df_complete.loc[apt, "verdieping"] == 1:
                    floor_1.append(apt_)
                elif df_complete.loc[apt, "verdieping"] == 2:
                    floor_2.append(apt)
                elif df_complete.loc[apt, "verdieping"] == 3:
                    floor_3.append(apt_)
                elif df_complete.loc[apt, "verdieping"] == 4:
                    floor_4.append(apt_)
                
                if df_complete.loc[apt, "Dakaanbouw"]:
                    dakaanbouw.append(apt_)
        if len(floor_0) == 0:
            floor_0 = ["Berging"]
        floor_0 = ", ".join(floor_0)
        floor_1 = ", ".join(floor_1)
        floor_2 = ", ".join(floor_2)
        floor_3 = ", ".join(floor_3)
        floor_4 = ", ".join(floor_4)

        dakaanbouw = ", ".join(dakaanbouw)
        if len(floor_4) == 0:
            html = f"""
            <h1>Kolom {idx}</h1>
            <table>
                <tr>
                    <td>Begane grond:</td>
                    <td>{floor_0}</td>
                </tr>
                <tr>
                    <td>Verdieping 1:</td>
                    <td>{floor_1}</td>
                </tr>
                <tr>
                    <td>Verdieping 2:</td>
                    <td>{floor_2}</td>
                </tr>
                <tr>
                    <td>Verdieping 3:</td>
                    <td>{floor_3}</td>
                </tr>
                <tr>
                    <td>Dakopbouw:</td>
                    <td>{dakaanbouw}</td>
                </tr>
            </table>

            """
        else:
            html = f"""
            <h1>Kolom {idx}</h1>
            <table>
                <tr>
                    <td>Begane grond:</td>
                    <td>{floor_0}</td>
                </tr>
                <tr>
                    <td>Verdieping 1:</td>
                    <td>{floor_1}</td>
                </tr>
                <tr>
                    <td>Verdieping 2:</td>
                    <td>{floor_2}</td>
                </tr>
                <tr>
                    <td>Verdieping 3:</td>
                    <td>{floor_3}</td>
                </tr>
                <tr>
                    <td>Verdieping 4:</td>
                    <td>{floor_4}</td>
                </tr>
                <tr>
                    <td>Dakopbouw:</td>
                    <td>{dakaanbouw}</td>
                </tr>
            </table>
            
            """

        iframe = branca.element.IFrame(html=html, width=500, height=400)
        folium.Popup(iframe, max_width=500, max_height=400).add_to(geo_j)
        geo_j.add_to(fg)#.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    m.save(f"htmls/kolommen.html")
if __name__ == "__main__":
    main()