import dash #DASHBOARD
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from textwrap import dedent

import dash_table
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd

import folium #MAP
from folium import plugins
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster

import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

#Files
from flask import Flask, send_from_directory
import os

import pandas as pd
import numpy as np

#PYTHON
from Classifier import DecreasePerformance
from sklearn.linear_model import  LassoLarsIC


UPLOAD_DIRECTORY = "files"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

#INICIALIZE
print(dcc.__version__) # 0.6.0 or above is required
external_stylesheets = [dbc.themes.BOOTSTRAP]
server = Flask(__name__)
app = dash.Dash(server=server,  meta_tags=[{"name": "viewport", "content": "width=device-width"}])
#server = app.server
app.title= "Predicción rendimiento escolar decreciente"

app.config.suppress_callback_exceptions = True


# ============================ METHODS ============================
# Por default: General
df = pd.read_csv('data/example_criteria_2.csv')
edo = pd.read_csv("data/estados.csv", encoding = 'latin-1')
#============================= LAYOUT =============================


# ============================ ELEMENTS ============================
table =  html.Div([
        dash_table.DataTable(
            style_data={'whiteSpace': 'normal'},
            css=[{
                'selector': '.dash-cell div.dash-cell-value',
                'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
            }],
            id='criteria_table',
            columns=[{"name": i, "id": i, } for i in df.columns],
            data = df.to_dict('records'),
            fixed_rows={ 'headers': True, 'data': 0 },
            #style_cell={'width': '100px'},
            style_cell_conditional=[
                {'if': {'column_id': 'Variable'},
                'width': '20%'},
                {'if': {'column_id': 'Coeficiente'},
                'width': '10%'},
                {'if': {'column_id': 'Descripcion'},
                'width': '40%'},
                {'if': {'column_id': 'Notas'},
                'width': '30%'},
            ],
            style_table={
            'height': '350px',
            #'width': "500px",
            #'overflowY': 'scroll',
            'border': 'thin lightgrey solid'
            },
            style_as_list_view=True,
            style_cell={'padding': '5px',
                    'height': 'auto',
                    # all three widths are needed
                    'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                    'whiteSpace': 'normal'},
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },     
          ),
           html.A('Descripción de variables', href="/download/variables.pdf"),
    ],  className="pretty_container five columns",)
    #style={'width': '49%', 'display': 'inline-block'}),

def markdown_popup():
    return html.Div(
        id="markdown",
        className="modal",
        style={"display": "none"},
        children=(
            html.Div(
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Cerrar",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=[
                            dcc.Markdown(
                                children=dedent(
                                    """
                                ##### Documentación                                
                                El proyecto se elaboró utilizando la metodología CRISP-DM. Para aprender más, consultar el [reporte final](https://github.com/paola-md/Tesis-Enlace/tree/master/analysis). 

                                #### Bases de datos 
                                ###### Originales
                                El desempeño academico se definió como resultados a nivel escuela del ENLACE. 
                                Las bases historicas están disponibles [aquí](http://www.enlace.sep.gob.mx/ba/resultados_anteriores).

                                Las características de las escuelas se obtuvieron del Censo de Escuelas,
                                Maestros y Alumnos de Educación Básica y Especial (disponible para descargar [aquí](http://cemabe.inegi.org.mx/)) y del Formato Estadístico 911
                                (disponible para descargar [aquí](https://www.dropbox.com/sh/h6gjchdww5d9js4/AADsEaVl6zTr0bwMogMxNw1Fa?dl=0)).

                                ###### Generadas
                                La tabla generada está disponible [aquí](https://drive.google.com/open?id=1YolynV1iNurMog-cruCtvzudhm6nYkV7) 
                                
                                #### Códigos 
                                ###### Del proyecto
                                El preprocesamiento de datos, integración de tablas y creación de nuevas variables se hizo en Stata. 
                                Mientras que el análisis de datos, selección de variables y modelos se implementaron en Python.
                                Para aprender más, visita el [repositorio del proyecto](https://github.com/paola-md/Tesis-Enlace/tree/master/code)     

                                ###### De la aplicación
                                Este aplicación utiliza el framework Dash de Python que estaba basado en Flask y React. 
                                Para aprender más, visita el [repositorio de la aplicación](https://github.com/paola-md/Tesis-Enlace/tree/master/deploy)

                                """
                                )
                            )
                        ],
                    ),
                ],
            )
        ),
    )


######################## START RESULTS ########################

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
)

