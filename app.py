import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import plotly.express as px
import os
import geojson
#import dash_auth

import pandas as pd
from datetime import datetime
from datetime import date
from bs4 import BeautifulSoup
from requests_html import HTMLSession

#USERNAME_PASSWORD_PAIRS = [['username','password'],['zenalytiks','Zenalytiks888']]

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CERULEAN],meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
app.title = "UK Covid-19 Dashboard"
#auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

pd.options.mode.chained_assignment = None

news_headline =[]
news =[]

def news_scrape():

    for i in range(1,5):
        news_url = "https://www.bbc.co.uk/search?q=covid+19&page="+str(i)

        session = HTMLSession()

        response = session.get(news_url)

        soup = BeautifulSoup(response.content,'html.parser')

        div = soup.findAll('div',attrs={'class':'ssrcss-1cbga70-Stack e1y4nx260'})

        for p in div:
            n = p.find('p',attrs={'class':'ssrcss-1q0x1qg-Paragraph eq5iqo00'})
            news_headline.append(n.text)
    return news_headline


#Further from here i am reading the csv files from the github provided by you

df_covid_global = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

df_covid_global.fillna(0)

for i in range(len(df_covid_global.index)):                                    #Had to formate the dataset in order to make it a square matrix.
    if(pd.isna(df_covid_global['Province/State'].iloc[i]) != True):            # Did this for both the global datasets further with other datasets.
        df_covid_global['Country/Region'][i] = df_covid_global['Country/Region'][i]+' '+ df_covid_global['Province/State'][i]


df_covid_global.drop('Province/State', axis=1, inplace=True)
df_covid_global.drop('Lat', axis=1, inplace=True)
df_covid_global.drop('Long', axis=1, inplace=True)
df_covid_global.set_index('Country/Region', inplace=True)

df_covid_global_transposed =df_covid_global.transpose()

df_death_sum = df_covid_global_transposed.sum(axis = 1,skipna = True)


for i in range(len(df_covid_global_transposed.index)):                  # Formatting the Time in correct foramt for the Dash to understand.Did this couple of times further.
    df_covid_global_transposed.index.values[i] = pd.to_datetime(df_covid_global_transposed.index.values[i]).strftime('%Y-%m-%d')

df_covid_global_transposed['date'] = df_covid_global_transposed.index

df_covid_global_cases = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

df_covid_global_cases.fillna(0)

#Some of the Countries had data represented as Province wise. So i just dropped the Province column and concatenated it with the country name.

for i in range(len(df_covid_global_cases.index)):
    if(pd.isna(df_covid_global_cases['Province/State'].iloc[i]) != True):
        df_covid_global_cases['Country/Region'][i] = df_covid_global_cases['Country/Region'][i]+' '+ df_covid_global_cases['Province/State'][i]


df_covid_global_cases.drop('Province/State', axis=1, inplace=True)
df_covid_global_cases.drop('Lat', axis=1, inplace=True)
df_covid_global_cases.drop('Long', axis=1, inplace=True)
df_covid_global_cases.set_index('Country/Region', inplace=True)

df_covid_global_cases_transposed =df_covid_global_cases.transpose()

df_cases_sum = df_covid_global_cases_transposed.sum(axis = 1,skipna = True)

for i in range(len(df_covid_global_cases_transposed.index)):
    df_covid_global_cases_transposed.index.values[i] = pd.to_datetime(df_covid_global_cases_transposed.index.values[i]).strftime('%Y-%m-%d')

df_covid_global_cases_transposed['date'] = df_covid_global_cases_transposed.index


df_covid_cases_deaths = pd.read_csv('https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=cumCasesByPublishDate&metric=cumDeaths60DaysByDeathDate&format=csv')

df_covid_hospital_cap = pd.read_csv('https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=plannedCapacityByPublishDate&format=csv')


df_covid_age_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/111 Online Covid-19 data_2021-08-26.csv')

df_covid_age = pd.read_csv(df_covid_age_path)

df_covid_transmission = pd.read_csv('https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=transmissionRateMax&metric=transmissionRateMin&format=csv')



fig_transmission = go.Figure()
fig_transmission.add_trace(go.Bar(x=df_covid_transmission['date'],
                y=df_covid_transmission['transmissionRateMin'],
                name='Minimum Transmission Rate',
                marker_color='rgb(55, 83, 109)'
                ))
