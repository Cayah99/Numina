import sqlite3 as sql
from os.path import dirname, join

import numpy as np
import pandas.io.sql as psql
import pandas as pd

from bokeh.io import curdoc, output_notebook
from bokeh.layouts import column, row
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import layout
from bokeh.models.widgets import Panel, Tabs, Paragraph, PreText
from bokeh.models import (Div, Button, CategoricalColorMapper, ColumnDataSource, Slider, Select,  TextInput, LinearAxis, Range1d, CustomJS, RadioButtonGroup,
                          HoverTool, Label, SingleIntervalTicker, Slider,LinearColorMapper, MultiSelect, CheckboxButtonGroup, CheckboxGroup, RangeSlider)

import datetime
import warnings
warnings.filterwarnings('ignore')
output_notebook()

numina_data = pd.read_csv('numina&weather_data.csv')
numina_data = numina_data.drop(['Unnamed: 0', 'weekday', 'month', 'YYYYMMDD'], axis=1)
numina_data['time'] = pd.to_datetime(numina_data['time'])
numina_data['Average_windspeed'] = numina_data['Average_windspeed']*0.1
numina_data['Average_temperature'] = numina_data['Average_temperature']*0.1
numina_data['Amount_sunshine'] = numina_data['Amount_sunshine']*0.1
numina_data['Length_raintime'] = numina_data['Length_raintime']*0.1
numina_data['Amount_rain'] = numina_data['Amount_rain']*0.1   

per = numina_data.time.dt.to_period("M")
numina_data['month'] = per
df = numina_data.groupby('month').mean().reset_index()

global p
global step

categories = ['pedestrians', 'bicyclists', 'cars', 'buses', 'trucks']
select_category = Select(title='Choose category:', value='pedestrians', options=categories, width=200, height=50)

weathertypes = ['Average_windspeed', 'Average_temperature', 'Amount_sunshine','Length_raintime', 
                'Amount_rain', 'Average_humidity']
select_weather = Select(title='Choose weather type:', value='Average_windspeed', options=weathertypes, 
                        width=200, height=50)

p = figure(title = '', height = 400, width=750, x_axis_type='datetime')
p.left[0].formatter.use_scientific = False
p.extra_y_ranges = {"foo": Range1d(start=0, end=100)}
p.add_layout(LinearAxis(y_range_name="foo", axis_label='foo label'), 'right')
p.xaxis.axis_label = "Month"
p.yaxis[0].axis_label = 'Traffic'
p.yaxis[1].axis_label = 'Weather'

r1 = p.line([], [], color="lightgreen", line_width=3, legend="Category")
r2 = p.line([], [], color="purple", line_width=3, legend="Weather", y_range_name='foo')

p.legend.location = "top_left"
p.legend.title = 'Legend'
p.legend.title_text_font_style = "bold"
p.legend.title_text_font_size = "20px"

ds1 = r1.data_source
ds2 = r2.data_source

step = 0
def update():
    global step
    category = df[select_category.value]
    weather = df[select_weather.value]
    p.y_range.start = min(category)
    p.y_range.end = max(category)
    p.extra_y_ranges['foo'].start = min(weather) #new secondary axis min
    p.extra_y_ranges['foo'].end = max(weather) #new secondary axis max

    p.title.text = select_category.value + " vs " + select_weather.value
    p.yaxis[0].axis_label = select_category.value
    p.yaxis[1].axis_label = select_weather.value
    ds1.data['x'].append(df['month'][step])
    ds1.data['y'].append(category[step])
    ds2.data['x'].append(df['month'][step])
    ds2.data['y'].append(weather[step])
    ds1.trigger('data', ds1.data, ds1.data)
    ds2.trigger('data', ds2.data, ds2.data)
    step += 1
    if step == 22:
        button.label = "🔄 Clear plot"
        curdoc().remove_periodic_callback(callback_id)

def update_select(attr, old, new):
    pass

select_category.on_change('value', update_select)
select_weather.on_change('value', update_select)

def animate():
    global callback_id
    if button.label == '▶️ Play':
        button.label = '⏸ Pause'
        callback_id = curdoc().add_periodic_callback(update, 600)
    elif button.label == "🔄 Clear plot":
        global step
        global renders
        renders = p.renderers
        renders[0].data_source.data['y'] = []
        renders[0].data_source.data['x'] = []
        renders[1].data_source.data['x'] = []
        renders[1].data_source.data['y'] = []
        step = 0
        button.label = '▶️ Play'
    else:
        button.label = '▶️ Play'
        curdoc().remove_periodic_callback(callback_id)


button = Button(label='▶️ Play', width=100)
button.on_click(animate)

title = Div(text="<b>AN INTERACTIVE EXPLORER FOR NUMINA AND WEATHER DATA</b>", style={'font-size': '150%', 'color': 'purple'})
subtitle = Div(text="<b>Interact with the widgets on the left to plot the different traffic categories versus the various weather types</b>", style={'font-size': '100%', 'color': 'black'})

controls = [select_category, select_weather, button]
inputs = column(controls)
l = column(title, subtitle, row(inputs, p), sizing_mode="scale_both")

#Making the document
curdoc().add_root(l)
curdoc().title = 'Numina'
