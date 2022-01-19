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

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CYBORG],meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"property": "og:image","content": "https://i.ibb.co/SXLDNvY/dash-img.jpg"}
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


df_covid_age_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/111 Online Covid-19 data_2021-11-18.csv')

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
    yaxis=dict(
        title='Rate',
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15,
    bargroupgap=0.1,
    paper_bgcolor='#282828',
    plot_bgcolor='#282828',
    font=dict(color='#adafae')
)

fig_transmission.update_xaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)
fig_transmission.update_yaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)

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
          'layout': {'update_layout':{'barmode':'stack'},'paper_bgcolor':'#282828','plot_bgcolor':'#282828','font':{'color':'#adafae'},'yaxis':{'title':'Cases','gridcolor':'rgba(61,61,61,0.2)'},'xaxis':{'showgrid':False},'legend':{'title':{'text':'Age Bands'}}}
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
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="#282828")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},height=1000,paper_bgcolor="#282828",plot_bgcolor="#282828",font=dict(color='#adafae'),coloraxis_colorbar_title="Total Cases")
    return fig



fig_deaths = go.Figure(data=go.Heatmap(
        z=df_region_covid['cumDeaths60DaysByDeathDate'],
        x=df_region_covid['date'],
        y=df_region_covid['areaName'],
        colorscale='Viridis',
        connectgaps=True))

fig_deaths.update_layout(
    title='Deaths in UK Regions',
    xaxis_nticks=36,
    paper_bgcolor='#282828',
    plot_bgcolor='#282828',
    font=dict(color='#adafae'))

fig_deaths.update_xaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)
fig_deaths.update_yaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)


fig_cases = go.Figure(data=go.Heatmap(
        z=df_region_covid['cumCasesBySpecimenDate'],
        x=df_region_covid['date'],
        y=df_region_covid['areaName'],
        colorscale='Viridis'))

fig_cases.update_layout(
    title='Cases in UK Regions',
    xaxis_nticks=36,
    paper_bgcolor='#282828',
    plot_bgcolor='#282828',
    font=dict(color='#adafae'))

fig_cases.update_xaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)
fig_cases.update_yaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)


features_deaths = df_covid_global_transposed.columns
features_cases = df_covid_global_cases_transposed.columns


news = news_scrape()
news.pop()
news.pop()
news.pop()


tabs_styles = {
    'height': '44px',
    'align-items': 'center',
    'margin':'10px'
}
tab_style = {
    'borderBottom': '1px solid #adafae',
    'padding': '6px',
    'fontWeight': 'bold',
    'border-radius': '15px',
    'background-color': '#282828',
    'box-shadow': '0px 4px 8px 0px #adafae',
    'margin':'10px'

}

tab_selected_style = {
    'borderTop': '1px solid #adafae',
    'borderBottom': '1px solid #adafae',
    'backgroundColor': '#adafae',
    'color': '#282828',
    'padding': '6px',
    'border-radius': '15px',
}

