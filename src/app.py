#Dashboard R-plug
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import os
import datetime as dt
import pathlib

bollette = ['BUPA_2022.csv','Serre_Morus.csv']
giorni_festivi2022 = [
    '01/01/2022',
    '06/01/2022',
    '17/04/2022',
    '18/04/2022',  
    '25/04/2022',   
    '01/05/2022',   
    '02/06/2022',   
    '15/08/2022', 
    '01/11/2022', 
    '08/12/2022',  
    '25/12/2022', 
    '26/12/2022'
]

def h(giorno, ora):
    return dt.datetime.combine(giorno,ora)
def get_pandas_data(csv_filename: str) -> pd.DataFrame:
   #'''
   #Load data from /data directory as a pandas DataFrame
   #using relative paths. Relative paths are necessary for
   #data loading to work in Heroku.
   #'''
   PATH = (pathlib.Path(__file__).parent).parent
   DATA_PATH = PATH.joinpath("data").resolve()
   return pd.read_csv(DATA_PATH.joinpath(csv_filename), sep =';')

def calendario(file, giorni_festivi):

    df_bolletta = get_pandas_data(file)
    df_bolletta['Giorno'] = [i[0].upper() for i in df_bolletta['Data']]
    df_bolletta['Alba'] = pd.to_datetime(df_bolletta['Alba'], format='%H:%M:%S').dt.time
    df_bolletta['Tramonto'] = pd.to_datetime(df_bolletta['Tramonto'], format='%H:%M:%S').dt.time
    df_bolletta['Ore_luce'] = pd.to_datetime(df_bolletta['Ore_luce'], format='%H:%M:%S').dt.time
    df_bolletta['Data'] = [dt.datetime.strptime(i[2:], '%d/%m/%Y').date() for i in df_bolletta['Data']]
    giorni_festivi = [dt.datetime.strptime(i, '%d/%m/%Y').date() for i in giorni_festivi2022]
    
    F1 = []
    F2 = []
    F3 = []

    F1_START = '08:00'
    F1_END = '19:00'

    F2_START = '07:00'
    F2_END = '08:00'

    F1_start = dt.datetime.strptime(F1_START, '%H:%M').time()
    F1_end = dt.datetime.strptime(F1_END, '%H:%M').time()

    F2_start = dt.datetime.strptime(F2_START, '%H:%M').time()
    F2_end =  dt.datetime.strptime(F2_END, '%H:%M').time()

    for index, row in df_bolletta.iterrows():
        if row['Giorno'] == 'D' or row['Data'] in giorni_festivi:
            F3.append(dt.timedelta(hours = row['Ore_luce'].hour, minutes = row['Ore_luce'].minute))
            F2.append(dt.timedelta(hours = 0, minutes = 0))
            F1.append(dt.timedelta(hours = 0, minutes = 0))

        elif row['Giorno'] == 'S' and row['Data'] not in giorni_festivi:
            F1.append(dt.timedelta(hours = 0, minutes = 0))
            if row['Alba'] < F2_start:
                F3.append(h(row['Data'],F2_start) - h(row['Data'],row['Alba']))
                F2.append(dt.timedelta(hours = row['Ore_luce'].hour, minutes = row['Ore_luce'].minute) - (h(row['Data'],F2_start) - h(row['Data'],row['Alba'])))
            else:
                F3.append(dt.timedelta(hours = 0, minutes = 0))
                F2.append(dt.timedelta(hours = row['Ore_luce'].hour, minutes = row['Ore_luce'].minute))
    
        elif row['Giorno'] in ['L','M','G','V'] and row['Data'] not in giorni_festivi:
            if row['Alba'] <= F2_start:
                F3.append(h(row['Data'],F2_start) - h(row['Data'],row['Alba']))
                if row['Tramonto'] < F1_end:
                    F2.append(h(row['Data'],F2_end) - h(row['Data'],F2_start))
                    F1.append(h(row['Data'],row['Tramonto']) - h(row['Data'],F1_start))
                else:
                    F2.append((h(row['Data'],F2_end) - h(row['Data'],F2_start)) + (h(row['Data'],row['Tramonto']) - h(row['Data'],F1_end)))
                    F1.append(h(row['Data'],F1_end) - h(row['Data'],F1_start))
            elif F2_start < row['Alba'] < F1_start:
                F3.append(dt.timedelta(hours = 0, minutes = 0))
                if row['Tramonto'] < F1_end:
                    F2.append(h(row['Data'],F2_end)- h(row['Data'],row['Alba']))
                    F1.append(h(row['Data'],row['Tramonto']) - h(row['Data'],F1_start))
                else:
                    F2.append((h(row['Data'],F2_end) - h(row['Data'],row['Alba'])) + (h(row['Data'],row['Tramonto']) - h(row['Data'],F1_end)))
                    F1.append(h(row['Data'],F1_end) - h(row['Data'],F1_start))
            elif row['Alba'] >= F1_start:
                F3.append(dt.timedelta(hours = 0, minutes = 0))
                if row['Tramonto'] < F1_end:
                    F2.append(dt.timedelta(hours = 0, minutes = 0))
                    F1.append(dt.timedelta(hours = row['Ore_luce'].hour, minutes = row['Ore_luce'].minute))
                else:
                    F2.append(h(row['Data'],row['Tramonto']) - h(row['Data'],F1_end))
                    F1.append(h(row['Data'],F1_end) - h(row['Data'],row['Alba']))
    
    df_bolletta['F1'] = F1
    df_bolletta['F2'] = F2
    df_bolletta['F3'] = F3

    F1_ore_totali = []
    F2_ore_totali = []
    F3_ore_totali = []
    for index, row in df_bolletta.iterrows():
        if row['Giorno'] == 'D' or row['Data'] in giorni_festivi:
            F3_ore_totali.append(dt.timedelta(days=0, hours=24, minutes=0))
            F2_ore_totali.append(dt.timedelta(days=0, hours=0, minutes=0))
            F1_ore_totali.append(dt.timedelta(days=0, hours=0, minutes=0))

        elif row['Giorno'] == 'S' and row['Data'] not in giorni_festivi:
            F3_ore_totali.append(dt.timedelta(days=0, hours=8, minutes=0))
            F2_ore_totali.append(dt.timedelta(days=0, hours=16, minutes=0))
            F1_ore_totali.append(dt.timedelta(days=0, hours=0, minutes=0))
        
        elif row['Giorno'] in ['L','M','G','V'] and row['Data'] not in giorni_festivi:
            F3_ore_totali.append(dt.timedelta(days=0, hours=8, minutes=0))
            F2_ore_totali.append(dt.timedelta(days=0, hours=5, minutes=0))
            F1_ore_totali.append(dt.timedelta(days=0, hours=11, minutes=0))

    df_bolletta['F1_ore_totali'] = F1_ore_totali
    df_bolletta['F2_ore_totali'] = F2_ore_totali
    df_bolletta['F3_ore_totali'] = F3_ore_totali
    
    df_bolletta['Data'] = pd.to_datetime(df_bolletta['Data'])

    return df_bolletta

