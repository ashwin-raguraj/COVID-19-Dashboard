


#######---------------------------------------LOADING LIBRARIES-----------------------------------------###################


import dash
import dash_core_components as dcc
import dash_html_components as html


import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import date
import plotly.graph_objects as go

import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import json
import dash_table
from datetime import date, timedelta


###-----------------  LOADING DATA -------------------------###

today = date.today() - timedelta(days=2)
previous_day = date.today() - timedelta(days=3)

# Month abbreviation, day and year  
today_formatted = today.strftime("%m-%d-%Y")
previous_day_formatted = previous_day.strftime("%m-%d-%Y")

today_formatted_text = today.strftime("%d %b %Y")

# DAILY CASES
df_daily_report = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/" + str(today_formatted) + ".csv")
df_daily_report_previous = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/" + str(previous_day_formatted) + ".csv")

# COMPUTING CONFIRMED, RECOVERED, ACTIVE, DEATHS CASES AND PERCENTAGE INCREASE/DECREASE
confirmed_world = df_daily_report['Confirmed'].sum()
confimred_world_previous = df_daily_report_previous['Confirmed'].sum()
confirmed_world_today = confirmed_world - confimred_world_previous

recovered_world = df_daily_report['Recovered'].sum()
recovered_world_previous = df_daily_report_previous['Recovered'].sum()
active_world = df_daily_report['Active'].sum()
active_world_previous = df_daily_report_previous['Active'].sum()
active_world_today = round((active_world - active_world_previous),0)

deaths_world = df_daily_report['Deaths'].sum()
deaths_world_previous = df_daily_report_previous['Deaths'].sum()

confirmed_outcome_world = recovered_world + deaths_world
percentage_recovered = round((recovered_world / confirmed_outcome_world)*100,1)
percentage_deaths = round((deaths_world / confirmed_outcome_world)*100,1)


## VACCINATION DATA
df_vacc = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')
df_vacc_max = df_vacc.groupby(["location"], as_index=False).max()
total_vaccinations_world = df_vacc_max['total_vaccinations']
countries_vacc = df_vacc['location'].unique()


#LOADING COUNTRY CODES
with open('cc3_cn_r.json') as json_file:
    cc3_cn_r = json.load(json_file)



#### GROUPING BY COUNTRIES 

df_group_country= df_daily_report.groupby('Country_Region')

list_countries=[]
for i,g in df_group_country:
	list_countries.append({'Country_Region':g['Country_Region'].unique()[0],
		                           'Confirmed':g['Confirmed'].sum(),\
		                           'Active':g['Active'].sum(),\
		                           'Recovered':g["Recovered"].sum(),\
		                           'Deaths':g['Deaths'].sum(),\
		                           'Incidence_Rate':round(g['Incident_Rate'].mean(),3),\
		                           'Case_Fatality_Ratio':round(g['Case_Fatality_Ratio'].mean(),3)})


df_countries=pd.DataFrame(list_countries)

df_countries['CODE']= df_countries['Country_Region'].map(cc3_cn_r)
df_countries= df_countries.dropna(subset=['CODE'])





# TIME SERIES DATA FOR CONFIRMED CASES
df_time_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')


df_exclude_confirmed= df_time_confirmed[df_time_confirmed.columns\
[~df_time_confirmed.columns.isin(['Province/State','Lat','Long'])]]
df_exclude_confirmed.set_index('Country/Region',inplace=True)
df_exclude_confirmed = df_exclude_confirmed.diff(axis=1)
df_exclude_confirmed.reset_index(inplace=True)
df_date_confirmed = pd.melt(df_exclude_confirmed,id_vars=['Country/Region'],var_name='date',value_name='value')


# TIME SERIES DATA FOR RECOVERED CASES
df_time_recovered = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

df_excluded_recovered= df_time_recovered[df_time_recovered.columns\
[~df_time_recovered.columns.isin(['Province/State','Lat','Long'])]]
df_excluded_recovered.set_index('Country/Region',inplace=True)
df_excluded_recovered = df_excluded_recovered.diff(axis=1)
df_excluded_recovered.reset_index(inplace=True)
df_date_recovered=pd.melt(df_excluded_recovered,id_vars=['Country/Region'],var_name='date',value_name='value')


## For callback retrieving countries

countries=df_date_recovered['Country/Region'].unique()


## LOADING NEWS ARTICLES