app.layout = dbc.Container([

           html.Div([
                     html.H1(['Dashboard for Covid-19 Statistics in UK'],style={'text-align':'center','color':'#adafae'}),
                     html.Hr(style={'background-color':'rgba(61,61,61,0.5)'}),
                    ],style={'margin-top':'10px'}),


          dbc.Row(
            [

                dbc.Col(
                    [
                        dbc.Card(
                                dbc.CardBody(
                                            [
                                            html.H3(['Total Cases in World: {}'.format(df_cases_sum.iloc[-1])],style={'color':'orange','text-align':'center'}),
                                            html.H3(['Total Cases in United Kingdom: {}'.format(df_covid_cases_deaths['cumCasesByPublishDate'].iloc[0])],style={'color':'orange','text-align':'center'})

                                            ]
                                ),
                        )

                    ],md=6
                ),
                dbc.Col(
                    [
                         dbc.Card(
                                  dbc.CardBody(
                                               [
                                                html.H3(['Total Deaths in World: {}'.format(df_death_sum.iloc[-1])],style={'color':'red','text-align':'center'}),
                                                html.H3(['Total Deaths in United Kingdom: {}'.format(df_covid_global_transposed['United Kingdom'].iloc[-1])],style={'color':'red','text-align':'center'})

                                               ]
                                  )
                         )

                    ],md=6
                ),
            ],style={'margin-bottom':'20px'},
            align="center",
         ),

         dbc.Row(
           [
               dbc.Col(
                   [
                        dbc.Card(
                                dbc.CardBody(
                                            [
                                            html.H2(['Global Covid-19'],style={'font-size':'30px', 'font-weight':'bold','text-align':'center'}),
                                            dcc.Tabs(
                                                    [
                                                    dcc.Tab(label="Global Cases",
                                                            children=[
                                                            html.Div(
                                                                    [
                                                                    html.Label(['Select Country'],style={'font-weight':'bold'}),
                                                                    dcc.Dropdown(id='country-dropdown-cases',
                                                                                 options=[{'label':i,'value':i} for i in features_cases],
                                                                                 value=['United Kingdom','Germany'],
                                                                                 multi= True,
                                                                                 style={'background-color':'#282828'}

                                                                    )

                                                                    ],style={'padding':'40px'}
                                                            ),

                                                            dcc.Graph(id='global-covid-cases',config= {'displaylogo': False,'displayModeBar':False})

                                                            ],
                                                            style = tab_style, selected_style = tab_selected_style
                                                    ),
                                                    dcc.Tab(label="Global Deaths",
                                                            children=[
                                                             html.Div(
                                                                      [
                                                                      html.Label(['Select Country'],style={'font-weight':'bold'}),
                                                                      dcc.Dropdown(id='country-dropdown',
                                                                                   options=[{'label':i,'value':i} for i in features_deaths],
                                                                                   value=['United Kingdom','Germany'],
                                                                                   multi= True,
                                                                                   style={'background-color':'#282828'}

                                                                      )

                                                                      ],style={'padding':'40px'}
                                                             ),

                                                             dcc.Graph(id='global-covid',config= {'displaylogo': False,'displayModeBar':False})

                                                            ],
                                                            style = tab_style, selected_style = tab_selected_style
                                                    )
                                                    ],style = tabs_styles
                                            )

                                            ]
                                )
                        )
                   ],md=8
               ),


               dbc.Col(
                   [
                         dbc.Card(
                                  dbc.CardBody(
                                               [
                                               html.H2(['Headlines | Covid-19 as of Today In United Kingdom'],style={'font-size':'30px', 'font-weight':'bold','text-align':'center'}),
                                               html.Div(
                                                        id="news",
                                                        children=[
                                                        html.Ul(className='timeline', children=[html.Li(i) for i in news])
                                                        ]
                                               )

                                               ],style={'height':'720px','overflow':'auto'}
                                  )
                         )
                   ],md=4
               ),
           ],style={'margin-bottom':'20px'},
           align="center",
        ),

        dbc.Row(
          [

              dbc.Col(
                  [
                       dbc.Card(
                                dbc.CardBody(
                                             [
                                             html.H2(['Covid-19 Vaccination Progress'],style={'font-size':'30px', 'font-weight':'bold','text-align':'center'}),
                                             dcc.Graph(id='covid-pie-v',
                                                       figure= {'data':[
                                                                   go.Pie(
                                                                   labels=['Complete','1st Dose','2nd Dose'],
                                                                   values= vaccinated_values
                                                                   )
                                                       ],'layout': go.Layout(title='Vaccination Stats',paper_bgcolor='#282828',plot_bgcolor='#282828',font=dict(color='#adafae'))},config= {'displaylogo': False,'displayModeBar':False}),

                                              dcc.Graph(id='covid-pie-t',
                                                        figure= {'data':[
                                                                    go.Pie(
                                                                    labels=['Pillar 1 Tests','Pillar 2 Tests','Pillar 3 Tests','Pillar 4 Tests'],
                                                                    values= pillar_values
                                                                    )
                                                        ],'layout': go.Layout(title='Testing Stats',paper_bgcolor='#282828',plot_bgcolor='#282828',font=dict(color='#adafae'))},config= {'displaylogo': False,'displayModeBar':False})

                                             ]
                                )
                       )

                  ],md=4
              ),
              dbc.Col(
                  [
                        dbc.Card(
                                dbc.CardBody(
                                            [
                                            html.H2(['Heatmap for Deaths in UK Regions'],style={'font-size':'30px', 'font-weight':'bold','text-align':'center'}),
                                            dcc.Graph(id='covid-heat-d',figure=fig_deaths,config= {'displaylogo': False,'displayModeBar':False}),
                                            dcc.Graph(id='covid-heat-c',figure=fig_cases,config= {'displaylogo': False,'displayModeBar':False})

                                            ]
                                )
                        )
                  ],md=8
              ),
          ],style={'margin-bottom':'20px'},
          align="center",
       ),


        dbc.Row(
          [

              dbc.Col(
                  [
                        dbc.Card(
                                dbc.CardBody(
                                            [
                                             html.H2(['Covid-19 Transmission Rate'],style={'font-size':'30px','font-weight':'bold','text-align':'center'}),
                                              dcc.Graph(id='covid-bar-transmission', figure=fig_transmission,config= {'displaylogo': False,'displayModeBar':False})


                                            ]
                                )
                        )

                  ],md=6
              ),
              dbc.Col(
                  [
                        dbc.Card(
                                dbc.CardBody(
                                            [
                                             html.H2(['Planned Daily Hospitalization Capacity for Covid-19 Patients'],style={'font-size':'30px', 'font-weight':'bold','text-align':'center'}),
                                             dcc.Graph(id='covid-hospital',
                                                       figure= {'data':[
                                                                   go.Scatter(
                                                                   x = df_covid_hospital_cap['date'],
                                                                   y = df_covid_hospital_cap['plannedCapacityByPublishDate'],
                                                                   mode='lines',
                                                                   )
                                                       ],'layout': go.Layout(paper_bgcolor='#282828',plot_bgcolor='#282828',font=dict(color='#adafae'),yaxis=dict(title='Capacity',gridcolor='rgba(61,61,61,0.2)'),xaxis=dict(gridcolor='rgba(61,61,61,0.2)'))},config= {'displaylogo': False,'displayModeBar':False})

                                            ]
                                )
                        )

                  ],md=6
              ),
          ],style={'margin-bottom':'20px'},
          align="center",
       ),


        dbc.Row(
          [

              dbc.Col(
                  [
                       dbc.Card(
                                dbc.CardBody(
                                            [
                                             html.H2(['Covid-19 Patients Data for UK Regions'],style={'font-size':'30px', 'font-weight':'bold','text-align':'center'}),
                                             html.Div([
                                                 html.Label(['Select Region'],style={'font-weight':'bold','margin-right':'5px'}),
                                                 dcc.Dropdown(id='selectedRegion',
                                                              options=[{'label':i,'value':i} for i in df_region_covid['areaName'].unique()],
                                                              value='London',
                                                              style={'background-color':'#282828','margin-right':'5px'})
                                             ], style={'width':'50%','display':'inline-block'}),
                                             html.Div([
                                                 html.Label(['Select Parameter'],style={'font-weight':'bold','margin-left':'5px'}),
                                                 dcc.Dropdown(id='selectedParameter',
                                                              options=[{'label':'Cases','value':'cumCasesBySpecimenDate'},{'label':'Deaths','value':'cumDeaths60DaysByDeathDate'}],
                                                              value='cumDeaths60DaysByDeathDate',
                                                              style={'background-color':'#282828','margin-left':'5px'})
                                             ], style={'width':'50%','display':'inline-block'}),
                                              dcc.Graph(id='region-graph',config= {'displaylogo': False,'displayModeBar':False})


                                            ]
                                )
                       ),


                  ],md=12
              )

              ],style={'margin-bottom':'20px'}
           ),



         dbc.Row(
           [

               dbc.Col(
                   [
                      dbc.Card([
                               dbc.CardBody(
                                            [
                                             html.H2(['Covid-19 Age Demographics'],style={'font-size':'30px', 'font-weight':'bold','text-align':'center'}),
                                             dcc.Graph(id='covid-age',figure=update_graph_age(),config= {'displaylogo': False,'displayModeBar':False})

                                            ]
                               )
                      ],style={'margin-bottom':'20px'}),
                      dbc.Card(
                              dbc.CardBody(
                                          [
                                          html.H2(['Covid-Patients Occupied MV Beds'],style={'font-size':'30px','font-weight':'bold','text-align':'center'}),
                                          dcc.Graph(id='covid-bar',
                                                    figure= {'data':[
                                                                go.Scatter(
                                                                x = df_occupied_beds['date'],
                                                                y = df_occupied_beds['covidOccupiedMVBeds'],
                                                                fill='tozeroy',
                                                                marker_color='rgb(26, 118, 255)',
                                                                )
                                                    ],'layout': go.Layout(bargap=0.5,paper_bgcolor='#282828',plot_bgcolor='#282828',font=dict(color='#adafae'),yaxis=dict(title='Number of MV Beds Occupied',gridcolor='rgba(61,61,61,0.2)'),xaxis=dict(showgrid=False))},config= {'displaylogo': False,'displayModeBar':False})

                                          ]
                              )
                      ),
                   ],md=6
               ),
               dbc.Col(
                   [
                       dbc.Card(
                                dbc.CardBody(
                                            [
                                             html.H2(['Covid-19 Infections with UK Region Map'],style={'font-size':'30px', 'font-weight':'bold','text-align':'center'}),
                                             dcc.Graph(id = 'map',figure=update_map(),config= {'displaylogo': False,'displayModeBar':False})
                                            ]
                                )
                       )
                   ],style={'height':'100%'},md=6
               )
           ],style={'margin-bottom':'20px'},
           align="center",
        ),


],style={'font-family':'Oswald'},
fluid=True)



