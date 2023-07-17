# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 18:12:35 2023

@author: loren
"""

#%% importing data
import pandas as pd
import plotly.express as px
import country_converter as coco
import math
import statistics
import copy

sheets = ['GDI','CPI','HFI','WPFI','EPI','Gas data']
path = 'raw_data.xlsx'

data = {i:pd.read_excel(path,sheet_name=i,index_col=[0]) for i in sheets}

#%% renaming countries
for index,ranking in data.items():
    countries = ranking.index
    new_countries = coco.convert(names=countries, to='name')
    ranking.index = new_countries

#%% list of countries for which LMI is assessable
all_countries = sorted(set(list(pd.concat([data['GDI'],data['CPI'],data['HFI'],data['WPFI'],data['EPI']],axis=0).index)))

countries = []
for country in all_countries:
    counter = 0
    for i in ['GDI','CPI','HFI','WPFI','EPI']:
        if country in data[i].index:
            counter+=1
    if counter==5:
        countries+=[country]

eu27_countries = pd.DataFrame(coco.convert(names=countries, to='EU27'),index=countries)
eu27_countries = eu27_countries.dropna()
eu27_countries = sorted(list(eu27_countries.index))

#%% calculate g and LMI with respect to EU for all countries
g = []
for country in countries:
    mean = statistics.geometric_mean([
        data['GDI'].loc[country,'Overall score'],
        data['CPI'].loc[country,'Overall score'],
        data['HFI'].loc[country,'Overall score'],
        data['WPFI'].loc[country,'Overall score'],
        data['EPI'].loc[country,'Overall score'],
        ])
    g+=[mean]
data['g'] = pd.DataFrame(g,index=countries,columns=['Overall score'])

g_eu27 = 0
for eu in eu27_countries:
    g_eu27+=data['g'].loc[eu,'Overall score']
g_eu27 /= 27

data['LMI'] = copy.deepcopy(data['g'])
for country in countries:
    data['LMI'].loc[country,'Overall score'] -= g_eu27

#%% selecting gas suppliers according to 3 criteria

gas_producers = sorted(list(data['Gas data'].index))
selected_suppliers = []

for country in gas_producers:
    
    # 1st criterion: presence of pipelines and/or LNG routes to EU
    if data['Gas data'].loc[country,"LNG export to EU, 2021 [bcm]"]>0 or data['Gas data'].loc[country,"Pipeline export to EU, 2021 [bcm]"]>0:
        selected_suppliers += [country]
    
    # 2nd criterion: LNG shipping distance lower than 5000 nautical miles
    if data['Gas data'].loc[country,"Sea shipping distance [n miles]"]!='/':
        if data['Gas data'].loc[country,"Sea shipping distance [n miles]"]<5000: 
            selected_suppliers += [country]
    
    # 3rd criterion: Presence of European O&G companies
    if type(data['Gas data'].loc[country,"Companies in operation"])==str:
        selected_suppliers += [country]
        
selected_suppliers = sorted(list(set(selected_suppliers)))

# 4th criterion: among countries?
selected_suppliers = sorted(list(set(selected_suppliers) & set(countries)))

other_gas_suppliers = []
for country in gas_producers:
    if country not in selected_suppliers:
        other_gas_suppliers+=[country]

#%%
for i in ['GDI','CPI','HFI','WPFI','EPI','g','LMI']:
    data[i].columns = [i]

countries_data = pd.concat([
    data['GDI'].loc[countries,:],
    data['CPI'].loc[countries,:],
    data['HFI'].loc[countries,:],
    data['WPFI'].loc[countries,:],
    data['EPI'].loc[countries,:],
    data['g'].loc[countries,:],
    data['LMI'].loc[countries,:],
    ], axis=1)

suppliers_data = pd.concat([
    data['GDI'].loc[selected_suppliers,:],
    data['CPI'].loc[selected_suppliers,:],
    data['HFI'].loc[selected_suppliers,:],
    data['WPFI'].loc[selected_suppliers,:],
    data['EPI'].loc[selected_suppliers,:],
    data['g'].loc[selected_suppliers,:],
    data['LMI'].loc[selected_suppliers,:],
    ], axis=1)

countries_data = countries_data.stack()
countries_data = countries_data.to_frame() 
countries_data.reset_index(inplace=True)
countries_data.columns = ['Country','Index','Score']


#%%





#%% boxplot EU countries g
eu27_g = countries_data.query("Index=='g'")
eu27_g['Score'] /= 100

reg_map = {}
for country in eu27_g['Country']:
    if country in eu27_countries:
        reg_map[country] = 'EU'
    elif country in selected_suppliers:
        reg_map[country] = 'EU potential<br>gas suppliers'
    elif country in other_gas_suppliers:
        reg_map[country] = 'Other gas<br>suppliers'
    else:
        reg_map[country] = 'Rest of<br>the World'      

eu27_g['Region'] = eu27_g['Country'].map(reg_map)
eu27_g = eu27_g.sort_values('Region')

boxplot = px.box(
    eu27_g,
    x='Score',
    y='Region', 
    color_discrete_map={
        "EU": "#3a86ff",
        "EU potential<br>gas suppliers": "#ff006e",
        'Other gas<br>suppliers': "#4cc9f0",
        "Rest of<br>the World": "#8338ec"
        },
    color='Region',
    points='all', 
    hover_data=['Country','Score'],
    template='seaborn', 
    )
boxplot.update_layout(
    font_size=16, 
    font_family='HelveticaNeue Light',
    legend=dict(traceorder='reversed')
)
boxplot.update_yaxes(title='')
boxplot.update_xaxes(title='g',)
    
boxplot.write_html(r"plots\boxplot_g.html",auto_open=True)