news_articles_list = open("covid_news_articles.csv", "r",encoding='utf-8').readlines()

news_cards_list=[]

for x in news_articles_list[1:]:
	article= x.split(',')
	news_cards_template= dbc.Col(dbc.Card(
		[dbc.CardImg(src=article[2],top=True),
		dbc.CardBody(
			[html.H6(article[0]),
			html.P(
				article[1],
				style={'fontSize':12}),
			dbc.CardLink('Link to the Article',href=article[3])])])
		,width=2)
	news_cards_list.append(news_cards_template)
BS = "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])


############----------------------------------------- INDICATOR -------------------------###############


fig_indicator= go.Figure()

fig_indicator.add_trace(go.Indicator(
	mode='number+delta',
	value=recovered_world,
	title={'text':'Recovered Cases'},
	domain={'x':[1,0.5],'y':[0.8,0.9]},
	title_font_size= 25,
	number_font_size=40,
	delta={'reference':recovered_world_previous}))


fig_indicator.add_trace(go.Indicator(
	mode='number+delta',
	value=confirmed_world,
	title={'text':'Confirmed Cases'},
	domain={'x':[1,0.5],'y':[0.4,0.5]},
	delta_increasing_color= '#FF4136',
	title_font_size= 25,
	number_font_size=40,
	delta={'reference':confimred_world_previous}))


fig_indicator.add_trace(go.Indicator(
	mode='number+delta',
	value=deaths_world,
	title={'text':'Total Deaths'},
	domain={'x':[1,0.5],'y':[0,0.1]},
	delta_increasing_color= '#FF4136',
	title_font_size= 25,
	number_font_size=40,
	delta={'reference':deaths_world_previous}))


#---------------------- CARDS ACTIVE AND OUTCOME CASES----------------------------#

card_active_cases= dbc.Card(

	[dbc.CardHeader('Active Cases'),

	dbc.CardBody(
		[html.H3(html.B(active_world)),
		html.H5("Cases Active Currently", style={'color':'blue','fontSize':14}),
		html.H5(html.B(confirmed_world), style={'color':'green'}),
		html.P("Total Confirmed Cases",style={'fontSize':14}),
		html.H5(html.B(confirmed_world_today),style={'color':'red'}),
		html.H5("Current Cases", style={'color':'black','fontSize':14}),

		dbc.CardLink("More Details",href="https://covid19.who.int/table")
		]
		
		),
	],
	)


card_outcome_cases= dbc.Card(

	[dbc.CardHeader('Closed Cases'),

	dbc.CardBody(
		[html.H3(html.B(confirmed_outcome_world)),
		html.H5("Cases which had an outcome", style={'color':'blue','fontSize':14}),
		html.H5(html.B(str(recovered_world)+"("+ str(percentage_recovered)+ "%)"),style={'color':'green'}),
		html.P("Total recovered cases till now",style={'fontSize':14}),
		html.H5(html.B(str(deaths_world)+"("+ str(percentage_deaths)+ "%)"),style={'color':'red'}),
		html.H5("Current Cases", style={'color':'black','fontSize':14}),

		dbc.CardLink("More Details",href="https://covid19.who.int/table")
		]
		
		),
	],
	)



#------------------------------ DROPDOWN COUNTRIES SELECTION ------------------------------------#

dropdown_countries= dcc.Dropdown(
	id='dropdown',
	options=[{'label':x,'value':x}for x in countries],

	value=['India','Russia','China'],
	clearable=False,
	multi=True)




#----------------------- RADIO BUTTON WORLD MAP -------------------------------------------------------#
radio_button_world= dcc.RadioItems(
	id='radio_button_world',
	options=[
	{'label':'Most Affected        ', 'value':'scatter'},
	{'label':'Country-wise','value':'choropleth'}],
	value='scatter',
	labelStyle={'display':'inline-block'})

#-------------------------- WORLD MAP -----------------------------------------#
fig_world = go.Figure(data=go.Choropleth(
	locations=df_countries['CODE'],
	z= df_countries['Confirmed'],
	text=df_countries['Country_Region'],
	colorscale='Reds',
	autocolorscale=True,
	colorbar_title='Number of confirmed cases'))


fig_world.update_layout(
	autosize=True,
	geo=dict(
		showcoastlines=True,
		projection_type='equirectangular'),

	)

#------------------------ WORLD MAP 2 ----------------------------------------#

