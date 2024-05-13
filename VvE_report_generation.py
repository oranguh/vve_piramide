import pandas as pd
import seaborn as sns
import seaborn.objects as so
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import ast    
import plotly.express as px
import plotly.graph_objects as go
import time
import pathlib

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak

from dash import jupyter_dash
import dash
from dash import dcc, html, Input, Output, State, callback, dash_table

from general_data import MOLUKKEN_GEBOUW, SUMATRAPLANTSOEN_GEBOUW, PORTIEKEN


def main():
    reparaties_df = pd.read_csv("datasets/klein_onderhoud_gekoppeld_met_verzoek.csv", index_col=0)
    apartment_df = pd.read_excel("datasets/appartementen_df_complete.xlsx", index_col=0)

    for portiek in apartment_df["Portiek"].unique():

        pathlib.Path('pdfs').mkdir(parents=True, exist_ok=True) 
        report_name = f"pdfs/{portiek}.pdf"
        portiek = portiek
        year = 2023
        create_pdf_report_portiek(report_name, portiek, reparaties_df, apartment_df, year)


def create_pdf_report_portiek(report_name: str, portiek: str, reparaties_df: pd.DataFrame, apartment_df: pd.DataFrame, year: int = None):

    if not year:
        year = "all years"

    if type(year) == int:
        boekjaar = f"jul-{year} - jun-2024" # NOTE note sure if we will use boekjaar or year... but this decision does matter.
        portiek_reparaties = reparaties_df.loc[(reparaties_df["Jaar"] == year) & (reparaties_df["Portiek"] == portiek), :].copy()
        apt_portiek_df = apartment_df.loc[apartment_df["Portiek"]==portiek].copy()
    else:
        portiek_reparaties = reparaties_df.loc[reparaties_df["Portiek"] == reparaties_df["Portiek"], :].copy()
        apt_portiek_df = apartment_df.copy()


    # doc = SimpleDocTemplate(report_name, pagesize=letter)
    doc = SimpleDocTemplate(report_name, pagesize=landscape(letter))

    styles = getSampleStyleSheet()

    # Title
    title_text = Paragraph(portiek, styles['Title'])
    # Add a spacer
    spacer = Spacer(1, 12)
    # Text

    
    percentage_van_totaal_apt = len(apt_portiek_df)/len(apartment_df)*100
    percentage_breukdeel = sum(apt_portiek_df["Breukdeel"])/sum(apartment_df["Breukdeel"])*100
    reparaties_aantal = len(portiek_reparaties)

    text_summary = [f"Aantal apartementen: {len(apt_portiek_df)} ({percentage_van_totaal_apt:.2f}%)"]
    text_summary += [f"\nPercentage Breukdeel: {percentage_breukdeel:.2f}%"]
    text_summary += [f"\nAantal reparaties in {year}: {len(portiek_reparaties)}"]
    text_summary += [f"\nKosten reparaties {year}: {sum(portiek_reparaties["Debet"])} €"]

    # breakpoint()

    text_summary = [Paragraph(x, styles['Normal']) for x in text_summary]
    # breakpoint()

    elements = [title_text, spacer, *text_summary, spacer]


    #make pie chart of the reparatie tag costs
    fig = px.pie(portiek_reparaties, values='Debet', names='tag')
    # fig.update_layout(
    #     legend=dict(
    #         orientation="h",  # Set orientation to horizontal
    #         yanchor="top",    # Anchor to the top
    #         y=1.5            # Adjust the position vertically
    #     ),
    #     margin=dict(
    #         l=0,  # Left margin
    #         r=0,  # Right margin
    #         t=50,  # Top margin
    #         b=50   # Bottom margin
    #     ),
    #     autosize=True,  # Automatically resize the figure
    #     width=450,      # Set the width of the figure
    #     height=700,      # Set the height of the figure
    # )
    elements = append_image_pdf(fig, elements)
    elements.append(PageBreak())


    ### TABLES ###

    # Table must be list of 
    apt_portiek_df.reset_index(inplace=True)

    rename_dict = {"Appartementsindex": "index",
                   "Tuin aanwezig": "Tuin",
                   "bijdrage_algnw_2023": "bijdrage breukdeel", 
                   "bijdrage_kostennw_2023": "bijdrage vast",
                   "bijdrage_kosten2nw_2023": "bijdrage geen lift",
                   "bijdrage_liftnw_2023": "bijdrage lift",
                   f"WOZ_{year}": "WOZ", 
                   f"WOZ_{year}_per_m2": "WOZ/m2"}

    apt_portiek_df.rename(columns=rename_dict, inplace=True)
    apt_portiek_df[f"WOZ/m2"] = apt_portiek_df[f"WOZ/m2"].round(2).astype(str)

    columns_to_show = ["Appartement", "index", "Breukdeel", "Bezit Ymere", "Tuin",
                       "postcode", "oppervlakte", f"WOZ", f"WOZ/m2"]
    

    table_data = [columns_to_show] + apt_portiek_df[columns_to_show].values.tolist()

    columns_to_show2 = ["Appartement", "bijdrage breukdeel", "bijdrage geen lift", 
                       "bijdrage lift", "bijdrage vast", 
                       "Totale contributie", "postcode",
                       "WWS", "energielabel"]
    
    table_data2 = [columns_to_show2] + apt_portiek_df[columns_to_show2].values.tolist()

    table_data = table_data + [[""]] + table_data2
    elements = append_table_pdf(table_data, elements)

    elements.append(PageBreak())


    ### REPARATIES DETAILS ###

    rename_dict = {"Appartementsindex": "index",
                "Tuin aanwezig": "Tuin",
                "bijdrage_algnw_2023": "bijdrage breukdeel", 
                "bijdrage_kostennw_2023": "bijdrage vast",
                "bijdrage_kosten2nw_2023": "bijdrage geen lift",
                "bijdrage_liftnw_2023": "bijdrage lift",
                f"WOZ_{year}": "WOZ", 
                f"WOZ_{year}_per_m2": "WOZ/m2"}

    apt_portiek_df.rename(columns=rename_dict, inplace=True)
    apt_portiek_df[f"WOZ/m2"] = apt_portiek_df[f"WOZ/m2"].round(2).astype(str)

    columns_to_show = ["Verzoeknummer", "Datum", "Omschrijving", "Debet", "boekjaar", "Opdracht/contract gegevens",
                       ]
    
    columns_to_show2 = ["Verzoeknummer", 
                    "Omschrijving_reparatie", "Opdracht", "Datum_reparatie", "Appartementsrecht(en)"]

    table_data = [columns_to_show] + portiek_reparaties[columns_to_show].values.tolist()
    table_data2 = [columns_to_show2] + portiek_reparaties[columns_to_show2].values.tolist()

    table_data = table_data + [[""]] + table_data2 
    elements = append_table_pdf(table_data, elements)

    doc.build(elements)

# test
def append_table_pdf(table_data, elements):
        spacer = Spacer(1, 12)
        table = Table(table_data)
        # Add style to the table
        # table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        #                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        #                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        #                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        #                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        #                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        #                            ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
        elements.append(spacer)

        return elements
def append_image_pdf(fig: go.Figure, elements):
    pathlib.Path('temp').mkdir(parents=True, exist_ok=True) 

    temp_image_path = "temp/pie.jpeg" 
    fig.write_image(temp_image_path)

    image = Image(temp_image_path, width=5*inch, height=3*inch)
    elements.append(image)
    return elements























if __name__ == "__main__":
    main()