#creiamo un applicazione web con stile bootstrap
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}])

server = app.server


#definiamo il layout dell'applicazione web
app.layout = html.Div([
    dbc.Container([
        dbc.Row([ #definiamo una riga
            dbc.Col([  #definiamo una colonna
                html.H1('Analisi Consumi e Copertura fotovoltaico', #titolo
                    className='text-center', #classe che contiene uno stile
                    style={'color':'white', 'font-family':'--tds-font-family--combined','font-weight': '--tds-heading--font-weight'}
                ), # colore del titolo e font
            ])
        ]),
        dbc.Row([ 
            dbc.Col([  
                html.H4("Seleziona l'abitazione",style={'color':'white','font-family':'--tds-font-family--combined','font-weight': '--tds-heading--font-weight'}),
                dcc.Dropdown(options = [{'label': i, 'value': i} for i in bollette], value='Serre_Morus.csv', id = 'bollette', style ={'width' :'400px','font-family':'--tds-font-family--combined','font-weight': '--tds-heading--font-weight'}),
            ])
        ]),
        dbc.Row([ 
            dbc.Col([  
                dcc.Graph(id='Copertuta'),
            ]),
        ]),
        dbc.Row([ 
            dbc.Col([ 
                dcc.Graph(id='Consumi')
            ])
        ]),
    ])
],style={'background-color':'#000000',
         'background-size': '50%',
         'height':'105h'
        })

