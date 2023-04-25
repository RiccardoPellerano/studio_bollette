#Dashboard R-plug
from calendario import calendario
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import os
import datetime as dt

bollette = ['BUPA_2022','Cagliari_3piano', 'Cagliari_5piano', 'Villasimius_Serre_Morus']

#creiamo un applicazione web con stile bootstrap
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}])

server = app.server

#os.chdir('..')
#print(os.getcwd()) # dice in quale directory ci troviamo
#os.chdir('data')

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
                dcc.Dropdown(options = [{'label': i, 'value': i} for i in bollette],value='BUPA_2022', id = 'bollette', style ={'width' :'400px','font-family':'--tds-font-family--combined','font-weight': '--tds-heading--font-weight'}),
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
    consumi = pd.read_excel('Bollette.xlsx', sheet_name=bollette)
    df_bolletta_2022 = calendario('Ore_luce_2022.xlsx', giorni_festivi2022)
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
    'Agosto',    'F1_08','F2_08','F3_08',  'F1_08_C', 'F2_08_C', 'F3_08_C',
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
