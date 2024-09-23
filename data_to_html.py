import pandas as pd

def main():
    df_apts = pd.read_excel("datasets/appartementen_df_complete.xlsx", index_col=0)
    df_apts.reset_index(inplace=True)
    df_apts.drop(columns=["Eigenaar", "Appartementsrecht", "Vanaf", "Stemmen"], inplace=True)
    df_apts.insert(3, 'oppervlakte', df_apts.pop('oppervlakte'))
    title_apts = "Apartementen informatie"
    filename_apts = "htmls/table_appartementen.html"

    df_reparaties = pd.read_csv("datasets/klein_onderhoud_gekoppeld_met_verzoek.csv", index_col=0)
    df_reparaties.reset_index(inplace=True)
    title_reparaties = "Reparaties VvE de Piramide"

    filename_reparaties = "htmls/table_reparaties.html"

    # create_html_from_table(df_apts, title_apts, filename_apts)
    create_html_from_table(df_reparaties, title_reparaties, filename_reparaties)

def create_html_from_table(df, title, filename):
    html_table = df.to_html(index=False, classes='display', table_id='data_table')

    html_page = f"""
    <html>
    <head>
        <title>{title}</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/fixedheader/3.1.9/css/fixedHeader.dataTables.min.css">
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                margin: 20px;
            }}
            h1 {{
                text-align: center;
                margin-bottom: 20px;
            }}
            table.dataTable {{
                width: 80%;
                margin: 0 auto;
                border-collapse: collapse;
            }}
            th {{
                font-size: 1.2em;
                font-weight: bold;
                background-color: #343a40;
                color: #fff;
                padding: 10px;
                text-align: left;
            }}
            th input {{
                width: 100%;
                box-sizing: border-box;
                padding: 5px;
                margin-top: 5px;
                font-size: 0.9em;
            }}
            td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            .dataTables_wrapper .dataTables_filter {{
                text-align: right;
            }}
            .dataTables_wrapper .dataTables_paginate .paginate_button {{
                padding: 0.5em 1em;
                margin-left: 0.2em;
                border-radius: 0.2em;
                border: 1px solid transparent;
            }}
            .dataTables_wrapper .dataTables_paginate .paginate_button:hover {{
                border: 1px solid #343a40;
                background-color: #f8f9fa;
            }}
        </style>
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/fixedheader/3.1.9/js/dataTables.fixedHeader.min.js"></script>
        <script>
            $(document).ready(function() {{
                // Setup - add a text input to each header cell
                $('#data_table thead th').each(function() {{
                    var title = $(this).text();
                    $(this).html(title + '<br><input type="text" placeholder="Search '+title+'" />');
                }});

                // DataTable
                var table = $('#data_table').DataTable({{
                    "pagingType": "simple",
                    "language": {{
                        "paginate": {{
                            "previous": "<i class='fa fa-chevron-left'></i>",
                            "next": "<i class='fa fa-chevron-right'></i>"
                        }}
                    }},
                    "fixedHeader": true,
                }});

                // Apply the search
                table.columns().every(function() {{
                    var that = this;

                    $('input', this.header()).on('keyup change clear', function() {{
                        if (that.search() !== this.value) {{
                            that
                                .search(this.value)
                                .draw();
                        }}
                    }});
                }});
            }});
        </script>
    </head>
    <body>
        <h1>{title}</h1>
        {html_table}
    </body>
    </html>
    """


    with open(filename, 'w', encoding="utf-8") as file:
        file.write(html_page)


if __name__ == '__main__':

    main()