from dash import dcc, html, dash
from dash.dependencies import Input, Output, State
from simulation_functions import supply_chain_simulation
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import json
import io
import zipfile
import re

# Create the Dash app
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

#Create the date validator
date_pattern = r"^\d{4}-\d{2}-\d{2}$"

# Define the layout of the web application
app.layout = dbc.Container([
    html.H1("CTE Data Generation", className="my-4"),
    html.Div([
        dbc.Label('Business Entities Count'),
        dbc.Input(id='entityCount', type='number', value=500),
        dbc.FormText('Input how Business Entities will be in the Supply Chain')
]),
    html.Div([
        dbc.Label('Food Item Count'),
        dbc.Input(id='foodCount', type='number', value=10000),
        dbc.FormText('Input how Food Items will be simulated in the Supply Chain')
],
style={"margin-top": "20px"}),
    html.Div([
        dbc.Label('Simulation Start Date'),
        dbc.Input(id='startDate', type='text', value='2023-07-01', pattern=date_pattern),
        dbc.FormText('Must be in the format YYYY-MM-DD')
],
style={"margin-top": "20px"}),
    html.Div([
        dbc.Label('Simulation End Date'),
        dbc.Input(id='endDate', type='text', value='2023-07-30', pattern=date_pattern),
        dbc.FormText('Must be in the format YYYY-MM-DD')
],
style={"margin-top": "20px"}),
    html.Div([
        dbc.Label('Selected Food Traceability List Items'),
        dbc.Input(id='food_file', type='text', value='ftl_items.xlsx'),
        dbc.FormText('File for the Selected Foods')
],
style={"margin-top": "20px"}),
    dbc.Row(
        [dbc.Button('Run Simulation', id='run-button', n_clicks=0, class_name='my-4 text-center'),
        ]
    ),
    dbc.Spinner(html.Div(id='output'))
])

# Define the callback to run the simulation when the button is clicked, return the datatable div
@app.callback(
              Output('output', 'children'),
              Input('run-button', 'n_clicks'),
              Input('entityCount', 'value'),
              Input('foodCount', 'value'),
              Input('startDate', 'value'),
              Input('endDate', 'value'),
              Input('food_file', 'value'),
              progress=[Output('progress-bar','value'),Output('progress-bar','max')],
              prevent_initial_callback=True)
def run_simulation(n_clicks, entityCount, foodCount, startDate, endDate, food_file):
    if n_clicks > 0:
        # Convert input values to appropriate types if needed
        entityCount = int(entityCount)
        foodCount = int(foodCount)

        # Run the simulation
        result = supply_chain_simulation(
            entityCount=entityCount,
            foodCount=foodCount,
            startDate=startDate,
            endDate=endDate,
            food_file=food_file,
            create_csv=False,
        ).run_simulation()

        # Dropdown to select the dataframe
        tables = [
            dcc.Store(id='result-store', data=json.dumps({key: df.to_json(orient='split') for key, df in result.items()})),
            dbc.Row(
            [
                dbc.Col(
                        [dbc.Button("Download All Data", id="btn-download-all", color="primary", className="mr-2"),
                         dcc.Download(id="download-all"),
                        ],
                        width={"size": 3, "offset": 3},
                        className="my-2 text-center"
                        ),
                dbc.Col(
                    [dbc.Button("Download Present Table", id="btn-download-present", color="primary"),
                     dcc.Download(id="download-current")],
                    width={"size": 3},
                    className="my-2 text-center"
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='dataframe-dropdown',
                        options=[{'label': key, 'value': key} for key in result.keys()],
                        value=list(result.keys())[0],  # Set the initial value to the first dataframe key
                    ),
                    width={"size": 6, "offset": 3},
                    className="my-2",
                ),
            ]
        ),
            # Table to display the selected dataframe
            dbc.Row(
                [
                    dbc.Col(
                        dash_table.DataTable(
                            id='dataframe-table',
                            columns=[{'name': col, 'id': col} for col in result[list(result.keys())[0]].columns],
                            data=result[list(result.keys())[0]].to_dict('records'),
                            style_table={'overflowX': 'auto'},  # Add this style to enable horizontal scrolling
                            page_current=0,  # Set the initial page to 0 (the first page)
                            page_size=20,  # Number of rows per page
                            page_action='native',
                        ),
                        width={"size": 10, "offset": 1},
                        className="my-2",
                    ),
                ]
            )
        ]

        return tables

    return ''


#A Callback for updating the data table based on the drop down value
@app.callback(
    Output('dataframe-table', 'data'),
    Output('dataframe-table', 'columns'),
    Input('dataframe-dropdown', 'value'),
    State('result-store','data'),
    prevent_initial_callback=True
)
def update_data_table(selected_dataframe_key, result):
    result = {key: pd.read_json(df, orient='split') for key, df in json.loads(result).items()}
    selected_dataframe = result[selected_dataframe_key]
    columns = [{'name': col, 'id': col} for col in selected_dataframe.columns]
    data = selected_dataframe.to_dict('records')
    return data, columns

#Download current dataframe
@app.callback(
    Output('download-current','data'),
    Input('btn-download-present','n_clicks'),
    State('dataframe-dropdown','value'),
    State('result-store','data'),
    prevent_initial_callback=True
)
def download_table(clicks,table_name,data):
    if clicks > 0:
        result = {key: pd.read_json(df, orient='split') for key, df in json.loads(data).items()}
        df = result[table_name]
        return dcc.send_data_frame(df.to_csv,f'{table_name}.csv',index=False)
    
#Download all the files as a ZIP
@app.callback(
    Output("download-all", "data"),
    Input("btn-download-all", "n_clicks"),
    State("result-store", "data"),
    prevent_initial_callback=True
)
def download_all_data(n_clicks, serialized_result):
    if n_clicks > 0:

        result = {key: pd.read_json(df, orient='split') for key, df in json.loads(serialized_result).items()}

        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for key, df in result.items():
                csv_string = df.to_csv(index=False, encoding='utf-8')
                csv_bytes = csv_string.encode()
                zipf.writestr(key + ".csv", csv_bytes)

        # Get the ZIP file content and return it
        zip_content = zip_buffer.getvalue()
        zip_buffer.close()

        # Return the content and filename properties for dcc.Download
        return dcc.send_bytes(zip_content, "all_generated_data.zip")



if __name__ == '__main__':
    app.run_server(debug=True, host="localhost", port=8050)
