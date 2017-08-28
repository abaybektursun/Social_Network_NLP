import pandas as pd
import plotly.plotly as py

from IPython.html import widgets 
from IPython.display import display, clear_output
from plotly.graph_objs import *
from plotly.widgets import GraphWidget

df = pd.read_csv('https://raw.githubusercontent.com/jvns/pandas-cookbook/master/data/311-service-requests.csv')

# Note: These are possible values for `borough`
# array(['QUEENS', 'MANHATTAN', 'BROOKLYN', 'BRONX', 'STATEN ISLAND',
#       'Unspecified'], dtype=object)

# we will define functions to deal with the output we get from our widgets

def isTextValid(text):
    if text_input.value.upper() in borough_list:
        valid.value=True
        borough_df = df[df['Borough'] == text_input.value.upper()]
        
        temp = borough_df.groupby([df['Agency']]).count()['Agency']
        g2.plot({'data': [{'x': temp.index, 'y': temp }]})
        g2.relayout({'title': 'Complaints Dealt by Agencies in {}'.format(text_input.value.upper())})
        message.value = ""
    else: 
        valid.value=False
        message.value = "<font color=\"red\">Can't find that borough</font>"
    
# we will no define and display the widgets in our app
g2 = GraphWidget('https://plot.ly/~kevintest/1178/')

button = widgets.Button(description="Submit")

text_input = widgets.Text(
    description='Borough:',
    value='MANHATTAN',
)

message = widgets.HTML(
    value="",
)

valid = widgets.Valid(
    value=True,
)

# this will be initalize our listener
button.on_click(isTextValid)


container = widgets.HBox(children=[text_input, button, valid, message])
display(container)
display(g2)

