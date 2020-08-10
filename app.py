import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''

The gender wage gap is a measure of how men and women are paid differently for no other reason than their sex. The
gender wage gap can be measured in many different ways but the results collectively show that women are paid approximately
20% less than men are. An average woman makes $530,000 less than an average man over the course of her lifetime because 
of the gender wage gap, while the average college-educated woman makes $800,000 less than the average college-educated man.
The gender wage gap has been narrowing since 1980s but the trend has stalled in recent years. The report from Economic
Policy Institute (EPI) discusses about the gender wage gap in more depth:
https://www.epi.org/publication/what-is-the-gender-pay-gap-and-is-it-real/#epi-toc-5

The General Social Survey (GSS) explains the modern American trends by gathering demographic and behavioral data 
on many topics such as civil liberties, crime, morality, etc. The GSS provides extensive set of sociological data 
collected by the National Opinion Research Center (NORC) at the University of Chicago since 1972. A full documentation 
of the data can be found here: 
http://gss.norc.org/Documents/reports/methodological-reports/MR122%20Occupational%20Prestige.pdf
'''

# select features
gss_table = gss_clean.groupby('sex').agg({'income': 'mean',
                                         'job_prestige': 'mean',
                                         'socioeconomic_index': 'mean',
                                         'education': 'mean'}).round(2)

gss_table = gss_table.reset_index()

# generate a table
table = ff.create_table(gss_table)
table.show()

gss_bar = gss_clean.groupby(['sex','male_breadwinner']).size().reset_index().rename({0:'count'}, axis=1)
gss_bar

fig_bar = px.bar(gss_bar, x='male_breadwinner', y='count', color='sex',
                 labels={'count':'Number of Responses', 'male_breadwinner':'Responses'},
                 barmode='group')

fig_bar.show()

fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income',\
                         color='sex', trendline='ols',
                         height=600, width=600,
                         labels={'job_prestige': 'Occupational Prestige Score',
                                 'income': 'Personal Annual Income'},
                         hover_data=['education','socioeconomic_index'])
fig_scatter.show()

# box plot of income distribution by sex
fig_box_income = px.box(gss_clean, x='income', y='sex', color='sex',
                        labels={'income': 'Personal Annual Income'})
fig_box_income.update_yaxes(visible=False) # remove the label for sex
fig_box_income.update_layout(showlegend=False)
fig_box_income.show()

# box plot of job_prestige distribution by sex
fig_box_prestige = px.box(gss_clean, x='job_prestige', y='sex', color='sex',
                          labels={'job_prestige': 'Occupational Prestige Score'})
fig_box_prestige.update_yaxes(visible=False) # remove the label for sex
fig_box_prestige.update_layout(showlegend=False)
fig_box_prestige.show()

# create a new dataframe with select features
gss_clean6 = gss_clean[['income','sex','job_prestige']]
gss_clean6.head()

# breaks 'job_prestige' into six categories with equal-sized bins
gss_clean6['job_prestige_cat'] = pd.cut(gss_clean6['job_prestige'], bins=6)
# drop all rows with any missing values
gss_clean6 = gss_clean6.dropna()

fig_facet = px.box(gss_clean6, x='income', y='sex', color='sex',
                   facet_col='job_prestige_cat', facet_col_wrap=3, 
                   color_discrete_map = {'male':'blue', 'female':'red'}, 
                   category_orders={'job_prestige_cat': gss_clean6.job_prestige_cat.cat.categories.tolist()})
fig_facet.show()

colors = {
    'background': '#9adbe8', #304C
    'text': '#FFFFFF'
}

app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1(
        children='Exploring the 2018 General Social Survey (GSS)',
        style={'width': '100%', 'height': 200,
               'border': 50,
               'border-color': '9adbe8', 
               'padding': 0,
               'textAlign': 'center',
               'line-height': 200,
               'font-size': 36,
               'backgroundColor': colors['background'],
               'color': colors['text']},
        ),
        
        dcc.Markdown(children=markdown_text),

        html.Div([
            html.H5("Socioeconomic Indicators by Sex"), # table (no.2)
            dcc.Graph(figure=table)],
            
            style={
                'border': 50
            }      
        ),  
       
        html.Div([
            html.Div([

                html.H5("Responses to Stereotypical Gender Roles by Sex"), # barplot (no.3)
                dcc.Graph(figure=fig_bar)

            ], style = {'width':'48%', 'float':'left'}),
            
             html.Div([

                html.H5("Occupational Prestige Score vs. Personal Annual Income by Sex"), # scatterplot (no.4)
                dcc.Graph(figure=fig_scatter),

            ], style = {'width':'52%', 'float':'right'})],
            
            style={
                'width': '100%', 'height': 700,
                'border': 50
            }
        ),
        
        html.Div([ # boxplots side-by-side (no.5)
            
            html.H5("Personal Annual Income Distribution by Sex"),
            dcc.Graph(figure=fig_box_income)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H5("Occupational Prestige Score Distribution by Sex"),
            dcc.Graph(figure=fig_box_prestige)
            
        ], style = {'width':'48%', 'float':'right'}),  
        
        html.H5("Income Distribution by Occupational Prestige Score Groups"), # faceted boxplots (no.6)
        dcc.Graph(figure=fig_facet)
    ]
)

if __name__ == '__main__':
    app.run_server(mode='inline', debug=True)