fig_world_scatter = px.scatter_geo(df_countries,locations='CODE',
	hover_name='Country_Region',size='Confirmed',

	projection='natural earth',size_max=45)


#---------------------------------- TABLE COVID ----------------------------------#

table_covid = dash_table.DataTable(
	id='datatable-interactivity',
	columns=[
	{'name':i,'id':i,'deletable':False,"selectable":True}
	for i in df_countries.columns],
	data= df_countries.to_dict('records'),
	editable=True,
	filter_action='native',
	sort_action='native',
	row_deletable=False,
	page_action='native',
	page_current=0,
	page_size=15,


	style_data_conditional=[

	{
	'if':{'row_index':'odd'},
	     'backgroundColor':'rgb(230,230,230)'
	}],

	style_header={
	'backgroundColor':'rgb(176,224,230)',
	'fontWeight':'bold',
	'whiteSpace':'normal',
	'height':'auto',
	'lineHeight':'15px'
	},

	style_data={
	'whiteSpace':'normal',
	'height':'auto'
	},

	style_table={
	'overflowY':'auto'
	},

	style_as_list_view=False
	)

#------------------------------------- VACCINE COUNTRIES DROPDOWN ------------------------------------#

dropdown_vaccine_timeline = dcc.Dropdown(
	id='dropdown_vaccine_timeline',
	options=[{'label':x,'value':x} for x in countries_vacc],
	value='World',
	clearable=False,
	multi=False)
#----------------------------- VACCINE DATA SELECTION -------------------------------------#

radio_button_vaccine=dcc.RadioItems(
	id='radio_button_vaccine',
	options=[
	{'label':'Total Vaccinated','value':'total_vaccinations'},
	{'label':'Vaccinated per 100','value':'people_vaccinated_per_hundred'},
	{'label':'Fully vaccinated per 100 ','value':'people_fully_vaccinated_per_hundred'}],
	value='people_vaccinated_per_hundred',
	labelStyle={'display':'inline-block'})

#------------------------ NEWS CARDS ----------------------------------------------#