fig_transmission.add_trace(go.Bar(x=df_covid_transmission['date'],
                y=df_covid_transmission['transmissionRateMax'],
                name='Maximum Transmission Rate',
                marker_color='rgb(26, 118, 255)'
                ))

fig_transmission.update_layout(
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='Rate',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
)

df_covid_age.drop('ccgcode',axis=1,inplace=True)
df_covid_age.drop('ccgname',axis=1,inplace=True)

# for i in range(len(df_covid_age.index)):
#     df_covid_age['journeydate'][i] = pd.to_datetime(df_covid_age['journeydate'][i]).strftime('%Y-%m-%d')

def update_graph_age():
    traces = []
    for sex in df_covid_age['sex'].unique():
        df_by_Type = df_covid_age[df_covid_age['sex']==sex]
        traces.append(go.Histogram(
        x= df_by_Type['ageband'],
        y= df_by_Type['Total'],
        name = sex
        ))
    fig = {
          'data': traces,
          'layout': {'title': 'Cases','update_layout':{'barmode':'stack'}}
    }

    return fig

df_occupied_beds = pd.read_csv('https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=covidOccupiedMVBeds&format=csv')

df_vaccinated = pd.read_csv('https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=cumPeopleVaccinatedCompleteByPublishDate&metric=cumPeopleVaccinatedFirstDoseByPublishDate&metric=cumPeopleVaccinatedSecondDoseByPublishDate&format=csv')

vaccinated_values = [df_vaccinated['cumPeopleVaccinatedCompleteByPublishDate'].iloc[0],df_vaccinated['cumPeopleVaccinatedFirstDoseByPublishDate'].iloc[0],df_vaccinated['cumPeopleVaccinatedSecondDoseByPublishDate'].iloc[0]]

df_pillar_test = pd.read_csv('https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=cumPillarOneTestsByPublishDate&metric=cumPillarThreeTestsByPublishDate&metric=cumPillarTwoTestsByPublishDate&metric=cumPillarFourTestsByPublishDate&format=csv')

pillar_values = [df_pillar_test['cumPillarOneTestsByPublishDate'].iloc[0],df_pillar_test['cumPillarTwoTestsByPublishDate'].iloc[0],df_pillar_test['cumPillarThreeTestsByPublishDate'].iloc[0],df_pillar_test['cumPillarFourTestsByPublishDate'].iloc[0]]

east_midlands = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/east_midlands.csv')
east_of_england = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/east_of_england.csv')
london = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/london.csv')
north_east = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/north_east.csv')
north_west = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/north_west.csv')
south_east = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/south_east.csv')
south_west = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/south_west.csv')
west_midlands = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/west_midlands.csv')
yorkshire_and_humber = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/yorkshire_and_humber.csv')

map_gj = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/UK_Coronavirus_(COVID-19)_Data.geojson')
map_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/UK_Coronavirus_(COVID-19)_Data.csv')

df_map_cases = pd.read_csv(map_csv)

with open(map_gj) as f:
    gj = geojson.load(f)

east_midland_covid = pd.read_csv(east_midlands)
east_england_coivd = pd.read_csv(east_of_england)
london_covid = pd.read_csv(london)
north_east_covid = pd.read_csv(north_east)
north_west_covid = pd.read_csv(north_west)
south_east_covid = pd.read_csv(south_east)
south_west_covid = pd.read_csv(south_west)
west_midlands_covid = pd.read_csv(west_midlands)
yorkshire_humber_covid = pd.read_csv(yorkshire_and_humber)

frames = [east_midland_covid,east_england_coivd,london_covid,north_east_covid,north_west_covid,south_east_covid,south_west_covid,west_midlands_covid,yorkshire_humber_covid]

df_region_covid = pd.concat(frames,ignore_index=True)


def update_map():

    fig = px.choropleth(df_map_cases, geojson=gj, color="cumCasesBySpecimenDate",
                        locations="OBJECTID", featureidkey="properties.OBJECTID",
                        projection="mercator",hover_data={'areaName':True,'cumCasesBySpecimenDate':True,'OBJECTID':False}
                       )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig



fig_deaths = go.Figure(data=go.Heatmap(
        z=df_region_covid['cumDeaths60DaysByDeathDate'],
        x=df_region_covid['date'],
        y=df_region_covid['areaName'],
        colorscale='Viridis',
        connectgaps=True))

