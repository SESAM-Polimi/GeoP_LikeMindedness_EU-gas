# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 16:42:26 2023

@author: Lorenzo Rinaldi
"""

import pandas as pd
import country_converter as coco
import statistics
import copy
import plotly.express as px

_acceptable_means = ["mean","fmean","geometric_mean","harmonic_mean"]
_score_column = ['Overall score']

class LMI():
    
    def __init__(self):
        self.indices = {}
        self.LMI = {}
        self.regions = {}
        
    def read_indices(self, path, name):  
        self.indices[name] = pd.read_excel(path,index_col=[0])/100
        self.indices[name]

    def rename_countries(self, method='name'):
        for index,ranking in self.indices.items():
            countries = ranking.index
            new_countries = coco.convert(names=countries, to=method)
            ranking.index = new_countries
        try:
            add_countries = list(self.additional_indicators.index)
            new_add_countries = coco.convert(names=add_countries, to=method)
            self.additional_indicators.index = new_add_countries
        except:
            pass
        try:
            add_countries = list(self.g.index)
            new_add_countries = coco.convert(names=add_countries, to=method)
            self.g.index = new_add_countries
        except:
            pass
    
    def all_countries(self,save=False):
        countries_list = []
        for i in self.indices:
            countries_list += list(self.indices[i].index)
        countries_list = sorted(set(countries_list))
        
        countries = []
        for country in countries_list:
            counter = 0
            for i in self.indices:
                if country in self.indices[i].index:
                    counter+=1
            if counter==len(list(self.indices.keys())):
                countries+=[country]
        
        self.countries = countries
        
        self.indices = {i:self.indices[i].loc[self.countries,:] for i in self.indices}
        
        if save:
            return self.countries

    def calc_g(self,mean='geometric_mean'):
        g = []
        if mean not in _acceptable_means:
            print(f"acceptable mean to be selected among {_acceptable_means}")
        else:
            for country in self.countries:
                
                values = [self.indices[i].loc[country,_score_column] for i in self.indices]   
                
                if mean == 'geometric_mean':
                    aggregated = statistics.geometric_mean(values)
                elif mean == 'mean':
                    aggregated = statistics.mean(values)
                elif mean == 'fmean':
                    aggregated = statistics.fmean(values)
                elif mean == 'harmonic_mean':
                    aggregated = statistics.harmonic_mean(values)
                    
                g += [aggregated]
                
            self.g = pd.DataFrame(g,index=self.countries,columns=_score_column)
            
            if self.regions != {}:
                for region_name in self.regions:
                    self.calc_g_regions(region_name)
            
                    
    def calc_g_regions(self,region_name):
        if self.g.shape[0] != 0:
            g_reg = 0
            for i in self.regions[region_name]:
                g_reg += self.g.loc[i,_score_column].values
            g_reg /= len(self.regions[region_name])
            
            self.g = pd.concat([self.g, pd.DataFrame(g_reg[0],index=[region_name],columns=_score_column)])
            
            
    def add_region(self, region_name, find_countries=True, countries_list=None):
        if find_countries:
            reg_countries = pd.DataFrame(coco.convert(names=self.countries, to=region_name),index=self.countries)
            reg_countries = reg_countries.dropna()
            reg_countries = sorted(list(reg_countries.index))
        else:
            reg_countries = countries_list
        self.regions[region_name] = reg_countries
        
        self.calc_g_regions(region_name)
        

    def calc_LMI(self, reference):
        self.LMI[reference] = copy.deepcopy(self.g.loc[self.countries,:])
        for country in self.countries:
            self.LMI[reference].loc[country,_score_column] -= self.g.loc[reference,_score_column].values[0]
            
            
    def add_indicators_template(self, excel_path, sheet_name='new_indicators'):
        excel_template = pd.DataFrame("",index=self.countries,columns=[""])
        excel_template.to_excel(excel_path,sheet_name=sheet_name)
    
    
    def get_add_indicators(self, excel_path, sheet_name='new_indicators'):
        self.additional_indicators = pd.read_excel(excel_path,sheet_name,index_col=[0])

        
    def LMI_matrix(self):
        for country in self.countries:
            self.calc_LMI(country)
        self.LMI_matrix = pd.concat([self.LMI[x] for x in self.LMI],axis=1)                 
        self.LMI_matrix.columns = list(self.LMI.keys())    
        
        
        
        
#%%
geop_LMI = LMI()

indices = ['CPI 2022','EPI 2022','GDI 2022','WPFI 2020','HFI 2022']
for i in indices:
    geop_LMI.read_indices(path=f"indices\{i}.xlsx",name=i)
    geop_LMI.rename_countries(method='ISO3')
all_countries = geop_LMI.all_countries(save=True)

geop_LMI.calc_g()
# geop_LMI.LMI_matrix()

geop_LMI.add_region('EU27')
geop_LMI.calc_LMI('EU27')

# geop_LMI.add_indicators_template(r"additional_data\gas_data.xlsx",sheet_name='gas_data')
geop_LMI.get_add_indicators(r"additional_data\gas_data.xlsx",sheet_name='gas_data')


#%% defining other countries clusters
gas_producers = list(geop_LMI.additional_indicators.query("`Total gas production, 2021, bcm [EIA]`!=0").index)
gas_producers_iso = coco.convert(names=gas_producers, to='ISO3')

EU_pot_suppliers = []
for country in gas_producers:

    # 1st criterion: presence of pipelines and/or LNG routes to EU
    if geop_LMI.additional_indicators.loc[country,'LNG export to EU, 2021 [bcm]']>0 or geop_LMI.additional_indicators.loc[country,'Pipeline export to EU, 2021 [bcm]']>0:
        EU_pot_suppliers += [country]
    
    # 2nd criterion: LNG shipping distance lower than 5000 nautical miles
    if geop_LMI.additional_indicators.loc[country,"Sea shipping distance [n miles]"]!='NA':
        if geop_LMI.additional_indicators.loc[country,"Sea shipping distance [n miles]"]<5000: 
            EU_pot_suppliers += [country]
    
    # 3rd criterion: Presence of European O&G companies
    if type(geop_LMI.additional_indicators.loc[country,"Companies in operation"])==str:
        EU_pot_suppliers += [country]
        
EU_pot_suppliers = sorted(list(set(EU_pot_suppliers)))
EU_pot_suppliers_iso = coco.convert(names=EU_pot_suppliers, to='ISO3')
for x in geop_LMI.regions['EU27']:
    if x in EU_pot_suppliers_iso:
        EU_pot_suppliers_iso.remove(x)

other_suppliers = []
for country in gas_producers_iso:
    if country not in EU_pot_suppliers_iso and country not in geop_LMI.regions['EU27']:
        other_suppliers+=[country]    

row = copy.deepcopy(geop_LMI.countries)
to_remove = []
for country in geop_LMI.countries:
    if country in geop_LMI.regions['EU27']:
        to_remove += [country]
    if country in gas_producers_iso:
        to_remove += [country]
    if country in other_suppliers:
        to_remove += [country]
    if country in EU_pot_suppliers_iso:
        to_remove += [country]

to_remove = sorted(list(set(to_remove)))
for x in to_remove:
    row.remove(x)
    
        
#%%
geop_LMI.rename_countries(method='ISO3')
geop_LMI.add_region('EU27 potential<br>gas suppliers',find_countries=False, countries_list=EU_pot_suppliers_iso)
geop_LMI.add_region('Other gas<br>suppliers',find_countries=False, countries_list=other_suppliers)
geop_LMI.add_region('Rest of<br>the World',find_countries=False, countries_list=row)
geop_LMI.add_region('World',find_countries=False, countries_list=geop_LMI.countries)

#%%
g = copy.deepcopy(geop_LMI.g).loc[geop_LMI.countries,:]
g.index.names = ['Country']
g.reset_index(inplace=True)

regions = {}
for country in geop_LMI.countries:
    for reg in geop_LMI.regions:
        if reg!='World':
            if country in geop_LMI.regions[reg]:
                regions[country] = reg


for region in geop_LMI.regions:
    if region != 'World':
        g['Region'] = g['Country'].map(regions)

g = g.sort_values('Region')


boxplot = px.box(
    g,
    x=_score_column[0],
    y='Region', 
    color_discrete_map={
        "EU27": "#3a86ff",
        "EU27 potential<br>gas suppliers": "#ff006e",
        'Other gas<br>suppliers': "#4cc9f0",
        "Rest of<br>the World": "#8338ec"
        },
    color='Region',
    points='all', 
    hover_data=['Country',_score_column[0]],
    template='seaborn', 
    )
boxplot.update_layout(
    font_size=16, 
    font_family='HelveticaNeue Light',
)
boxplot.update_yaxes(title='')
boxplot.update_xaxes(title='g',)
    
boxplot.write_html(r"plots\Figure 2.html",auto_open=True)