app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("logo-ITAM.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Producto de datos para la toma de decisiones en programas sociales para escuelas primarias en México",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Predicción de rendimiento académico decreciente", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.Button("Más información", id="learn-more-button", n_clicks=0),
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "35px"},
        ),

        html.Div(
            [
                
                html.Div(
                    [
                     html.H5("Acerca del proyecto",
                    className="control_label"),   
                    html.P("El objetivo de la aplicación es proporcionar información para la toma de decisiones de politicas públicas y asignación de programas sociales educativos en primarias de México. La aplicación pretende responder la pregunta: ¿Cuáles escuelas primarias están en riesgo de bajar su rendimiento académico?. Asimismo, se pretende que el usuario tenga la flexibilidad de escoger los estados de interés y el tiempo a futuro. Un año hacia adelante predice el resultado en el corto plazo y tres años hacia adelante en el mediano plazo (medio sexenio).",
                    className="control_label"),                
                    html.H5("Así que, ¿cómo funciona?",
                    className="control_label"),
                    html.P("Al seleccionar estados y número de años a futuro, la aplicación identifica a las escuelas en riesgo de bajar su desempeño más de 0.2 desviciones estándar utilizando una regresión Bernoulli con liga logística." ,
                    className="control_label"),
                    ],  
                    className="pretty_container seven columns"),
                html.Div([
                html.P(
                    "Selecciona uno o más estados:",
                    className="control_label",
                ),   
                dcc.Dropdown(
                    id="estado_dropdown",
                    #options=edo.to_dict("records"),
                    value=1,
                    className="dcc_control",
                    multi=True,
                ),
                html.P(id="radioitems-checklist-output",
                        className="control_label"),

                html.P(
                    "Selecciona número de años hacia adelante",
                    className="control_label",
                ), 
                dcc.RadioItems(
                    id="tipoEscuela",
                    options=[
                        {"label": "1 año", "value": 1},
                        {"label": "2 años", "value": 2},
                        {"label": "3 años", "value": 3},
                    ],
                    value=1,
                    #labelStyle={"display": "inline-block"},
                    className="dcc_control",
                ),                
                html.P(
                    "",
                    className="control_label",
                ), 
                html.Button("Obtener resultados", id="button_envia", className="control_center"),

                  
                ], 
                className="pretty_container five columns"),

            ], 
            className="row flex-display",
            ),

        html.Div(
            [
                table,
                html.Div(
                    [html.Iframe(id = "map", srcDoc = open("mapas/mapa_base.html", 'r').read(), width=650, height=350)],
                     className="pretty_container seven columns",
                ),
                
            ],
            className="row flex-display",
        ),


        html.Div(
            [
                html.Div(
                    [html.H6(id="calif-escuela"), 
                    html.P("Resultados por escuela"),
                    html.A('Descargar', id='link_descarga',  href="/results/info.csv"), ],
                    id="wells",
                    className="mini_container",
                ),
                html.Div(
                    [html.H6(id="num_escuelas"), html.P("Número de escuelas en subconjunto")],
                    id="esc",
                    className="mini_container",
                ),
            ],
            id="info-container",
            className="row container-display",
        ),
         markdown_popup(),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)








#app.layout = layout_results

@app.callback(
    Output("fade", "is_in"),
    [Input("fade-button", "n_clicks")],
    [State("fade", "is_in")],
)
def toggle_fade(n, is_in):
    if not n:
        # Button has never been clicked
        return False
    return not is_in


@app.callback(
    [Output('criteria_table', "data"),
    Output("map", "srcDoc"),
    Output('link_descarga', "href"),
    Output('num_escuelas','children')],
    [Input('button_envia', "n_clicks")],
    [State('tipoEscuela', "value"),
     State("estado_dropdown", "value")])
def update_results(n_clicks, value_tipo, value_estados):
    """
    Actualiza la tabla y el mapa
    Obtiene los resultados con las especificaciones del usuario

    """
    if n_clicks is None:
        raise PreventUpdate
    else: 
        if value_estados == []:
            raise PreventUpdate

        if type(value_estados) == int:
            value_estados = [value_estados]
        lista_final = list(map(int, value_estados))
    
        tipo = value_tipo


        agent = DecreasePerformance()
        num_obs, nuevas_vars, df_cct  = agent.get_results(tipo,lista_final)

        criteria = nuevas_vars.to_dict('records')
     
        id_map = int(''.join(map(str,lista_final)))
        nombre_map = "mapas/mapa_"+ str(tipo) + "_" + str(id_map) + ".html"
        
        if os.path.isfile(nombre_map)==False:
            agent.get_map(df_cct, nombre_map)

        abre_mapa = open(nombre_map, 'r').read()
        
        #Guarda resultados
        nombre_rs = "files/risk_"+ str(tipo) + "_" + str(id_map) + ".csv"
        if os.path.isfile(nombre_rs)==False:
             df_cct.to_csv(nombre_rs, index=False)
        update_link = "/download/risk_"+ str(tipo) + "_" + str(id_map) + ".csv"

        num_escu = format(num_obs, ',')
        return criteria, abre_mapa, update_link, num_escu

@app.callback(
    Output("radioitems-checklist-output", "children"),
    [
        Input("estado_dropdown", "value"),
    ],
)
def on_form_change(n_drop):
    error = "Por favor, selecciona un estado."
    if n_drop == []:
        output_string = error
    else:
        output_string = ""

    return output_string


@app.callback(
    [Output('estado_dropdown', 'options')],
    [Input('tipoEscuela', 'value')]
)
def update_date_dropdown(tipo):
    if tipo == 3:
        edo = pd.read_csv("data/estados_ind.csv", encoding = 'latin-1')
    else:
        edo = pd.read_csv("data/estados.csv", encoding = 'latin-1')
    resp = [edo.to_dict("records")]
    return resp

@server.route("/download/<path:path>")
def download(path):
    if path == "info.csv":
        raise PreventUpdate
    else:
        return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


# Learn more popup
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context
    prop_id = ""
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if prop_id == "learn-more-button":
        return {"display": "block"}
    else:
        return {"display": "none"}


################################# MAIN ################################
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)