@app.callback(
    Output('Copertuta', 'figure'),
    Output('Consumi', 'figure'),
    Input("bollette", "value"),
)

def mappa(bollette):

    consumi = get_pandas_data(bollette)

    df_bolletta_2022 = calendario('Ore_luce_2022.csv', giorni_festivi2022)
    
    mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
    mesi1=[0,1,2,3,4,5,6,7,8,9,10,11]

    Ore_f1 = [round(df_bolletta_2022.loc[df_bolletta_2022['Data'].dt.month==i]['F1_ore_totali'].sum()/dt.timedelta(hours=1),2) for i in range(1,13)]
    Ore_luce_f1 = [round(df_bolletta_2022.loc[df_bolletta_2022['Data'].dt.month==i]['F1'].sum()/dt.timedelta(hours=1),2) for i in range(1,13)]
    consumi_compensabili_f1 =[round((consumi['F1'][i] /  Ore_f1[i]) * Ore_luce_f1[i],2) for i in mesi1]

    Ore_f2 = [round(df_bolletta_2022.loc[df_bolletta_2022['Data'].dt.month==i]['F2_ore_totali'].sum()/dt.timedelta(hours=1),2) for i in range(1,13)]
    Ore_luce_f2 = [round(df_bolletta_2022.loc[df_bolletta_2022['Data'].dt.month==i]['F2'].sum()/dt.timedelta(hours=1),2) for i in range(1,13)]
    consumi_compensabili_f2 =[round((consumi['F2'][i] /  Ore_f2[i]) * Ore_luce_f2[i],2) for i in mesi1]

    Ore_f3 = [round(df_bolletta_2022.loc[df_bolletta_2022['Data'].dt.month==i]['F3_ore_totali'].sum()/dt.timedelta(hours=1),2) for i in range(1,13)]
    Ore_luce_f3 = [round(df_bolletta_2022.loc[df_bolletta_2022['Data'].dt.month==i]['F3'].sum()/dt.timedelta(hours=1),2) for i in range(1,13)]
    consumi_compensabili_f3 =[round((consumi['F3'][i] /  Ore_f3[i]) * Ore_luce_f3[i],2) for i in mesi1]

    labels = [
    'total',
    'Gennaio',  'F1_01','F2_01','F3_01',   'F1_01_C', 'F2_01_C', 'F3_01_C',
    'Febbraio', 'F1_02','F2_02','F3_02',   'F1_02_C', 'F2_02_C', 'F3_02_C',
    'Marzo',    'F1_03','F2_03','F3_03',   'F1_03_C', 'F2_03_C', 'F3_03_C',
    'Aprile',   'F1_04','F2_04','F3_04',   'F1_04_C', 'F2_04_C', 'F3_04_C',
    'Maggio',   'F1_05','F2_05','F3_05',   'F1_05_C', 'F2_05_C', 'F3_05_C',
    'Giugno',   'F1_06','F2_06','F3_06',   'F1_06_C', 'F2_06_C', 'F3_06_C',
    'Luglio',   'F1_07','F2_07','F3_07',   'F1_07_C', 'F2_07_C', 'F3_07_C',
    'Agosto',   'F1_08','F2_08','F3_08',  'F1_08_C', 'F2_08_C', 'F3_08_C',
    'Settembre','F1_09','F2_09','F3_09',   'F1_09_C', 'F2_09_C', 'F3_09_C',
    'Ottobre',  'F1_10','F2_10','F3_10',   'F1_10_C', 'F2_10_C', 'F3_10_C',
    'Novembre', 'F1_11','F2_11','F3_11',   'F1_11_C', 'F2_11_C', 'F3_11_C',
    'Dicembre', 'F1_12','F2_12','F3_12',   'F1_12_C', 'F2_12_C', 'F3_12_C',
    ]
    parents=['',
    'total',  'Gennaio','Gennaio','Gennaio',      'F1_01','F2_01','F3_01',
    'total',  'Febbraio','Febbraio','Febbraio',   'F1_02','F2_02','F3_02',
    'total',  'Marzo', 'Marzo', 'Marzo',          'F1_03','F2_03','F3_03',
    'total',  'Aprile','Aprile','Aprile',         'F1_04','F2_04','F3_04',
    'total',  'Maggio','Maggio','Maggio',         'F1_05','F2_05','F3_05', 
    'total',  'Giugno','Giugno','Giugno',         'F1_06','F2_06','F3_06',
    'total',  'Luglio','Luglio','Luglio',         'F1_07','F2_07','F3_07', 
    'total',  'Agosto','Agosto','Agosto',         'F1_08','F2_08','F3_08',
    'total',  'Settembre','Settembre','Settembre','F1_09','F2_09','F3_09',
    'total',  'Ottobre','Ottobre','Ottobre',      'F1_10','F2_10','F3_10', 
    'total',  'Novembre','Novembre','Novembre',   'F1_11','F2_11','F3_11', 
    'total',  'Dicembre','Dicembre','Dicembre',   'F1_12','F2_12','F3_12'
    ]
    consumi_mesi = [consumi['F1'][i]+consumi['F2'][i]+consumi['F3'][i] for i in range(0,12)]
    values = []
    for j in [[
        consumi_mesi[i],
        consumi['F1'][i],
        consumi['F2'][i],
        consumi['F3'][i],
        consumi_compensabili_f1[i],
        consumi_compensabili_f2[i],
        consumi_compensabili_f3[i]] for i in range(0,12)]:
        values.extend(j)
    values = [sum(consumi_mesi)] + values
    color = []
    for j in  [[
        ((consumi_compensabili_f1[i]+consumi_compensabili_f2[i]+consumi_compensabili_f3[i])/consumi_mesi[i])*100,
        (consumi_compensabili_f1[i]/consumi['F1'][i])*100,
        (consumi_compensabili_f2[i]/consumi['F2'][i])*100,
        (consumi_compensabili_f3[i]/consumi['F3'][i])*100,
        (consumi_compensabili_f1[i]/consumi['F1'][i])*100,
        (consumi_compensabili_f2[i]/consumi['F2'][i])*100,
        (consumi_compensabili_f3[i]/consumi['F3'][i])*100] for i in range(0,12)]:
        color.extend(j)
    color = [(sum(consumi_compensabili_f1+consumi_compensabili_f2+consumi_compensabili_f3)/sum(consumi_mesi))*100] + color

    fig1 = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues='total',
        marker=dict(
            colors=color,
            colorscale='RdYlGn',
            cmid = 50,
            showscale = True,
            colorbar= dict(
                title = 'Ratio',
                titlefont_color ='#ffffff',
                tickvals = [0, 50, 100],
                ticktext = ['low', 'middle', 'high'],
                nticks = 3,
                tickcolor='#ffffff',
                tickfont_color = '#ffffff',
                x = 0.8      
            ),   
        ),
        sort = False,
        hovertemplate='<b>%{label} </b> <br> kWh: %{value}</b> <br> Copertura: %{color:.2f}%',
        name='',
        textfont_color='#000000',
    ))

    fig1.update_layout(
        margin = dict(t=0, l=0, r=0, b=20, pad=0),
        height = 500,
        hoverlabel_font =dict(
            color="#000000",
            size=15
        ),
        paper_bgcolor  = '#000000',
    )

    fig1.update_xaxes(
        color='#ffffff',
        linecolor='#ffffff',
    )
    
    fig2 = go.Figure(
        data=[
        go.Bar(name='F1', x=mesi, y=consumi['F1'], hovertemplate= "consumo: %{y}"),
        go.Bar(name='F2', x=mesi, y=consumi['F2'], hovertemplate= "consumo: %{y}"),
        go.Bar(name='F3', x=mesi, y=consumi['F3'], hovertemplate= "consumo: %{y}")
        ])
    
    fig2.update_layout(
        xaxis_title="Mesi",
        yaxis_title="Consumi",
        yaxis_ticksuffix = ' kWh ',
        hoverlabel_font =dict(
            color="#ffffff",
            size=15
        ),
        margin = dict(t=0, l=0, r=0, b=0),
        paper_bgcolor  = '#000000',
        plot_bgcolor  = '#000000',
        legend=dict(
            title="Fasce",
            y=0.5,
            x=1,
            font=dict(

                color="#ffffff"
            )
        ),        
    )
    
    fig2.update_xaxes(color='#ffffff',
                      mirror=True,
                      gridcolor='#000000'
    )
    
    fig2.update_yaxes(color='#ffffff', 
                      gridcolor='#ffffff'
    )
    
    return fig1, fig2

    
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader = False)