fig_deaths.update_layout(
    title='Deaths in UK Regions',
    xaxis_nticks=36)


fig_cases = go.Figure(data=go.Heatmap(
        z=df_region_covid['cumCasesBySpecimenDate'],
        x=df_region_covid['date'],
        y=df_region_covid['areaName'],
        colorscale='Viridis'))

fig_cases.update_layout(
    title='Cases in UK Regions',
    xaxis_nticks=36)


features_deaths = df_covid_global_transposed.columns                    #Making a list of all the columns of all data sets which are further to be used by
features_cases = df_covid_global_cases_transposed.columns                #Dash core components like dropdown menus.


news = news_scrape()
news.pop()
news.pop()
news.pop()


#Further from here i have designed the layout of my dashboard which includes dash html components and dash core components
#HTML components behave in the same way as the regular HTML and these components also takes CSS as parameters.
#If you are familiar with CSS then you can stylize it just as you want.
#The attributes in regular HTML are given as parameters to these Dash html component.

app.layout = dbc.Container([

      # dcc.Tabs([
      #     dcc.Tab(label='Data Visualzation',children=[


           html.Div([
                     html.H1(['Dashboard for Covid-19 Statistics in UK'],style={'text-align':'center'}),
                     html.Hr(),
                    ]),


          dbc.Row(
            [

                dbc.Col(
                    [
                        html.Div([
                        html.H2(['Total Cases in World: {}'.format(df_cases_sum.iloc[-1])],style={'color':'orange','text-align':'center'}),
                        html.H2(['Total Cases in United Kingdom: {}'.format(df_covid_cases_deaths['cumCasesByPublishDate'].iloc[0])],style={'color':'orange','text-align':'center'})

                        ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),

                    ],md=6
                ),
                dbc.Col(
                    [
                         html.Div([
                          html.H2(['Total Deaths in World: {}'.format(df_death_sum.iloc[-1])],style={'color':'red','text-align':'center'}),
                          html.H2(['Total Deaths in United Kingdom: {}'.format(df_covid_global_transposed['United Kingdom'].iloc[-1])],style={'color':'red','text-align':'center'})
                         ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),

                    ],md=6
                ),
            ],
            align="center",
         ),





         dbc.Row(
           [

               dbc.Col(
                   [
                        html.Div([
                        html.Div([
                        html.Div([
                              html.H2(['Global Data for Cases of Covid-19'],style={'font-size':'30px', 'font-weight':'bold'})
                        ],style={'text-align':'center','margin-top':'20px'}),
                        html.Label(['Select Country'],style={'font-weight':'bold'}),
                        dcc.Dropdown(id='country-dropdown-cases',
                                     options=[{'label':i,'value':i} for i in features_cases],   #Here the multi-dropdown menu takes a dictionary of label and value pair that is mapped on the
                                     value=['United Kingdom','Germany'],                              #columns of the datasets.
                                     multi= True

                        )
                        ]),
                         dcc.Graph(id='global-covid-cases',config= {'displaylogo': False,'displayModeBar':False})
                         ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),

                   ],md=4
               ),
               dbc.Col(
                   [
                         html.Div([
                         html.Div([
                         html.Div([
                               html.H2(['Global Data for Deaths from Covid-19'],style={'font-size':'30px', 'font-weight':'bold'})
                         ],style={'text-align':'center','margin-top':'20px'}),
                         html.Label(['Select Country'],style={'font-weight':'bold'}),
                         dcc.Dropdown(id='country-dropdown',
                                      options=[{'label':i,'value':i} for i in features_deaths],
                                      value=['United Kingdom','Germany'],
                                      multi= True

                         )
                         ]),
                         dcc.Graph(id='global-covid',config= {'displaylogo': False,'displayModeBar':False})
                         ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),


                   ],md=4
               ),

               dbc.Col(
                   [
                         html.Div([
                         html.Div([
                         html.H2(['Headlines | Covid-19 as of Today In United Kingdom'],style={'font-size':'30px', 'font-weight':'bold'})
                         ],style={'text-align':'center','margin-top':'20px'}),
                         html.Div(
                                  id="news",
                                  children=[                                                   #children is a parameter of Div component which means the very next nested element.
                                  html.Ul(className='timeline', children=[html.Li(i) for i in news])
                                  ]
                         )
                         ],style = {'height':'600px','padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px','overflow':'auto'}),

                   ],md=4
               ),
           ],
           align="center",
        ),




        dbc.Row(
          [

              dbc.Col(
                  [
                       html.Div([
                       html.Div([
                       html.Div([
                            html.H2(['Covid-19 Vaccination Progress'],style={'font-size':'30px', 'font-weight':'bold'})
                        ],style={'text-align':'center','margin-top':'20px'}),
                            dcc.Graph(id='covid-pie-v',
                                      figure= {'data':[
                                                  go.Pie(
                                                  labels=['Complete','1st Dose','2nd Dose'],
                                                  values= vaccinated_values
                                                  )
                                      ],'layout': go.Layout(title='Vaccination Stats')},config= {'displaylogo': False,'displayModeBar':False}),

                             dcc.Graph(id='covid-pie-t',
                                       figure= {'data':[
                                                   go.Pie(
                                                   labels=['Pillar 1 Tests','Pillar 2 Tests','Pillar 3 Tests','Pillar 4 Tests'],
                                                   values= pillar_values
                                                   )
                                       ],'layout': go.Layout(title='Testing Stats')},config= {'displaylogo': False,'displayModeBar':False})

                       ])
                       ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),

                  ],md=4
              ),
              dbc.Col(
                  [
                        html.Div([
                        html.Div([
                        html.Div([
                             html.H2(['Heatmap for Deaths in UK Regions'],style={'font-size':'30px', 'font-weight':'bold'})

                        ],style={'text-align':'center','margin-top':'20px'})
                        ]),

                        dcc.Graph(id='covid-heat-d',figure=fig_deaths,config= {'displaylogo': False,'displayModeBar':False}),
                        dcc.Graph(id='covid-heat-c',figure=fig_cases,config= {'displaylogo': False,'displayModeBar':False})
                        ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),



                  ],md=8
              ),
          ],
          align="center",
       ),


        dbc.Row(
          [

              dbc.Col(
                  [
                        html.Div([
                        html.Div([
                        html.Div([
                             html.H2(['Covid-19 Transmission Rate'],style={'font-size':'30px', 'font-weight':'bold'})
                         ],style={'text-align':'center','margin-top':'20px'}),
                             dcc.Graph(id='covid-bar-transmission', figure=fig_transmission,config= {'displaylogo': False,'displayModeBar':False})

                        ])
                        ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),


                  ],md=6
              ),
              dbc.Col(
                  [
                        html.Div([
                        html.Div([
                        html.Div([
                             html.H2(['Planned Daily Hospitalization Capacity for Covid-19 Patients'],style={'font-size':'30px', 'font-weight':'bold'})
                         ],style={'text-align':'center','margin-top':'20px'}),
                             dcc.Graph(id='covid-hospital',
                                       figure= {'data':[
                                                   go.Scatter(
                                                   x = df_covid_hospital_cap['date'],
                                                   y = df_covid_hospital_cap['plannedCapacityByPublishDate'],
                                                   mode='lines',
                                                   )
                                       ],'layout': go.Layout(title = 'Capacity')},config= {'displaylogo': False,'displayModeBar':False})

                        ])
                        ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),


                  ],md=6
              ),
          ],
          align="center",
       ),



        dbc.Row(
          [

              dbc.Col(
                  [
                       html.Div([
                       html.Div([
                       html.Div([
                       html.H2(['Covid-19 Patients Data for UK Regions'],style={'font-size':'30px', 'font-weight':'bold'})
                      ],style={'text-align':'center','margin-top':'20px','margin-left':'20px'})

                       ]),
                       html.Div([

                           html.Label(['Select Region'],style={'font-weight':'bold'}),
                           dcc.Dropdown(id='selectedRegion',
                                        options=[{'label':i,'value':i} for i in df_region_covid['areaName'].unique()],
                                        value='London')
                       ], style={'width':'50%','display':'inline-block'}),
                       html.Div([
                           html.Label(['Select Parameter'],style={'font-weight':'bold'}),
                           dcc.Dropdown(id='selectedParameter',
                                        options=[{'label':'Cases','value':'cumCasesBySpecimenDate'},{'label':'Deaths','value':'cumDeaths60DaysByDeathDate'}],
                                        value='cumDeaths60DaysByDeathDate')
                       ], style={'width':'50%','display':'inline-block'}),

                       dcc.Graph(id='region-graph',config= {'displaylogo': False,'displayModeBar':False})
                    ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),

                  ],md=6
              ),
              dbc.Col(
                  [
                        html.Div([
                        html.Div([
                        html.Div([
                             html.H2(['Covid Occupied MV Beds'],style={'font-size':'30px', 'font-weight':'bold'})
                         ],style={'text-align':'center','margin-top':'20px'}),
                             dcc.Graph(id='covid-bar',
                                       figure= {'data':[
                                                   go.Bar(
                                                   x = df_occupied_beds['date'],
                                                   y = df_occupied_beds['covidOccupiedMVBeds'],
                                                   marker_color='rgb(26, 118, 255)',
                                                   )
                                       ],'layout': go.Layout(title = 'Number of MV Beds Occupied',bargap=0.5)},config= {'displaylogo': False,'displayModeBar':False})

                        ])
                        ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),



                  ],md=6
              ),
          ],
          align="center",
       ),




         dbc.Row(
           [

               dbc.Col(
                   [
                      html.Div([
                      html.Div([
                      html.Div([
                           html.H2(['Covid-19 Age Demographics'],style={'font-size':'30px', 'font-weight':'bold'})

                      ],style={'text-align':'center','margin-top':'20px'})
                      ]),

                      dcc.Graph(id='covid-age',figure=update_graph_age(),config= {'displaylogo': False,'displayModeBar':False})
                      ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'}),


                   ],md=6
               ),
               dbc.Col(
                   [
                       html.Div([
                       html.Div([
                       html.H2(['Covid-19 Infections with UK Region Map'],style={'font-size':'30px', 'font-weight':'bold'})
                      ],style={'text-align':'center','margin-top':'20px','margin-left':'20px'}),

                       html.Div([
                       dcc.Graph(id = 'map',figure=update_map(),config= {'displaylogo': False,'displayModeBar':False})
                       ])
                       ],style={'padding':10,'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)','transition': '0.3s','border-radius': '5px','margin-top':'20px','margin-bottom':'20px'})

                   ],md=6
               ),
           ],
           align="center",
        ),


],style={'background-color':'#F4F4F4'},fluid=True)


#Following code can be referred as Eventlisteners to all the dropdown menus.
#app.callback takes the Output function which takes the ID's of the dash core components which in this case is graph
#and take a list of Inputs which in this case are dropdown menus.

@app.callback(Output('global-covid','figure'),
              [Input('country-dropdown','value')])

def update_graph(country_name):   # Here the parameter "country_name" is passed the same parameter of Input i.e "value"
    traces = []
    for tic in country_name:
        traces.append({'x':df_covid_global_transposed['date'], 'y':df_covid_global_transposed[tic],'name':tic})   #Here i'm appending the list of columns to the multi-dropdown menu.
    fig = {
          'data': traces,
          'layout': {'title':','.join(country_name)+' Deaths'}
    }

    return fig


@app.callback(Output('global-covid-cases','figure'),
              [Input('country-dropdown-cases','value')])

def update_graph(country_name):
    traces = []
    for tic in country_name:
        traces.append({'x':df_covid_global_cases_transposed['date'], 'y':df_covid_global_cases_transposed[tic],'name':tic})
    fig = {
          'data': traces,
          'layout': {'title':','.join(country_name)+' Cases'}
    }

    return fig


@app.callback(Output('region-graph','figure'),
             [Input('selectedRegion','value')],
             [Input('selectedParameter','value')])

def update_figure(region,parameter):
    for region_name in df_region_covid['areaName'].unique():
        df_by_region = df_region_covid[df_region_covid['areaName']==region]

    return {'data':[go.Bar(                                     #This is Plotly graph object. You can use any kind of graph here such as Bar, Heatmap etc.
                    x=df_by_region['date'],
                    y=df_by_region[parameter],
                    marker_color='rgb(26, 118, 255)'

    )]

    ,'layout':go.Layout(
                        xaxis={'title':'Date'},
                        yaxis={'title':parameter},
                        hovermode='closest')
                        }



if __name__ == "__main__":            # Here the App will run on the local server which then further can be viewed in the browser.
    app.run_server()
