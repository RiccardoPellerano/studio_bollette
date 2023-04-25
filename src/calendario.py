import pandas as pd
import datetime as dt
import pathlib

def get_pandas_data(xlsx_filename: str,xlsx_sheet: str) -> pd.DataFrame:
   '''
   Load data from /data directory as a pandas DataFrame
   using relative paths. Relative paths are necessary for
   data loading to work in Heroku.
   '''
   PATH = pathlib.Path(__file__).parent
   DATA_PATH = PATH.joinpath("data").resolve()
   return pd.read_excel(DATA_PATH.joinpath(xlsx_filename),sheet_name=xlsx_sheet)

def h(giorno, ora):
    return dt.datetime.combine(giorno,ora)

def calendario(file, giorni_festivi):
    df_01 = get_pandas_data(file, sheet_name='Gennaio')
    df_02 = get_pandas_data(file, sheet_name='Febbraio')
    df_03 = get_pandas_data(file, sheet_name='Marzo')
    df_04 = get_pandas_data(file, sheet_name='Aprile')
    df_05 = get_pandas_data(file, sheet_name='Maggio')
    df_06 = get_pandas_data(file, sheet_name='Giugno')
    df_07 = get_pandas_data(file, sheet_name='Luglio')
    df_08 = get_pandas_data(file, sheet_name='Agosto')
    df_09 = get_pandas_data(file, sheet_name='Settembre')
    df_10 = get_pandas_data(file, sheet_name='Ottobre')
    df_11 = get_pandas_data(file, sheet_name='Novembre')
    df_12 = get_pandas_data(file, sheet_name='Dicembre')
    mesi = [df_01, df_02, df_03, df_04, df_05, df_06, df_07, df_08, df_09, df_10, df_11, df_12]
    
    df_bolletta = pd.concat(mesi, ignore_index=True)
    df_bolletta['Giorno'] = [i[0].upper() for i in df_bolletta['Data']]
    df_bolletta['Data'] = [dt.datetime.strptime(i[2:], '%d/%m/%Y').date() for i in df_bolletta['Data']]
    
    giorni_festivi = [dt.datetime.strptime(i, '%d/%m/%Y').date() for i in giorni_festivi]

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

    