#!/usr/bin/env python
# coding: utf-8

# # Segmenting and Clustering Neighbourhoods in Toronto

# 
# Importing libraries

# In[3]:


import pandas as pd
import numpy as np
import requests


# All the 3 tasks of web scraping, cleaning and clustering are implemented in the same notebook for the ease of evaluation.
# 
# Installing and Importing the required Libraries

# In[5]:


get_ipython().system('pip install beautifulsoup4')
get_ipython().system('pip install lxml')
import requests # library to handle requests
import pandas as pd # library for data analsysis
import numpy as np # library to handle data in a vectorized manner
import random # library for random number generation

#!conda install -c conda-forge geopy --yes 
from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values

# libraries for displaying images
from IPython.display import Image 
from IPython.core.display import HTML 


from IPython.display import display_html
import pandas as pd
import numpy as np
    
# tranforming json file into a pandas dataframe library
from pandas.io.json import json_normalize

get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium # plotting library
from bs4 import BeautifulSoup
from sklearn.cluster import KMeans
import matplotlib.cm as cm
import matplotlib.colors as colors

print('Folium installed')
print('Libraries imported.')


# # Scraping the Wikipedia page for the table of postal codes of Canada
# 
# BeautifulSoup Library of Python is used for web scraping of table from the Wikipedia. The title of the webpage is printed to check if the page has been scraped successfully or not. Then the table of postal codes of Canada is printed.

# In[22]:


source = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup=BeautifulSoup(source,'lxml')
print(soup.title)
from IPython.display import display_html
tab = str(soup.table)
display_html(tab,raw=True)


# # The html table is converted to Pandas DataFrame for cleaning and preprocessing.

# In[23]:


dfs = pd.read_html(tab)
df=dfs[0]
df.head()


# # Data preprocessing and cleaning

# In[24]:


# Dropping the rows where Borough is 'Not assigned'
df1 = df[df.Borough != 'Not assigned']

# Combining the neighbourhoods with same Postalcode
df2 = df1.groupby(['Postal Code','Borough'], sort=False).agg(', '.join)
df2.reset_index(inplace=True)

# Replacing the name of the neighbourhoods which are 'Not assigned' with names of Borough
df2['Neighbourhood'] = np.where(df2['Neighbourhood'] == 'Not assigned',df2['Borough'], df2['Neighbourhood'])

df2


# In[25]:


# Shape of data frame
df2.shape


# #  Importing the csv file conatining the latitudes and longitudes for various neighbourhoods in Canada

# In[59]:


lat_lon = pd.read_csv('https://cocl.us/Geospatial_data')
lat_lon.head()


# # Merging the two tables for getting the Latitudes and Longitudes for various neighbourhoods in Canada

# In[62]:


#lat_lon.rename(columns={'Postal Code':'Postcode1'},inplace=True)
df3 = pd.merge(df2,lat_lon,on='Postal Code')
df3.head()


# # The notebook from here includes the Clustering and the plotting of the neighbourhoods of Canada which contain Toronto in their Borough
# Getting all the rows from the data frame which contains Toronto in their Borough.

# In[63]:


df4 = df3[df3['Borough'].str.contains('Toronto',regex=False)]
df4


# # Visualizing all the Neighbourhoods of the above data frame using Folium

# In[64]:


map_toronto = folium.Map(location=[43.651070,-79.347015],zoom_start=10)

for lat,lng,borough,neighbourhood in zip(df4['Latitude'],df4['Longitude'],df4['Borough'],df4['Neighbourhood']):
    label = '{}, {}'.format(neighbourhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
    [lat,lng],
    radius=5,
    popup=label,
    color='blue',
    fill=True,
    fill_color='#3186cc',
    fill_opacity=0.7,
    parse_html=False).add_to(map_toronto)
map_toronto


# # The map might not be visible on Github. Check out the README for the map.
# Using KMeans clustering for the clsutering of the neighbourhoods

# In[68]:


k=5
toronto_clustering = df4.drop(['Postal Code','Borough','Neighbourhood'],1)
kmeans = KMeans(n_clusters = k,random_state=0).fit(toronto_clustering)
kmeans.labels_
df4.insert(0, 'Cluster Labels', kmeans.labels_)


# In[69]:


df4


# In[70]:


# create map
map_clusters = folium.Map(location=[43.651070,-79.347015],zoom_start=10)

# set color scheme for the clusters
x = np.arange(k)
ys = [i + x + (i*x)**2 for i in range(k)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, neighbourhood, cluster in zip(df4['Latitude'], df4['Longitude'], df4['Neighbourhood'], df4['Cluster Labels']):
    label = folium.Popup(' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[ ]:




