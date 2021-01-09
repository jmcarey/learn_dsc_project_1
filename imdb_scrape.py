# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 12:47:39 2020

@author: Jordan
"""
import requests, re
import pandas as pd
import datetime
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import re
from bs4 import BeautifulSoup
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.models import ColumnDataSource, Slider, RangeSlider, LinearColorMapper, ColorBar
from bokeh.transform import transform
from bokeh.layouts import column, row
from math import pi
from collections import Counter
def parse_film(lister):
    film = {}
    
    text = [text for text in lister.stripped_strings]
    while '|' in text:
        text.remove('|')
    while ',' in text:
        text.remove(',')
    
    film['title']= text[1]
      
    film['imdb_id'] = lister.find('div', class_='ribbonize').attrs['data-tconst']
    
    year = lister.find('span', class_="lister-item-year text-muted unbold").contents[0]
    film['year'] = int(re.search("\\d+", year).group(0))
    
    if lister.find('span', class_='genre'):
        genre = lister.find('span', class_='genre').contents
        film['genre'] = genre[0].replace(',', '').strip().split()
    
    if lister.find('strong'):
        film['imdb_rating'] = float(lister.find('strong').contents[0])

    metascore = lister.find('span', class_=re.compile('metascore'))
    if metascore:
        film['metascore'] = int(metascore.contents[0].strip())

    directors = []
    stars = []
    if 'Director:' in text:
        directors.append(text[text.index('Director:')+1])
    if 'Directors:' in text:
        directors.append(text[text.index('Directors:')+1])
        directors.append(text[text.index('Directors:')+2])
    if 'Stars:' in text:
        for i in range(1, 5):
            try:
                stars.append(text[text.index('Stars:')+i])
            except:
                break
    if 'Gross:' in text:
            film['gross'] = text[text.index('Gross:')+1]
    film['director'], film['stars'] = directors, stars
    
    return film


# Retrieve the 10000 most popular English language films on IMDB and parse data
films = []
today = datetime.date.today()
delta = datetime.timedelta(days=45)
release_date = today - delta
for i in range(0,40):
    html_page = requests.get(
        'https://www.imdb.com/search/title/?title_type=feature&release_date=,{release_date}&languages=en&count=250&start={250*i +1}'
    )
    soup = BeautifulSoup(html_page.content, 'html.parser')
    lister = soup.find('div', class_="lister-item mode-advanced")

    for _ in list(range(0, 250)):
        films.append(parse_film(lister))
        lister = lister.nextSibling.nextSibling
 
# Clean data       
films_df = pd.DataFrame(films)
films_df.set_index('imdb_id', inplace=True)
films_df = films_df.dropna()
extr = films_df.loc[:, 'gross'].str.extract(r'(\d+\.?\d+)', expand=False)
extr = pd.to_numeric(extr)
films_df.loc[:, 'gross'] = extr

films_df.to_csv('movie_info.csv')