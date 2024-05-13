import pandas as pd
import seaborn as sns
import seaborn.objects as so
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import ast    
import plotly.express as px
import plotly.graph_objects as go
import time

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from dash import jupyter_dash
import dash
from dash import dcc, html, Input, Output, State, callback, dash_table

from general_data import MOLUKKEN_GEBOUW, SUMATRAPLANTSOEN_GEBOUW, PORTIEKEN


def create_pdf_report_portiek(report_name: str, portiek: str, reparaties_df: pd.DataFrame, apartment_df: pd.DataFrame, year: int = None):

    if not year:
        year = "all years"

    if type(year) == int:
        portiek_reparaties = reparaties_df.loc[(reparaties_df["Jaar"] == year) & (reparaties_df["Portiek"] == portiek), :].copy()
    else:
        portiek_reparaties = reparaties_df.loc[reparaties_df["Portiek"] == reparaties_df["Portiek"], :].copy()

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

    doc = SimpleDocTemplate(report_name, pagesize=letter)
    # doc = SimpleDocTemplate(report_name, pagesize=landscape(letter))

    styles = getSampleStyleSheet()

    # Title
    title_text = Paragraph(portiek, styles['Title'])
    # Text
    text_content = Paragraph(portiek, styles['Normal'])
    # Add a spacer
    spacer = Spacer(1, 12)
    elements = [title_text, spacer, text_content, spacer]

    # Table
    if table_data:
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

    # Figure
    if figure_path:
        from reportlab.lib.units import inch
        from reportlab.platypus import Image
        image = Image(figure_path, width=5*inch, height=3*inch)
        elements.append(image)

    doc.build(elements)

# test
def main():
    pass























if __name__ == "__main__":
    main()