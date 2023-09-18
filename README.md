# Assess Like-Mindedness among two countries/regions

### Application to EU potential gas suppliers.

This repository allows to reproduce the calculations underlying the findings of the paper "Geopolitical application of "like-mindedness" indicator in choosing and diversifying EU energy partners to substitute Russian gas”, currently submitted to Energy Policy.

In the "LMI_class.py" script, you find a simple Python class which allows to:
- parse the Excel files containing the scores of each country in each of the adopted indices (in the "indices" folder)
- rename all the countries names according to a specific criteria, adopting the [country_converter library](https://github.com/IndEcol/country_converter)
- calculate the average (possibly as arithmetic and geometric) of the indices scores by country (indicator 'g') and the like-mindedness indicator (LMI) given a reference country/region
- add new indicators for each country (in this case data about gas production, reserves, exports, marginal export capacity and others); raw data are provided within the "additional_data" folder

Additionally, the script allows to plot Figure 2 in html (the annotations provided in the paper's version have been added separately). For better visualization, install the font we used from this [link](https://fontsgeek.com/fonts/helveticaneue-light).

Figure 1 and 3 are provided in Excel format. Figures are contained in the "plots" folder