@app.callback(Output('global-covid','figure'),
              [Input('country-dropdown','value')])

def update_graph(country_name):
    fig = go.Figure()
    for tic in country_name:
        fig.add_trace(go.Scatter(x=df_covid_global_transposed['date'],
                                 y=df_covid_global_transposed[tic],
                                 name=tic,
                                 mode='lines'))

        fig.update_layout(yaxis=dict(title="Deaths"),
                         paper_bgcolor='#282828',
                         plot_bgcolor='#282828',
                         font=dict(color="#adafae"))
        fig.update_xaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)
        fig.update_yaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)

    return fig


@app.callback(Output('global-covid-cases','figure'),
              [Input('country-dropdown-cases','value')])

def update_graph(country_name):
    fig = go.Figure()
    for tic in country_name:
        fig.add_trace(go.Scatter(x=df_covid_global_cases_transposed['date'],
                                 y=df_covid_global_cases_transposed[tic],
                                 name=tic,
                                 mode='lines'))

        fig.update_layout(yaxis=dict(title="Cases"),
                         paper_bgcolor='#282828',
                         plot_bgcolor='#282828',
                         font=dict(color="#adafae"))
        fig.update_xaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)
        fig.update_yaxes(gridcolor='rgba(61,61,61,0.2)',zerolinecolor='rgb(61,61,61)',zeroline=True,zerolinewidth=2)


    return fig


@app.callback(Output('region-graph','figure'),
             [Input('selectedRegion','value')],
             [Input('selectedParameter','value')])

def update_figure(region,parameter):

    if parameter == "cumDeaths60DaysByDeathDate":
        yaxis_title = "Deaths"
    elif parameter == "cumCasesBySpecimenDate":
        yaxis_title = "Cases"
    for region_name in df_region_covid['areaName'].unique():
        df_by_region = df_region_covid[df_region_covid['areaName']==region]

    return {'data':[go.Scatter(
                    x=df_by_region['date'],
                    y=df_by_region[parameter],
                    fill='tozeroy',
                    marker_color='rgb(26, 118, 255)'

    )]

    ,'layout':go.Layout(
                        yaxis={'title':yaxis_title,'gridcolor':'rgba(61,61,61,0.2)'},
                        hovermode='closest',
                        paper_bgcolor='#282828',
                        plot_bgcolor='#282828',
                        font=dict(color='#adafae')
                        )
            }



if __name__ == "__main__":
    app.run_server()