####################---------------- NAVIGATION BAR AT TOP --------------------------##
navbar = dbc.Navbar(
    [
        html.A(
            
            dbc.Row(
                [
                    
                    dbc.Col(dbc.NavbarBrand("COVID-19 Dashboard", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            
        ),
        dbc.NavbarToggler(id="navbar-toggler")
    ],
    color="#00008B",
    dark=True,
)


##################### -------------------------------------- APP LAYOUT WITH HTML---------------------------------------------------##############3
app.layout = html.Div(children=[navbar,

    dbc.Row([dbc.Col(html.P('Last updated on: ' + str(today_formatted_text), \
        style={"fontSize":14, 'color':'grey'}),width=10)],justify='center'),
    #INDICATOR

    dbc.Row([dbc.Col(dcc.Graph(figure=fig_indicator),width=10)],justify='center'),

    #ACTIVE & CLOSED CASES CARDS
    
    dbc.Row([dbc.Col(card_active_cases,width={"size":4,"offset":2}),
    	dbc.Col(card_outcome_cases,width={"size":4})]) ,
    html.Br(),
    html.Br(),
    

    dbc.Row([dbc.Col(html.H5('Number of cases by Countries'),width=10)],justify='center'),
    html.Br(),

    #DROPDOWN COUNTRIES


    dbc.Row([dbc.Col(dropdown_countries,width=8)],justify='center'),
    dbc.Row([dbc.Col(dbc.Card(dcc.Graph(id='line-chart-confirmed'),body=True), width=5),
    	dbc.Col(dbc.Card(dcc.Graph(id='line-chart-recovered'),body=True), width=5)], justify='center'),


    #RECOVERED AND CONFIRMED CASES GRAPHS

    html.Br(),
    html.Br(),

    dbc.Row([dbc.Col(html.H5('COVID-19 Tabular Data'),\
        width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("COVID-19 is an infectious disease caused by a 2019 discovered coronavirus."),width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("The countries and their corresponding data are given below"),width=10)],justify='center'),
    
    #TABLE

    dbc.Row([dbc.Col(table_covid,width=10)],justify='center'),

    html.Br(),
    dbc.Row([dbc.Col(html.H5('World Map'),width=10)],justify='center'),
    html.Br(),

    # RADIO BUTTONS
    dbc.Row([dbc.Col(radio_button_world,width=10)],justify='center'),

    html.Br(),
    # WORLD GRAPH

    dbc.Row([dbc.Col(dcc.Graph(id='update-world-graph'),width=10)],justify='center'),


   
    html.Br(),
    dbc.Row([dbc.Col(html.H5('Vaccination Data '),\
                        width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("The COVID-19 vaccines are safe for most people 18 years and older, including those with pre-existing conditions of any kind, including auto-immune disorders. These conditions include: hypertension, diabetes, asthma, pulmonary, liver and kidney disease, as well as chronic infections that are stable and controlled")\
                        ,width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("Take whatever vaccine is made available to you first, even if you have already had COVID-19. It is important to be vaccinated as soon as possible once it’s your turn and not wait. Approved COVID-19 vaccines provide a high degree of protection against getting seriously ill and dying from the disease, although no vaccine is 100% protective.")\
                        ,width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("The vaccine timeline of different countries are plotted below:")\
                        ,width=10)],justify='center'),
    #DROPDOWN VACCINE TIMELINE 
    dbc.Row([dbc.Col(dropdown_vaccine_timeline,width=5)],justify='center'),



    #VACCINE TIMELINE AND STAtUS GRAPH

    dbc.Row([dbc.Col(dcc.Graph(id='vaccine_timeline'),width=10)],justify='center'),
    dbc.Row([dbc.Col(html.H5('Vaccination Status as of now'),\
        width=10)],justify='center'),
    
    #RADIO BUTTON VACCINE

    dbc.Row([dbc.Col(radio_button_vaccine,width=10)],justify='center'),
    
    #BAR GRAPH VACCINES
    dbc.Row([dbc.Col(dcc.Graph(id='update-vaccine'),width=10)],justify='center'),


    html.Br(),
    dbc.Row([dbc.Col(html.H5('COVID-19 Latest News updates'),\
        width=10)],justify='center'),
    html.Br(),
    #NEWS CARDS

    dbc.Row(news_cards_list,justify='center')

    ]
    )




##################################3------------------------- DEFINING CALL BACKS ------------------------------#####################3


# LINE CHART CONFIRMED 


@app.callback(
	Output("line-chart-confirmed",'figure'),
	[Input('dropdown','value')])
def update_line_chart_confirmed(countries):
	df_filtered_date = df_date_confirmed[df_date_confirmed['Country/Region'].isin(countries)]
	
	fig = px.line(df_filtered_date,x='date',y='value',color='Country/Region',\
		title= 'Confirmed Cases', line_shape='hv')

	return fig

# LINE CHART RECOVERED

@app.callback(
	Output("line-chart-recovered",'figure'),
	[Input('dropdown','value')])
def update_line_chart_recovered(countries):
	df_filtered_date = df_date_recovered[df_date_recovered['Country/Region'].isin(countries)]
	
	fig = px.line(df_filtered_date,x='date',y='value',color='Country/Region',\
		title= 'Recovered Cases', line_shape='hv')

	return fig


# WORLD GRAPH
@app.callback(
	Output('update-world-graph','figure'),
	[Input('radio_button_world','value')])

def update_world_graph(plot_type):
	if plot_type == 'scatter':
		return fig_world_scatter
	elif plot_type == 'choropleth':
		return fig_world





# VACCINE TIMELINE
@app.callback(
	Output('vaccine_timeline','figure'),
	[Input('dropdown_vaccine_timeline','value')])

def vaccine_timeline(country):
	df_vacc_filtered = df_vacc[df_vacc['location']==country]
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=df_vacc_filtered['date'],\
		y=df_vacc_filtered['total_vaccinations'],fill='tonexty',name='Total Vaccination'))

	fig.add_trace(go.Scatter(x=df_vacc_filtered['date'],\
		y=df_vacc_filtered['people_fully_vaccinated'],fill='tozeroy',name='People Vaccinted'))

	fig.update_layout(xaxis_title='Date',yaxis_title='Total Count')

	return fig

# VACCINATION STATUS
@app.callback(
	Output('update-vaccine','figure'),
	[Input('radio_button_vaccine','value')])

def vaccination_status(parameter):
	fig=px.bar(df_vacc_max, x='location', y=parameter,color_discrete_sequence=['blue'],\
		height=650)
	return fig


#------------------------------ RUNNING THE SERVER --------------------------------#
app.run_server(debug=True)


