import numpy as np
import pandas as pd
import plotly.graph_objects as go

def recession_figure(df, title=None,  forecast_begin = None):
    
    cols = df.columns.tolist()
    x = cols[0]
    y = cols[1]
    df = df[df[x]>='1976-01-01']
 
    NBER_recessions = {'1': {'Begin': '1957-09-01', 'End': '1958-04-01'},
                       '2': {'Begin': '1960-05-01', 'End': '1961-02-01'},
                       '3': {'Begin': '1970-01-01', 'End': '1970-11-01'},
                       '4': {'Begin': '1973-12-01', 'End': '1975-03-01'},
                       '5': {'Begin': '1980-02-01', 'End': '1980-07-01'},
                       '6': {'Begin': '1981-08-01', 'End': '1982-11-01'},
                       '7': {'Begin': '1990-08-01', 'End': '1991-03-01'},
                       '8': {'Begin': '2001-04-01', 'End': '2001-11-01'},
                       '9': {'Begin': '2008-01-01', 'End': '2009-06-01'},
                       '10': {'Begin': '2020-03-01', 'End': '2020-04-01'}}
    def create_recession_dict(begin, end, min_y=0, max_y = 1):
        return dict(
                type="rect",
                xref="x",
                yref="y",
                x0=begin,
                y0=min_y,
                x1=end,
                y1=max_y,
                fillcolor="lightgray",
                opacity=1,
                line_width=0,
                layer="below"
            )
    
    
    def create_forecast_dict(begin, end, min_y=0, max_y = 1):
        return dict(
                type="rect",
                xref="x",
                yref="y",
                x0=begin,
                y0=min_y,
                x1=end,
                y1=max_y,
                fillcolor="lightblue",
                opacity=1,
                line_width=0,
                layer="below"
            )
    
    min_date =  df[x].min()
    y_min =df[[y]].min().values[0]
    y_max = df[[y]].max().values[0]
    
     

    y_min= np.floor(y_min/0.05)*0.05
    y_max= np.ceil(y_max/0.05)*0.05
    add_axis = 0.03*(y_max - y_min)
    
    recession_dicts = []
    for recession in NBER_recessions:
        begin_dt = NBER_recessions[recession]['Begin']
        end_dt = NBER_recessions[recession]['End']
        if min_date <= begin_dt:
            recession_dicts.append(create_recession_dict(begin_dt, end_dt,y_min-add_axis, y_max+add_axis))
            
    if forecast_begin is not None: 
        begin_dt = forecast_begin
        end_dt = df['Dates'].max()
        recession_dicts.append(create_forecast_dict(begin_dt, end_dt,y_min-add_axis, y_max+add_axis))        
    
    fig = go.Figure([go.Scatter(x=df[x], y=df[y])])
    fig.update_layout(shapes=recession_dicts)
    
    if title is None:
        fig.update_layout(title_text=y)
    else:
        fig.update_layout(title_text=title)

    # https://stackoverflow.com/questions/55704058/plotly-how-to-set-the-range-of-the-y-axis         

    fig.update_layout(yaxis_range=[y_min-add_axis, y_max+add_axis])
    return fig