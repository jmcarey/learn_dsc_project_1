#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.models import ColumnDataSource, Slider, LinearColorMapper, ColorBar
from bokeh.transform import transform
from bokeh.layouts import column, row
from math import pi
from collections import Counter
import ast


def get_actors(df):
    # Returns a counter of how many times each actor appears in the films
    actors = Counter()
    for film in df['stars']:
        for actor in film:
            actors[actor] += 1
    return actors  

def get_directors(df):
    # Returns a counter of how many times each director appears in the films
    directors = Counter()
    for film in df['director']:
        for director in film:
            directors[director] += 1
    return directors  


def get_genres(df):
    # Returns a counter of how many times each genre appears in the films
    genres = Counter()
    for film in df['genre']:
        for genre in film:
            genres[genre] += 1
    return genres



films_df = pd.read_csv('movie_info.csv')

# Convert web scraper results from strings into lists
for i in range(len(films_df['stars'])):
    f = ast.literal_eval(films_df.stars[i])
    # f = f.replace('\'', '')
    # f = f.replace('[', '')
    # f = f.replace(']', '')
    # f = f.split(', ')
    #f = films_df.stars[i].split('\'')
    #while ', ' in f: f.remove(', ')
    #while '\'' in f: f.remove('\'')
    #while '[' in f: f.remove('[')
    #while ']' in f: f.remove(']')
    films_df.stars.iloc[i] = f
for i in range(len(films_df['director'])):
    f = ast.literal_eval(films_df.director[i])
    # f = films_df.director[i].split('\'')
    # while ', ' in f: f.remove(', ')
    # while '[' in f: f.remove('[')
    # while ']' in f: f.remove(']')
    films_df.director.iloc[i] = f
for i in range(len(films_df['genre'])):
    f = ast.literal_eval(films_df.genre[i])
    # f = films_df.genre[i].split('\'')
    # while ', ' in f: f.remove(', ')
    # while '[' in f: f.remove('[')
    # while ']' in f: f.remove(']')
    films_df.genre.iloc[i] = f

print(type(films_df['director'][0]))

# Create a scatter plot of gross vs metascore
source = ColumnDataSource(data=dict(title=[], year=[], genre=[], imdb_rating=[], metascore=[], director=[], stars=[],
                                   gross=[]))
hover = HoverTool(tooltips=[('Title', '@title'), ('Year', '@year'), ('Gross', '@gross'), ('Metascore', '@metascore'),
                           ('IMDB Rating', '@imdb_rating'), ('Director', '@director'), ('Cast', '@stars'), ('Genre', '@genre')])

plot = figure(plot_width=600, plot_height=800, min_border_top=100,tools=[hover,'box_zoom,pan,wheel_zoom'], title='Popular Films on IMDB', sizing_mode='scale_both')

color_mapper = LinearColorMapper(palette='Viridis256', low=films_df.imdb_rating.min(), high = films_df.imdb_rating.max())
plot.circle('metascore', 'gross', source=source, color=transform('imdb_rating', color_mapper),)

color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, location=(0,0), title='IMDB_Rating')
plot.add_layout(color_bar, 'right')

plot.xaxis.axis_label = 'Metascore'
plot.yaxis.axis_label = 'Gross (million USD)'


year_min = Slider(start=films_df['year'].min(), end=films_df['year'].max(),
                          value=films_df['year'].min(), step=1, title='Earliest Release Year')
year_max = Slider(start=films_df['year'].min(), end=films_df['year'].max(),
                          value=films_df['year'].max(), step=1, title='Latest Release Year')
gross_slider = Slider(start=0, end=films_df['gross'].max(), value=0, step=10, title="Minimum Gross")
rating_slider = Slider(start=0, end=100, value=0, step=1, title='Minimum Metascore')

source.data = dict(title=films_df['title'], year=films_df['year'], genre=films_df['genre'], imdb_rating=films_df['imdb_rating'],
                  metascore=films_df['metascore'], director=films_df['director'], stars=films_df['stars'], gross=films_df['gross'])

#Create a histogram of the actors appearing most frequently
actors_data = list(zip(*get_actors(source.data).most_common(10)))
actors_source = ColumnDataSource(data=dict(actors=actors_data[0], number=actors_data[1]))

top_actors = figure(x_range=actors_data[0], plot_height=350, plot_width=500, title="Most Common Actors",sizing_mode='scale_both',
                    tools=[HoverTool(tooltips=[('Actor', '@actors'), ('Appearances', '@number')])])
top_actors.vbar(x='actors', top='number', source=actors_source, width=0.9)
top_actors.yaxis.axis_label = 'Appearances'
top_actors.xaxis.major_label_orientation = pi / 4

#Create a histogram of the directors appearing most frequently
directors_data = list(zip(*get_directors(source.data).most_common(10)))
directors_source = ColumnDataSource(data=dict(directors=directors_data[0], number=directors_data[1]))

top_directors = figure(x_range=directors_data[0], plot_height=350, plot_width=500, title="Most Common Directors", sizing_mode='scale_both',
                       tools=[HoverTool(tooltips=[('Director', '@directors'), ('Appearances', '@number')])])
top_directors.vbar(x='directors', top='number', source=directors_source, width=0.9)
top_directors.yaxis.axis_label = 'Appearances'
top_directors.xaxis.major_label_orientation = pi / 4

# Create a histogram of the genres appearing most frequently
genres_data = list(zip(*get_genres(source.data).most_common(10)))
genre_source = ColumnDataSource(data=dict(genre=genres_data[0], number=genres_data[1]))

top_genres = figure(x_range=genres_data[0], plot_height=350, plot_width=500, title="Most Common Genres", sizing_mode='scale_both',
                    tools=[HoverTool(tooltips=[('Genre', '@genre'), ('Appearances', '@number')])])
top_genres.vbar(x='genre', top='number', source=genre_source, width=0.9)
top_genres.yaxis.axis_label = 'Appearances'
top_genres.xaxis.major_label_orientation = pi / 4





def select():
    selection = films_df[(films_df.year >= year_min.value) & (films_df.year <= year_max.value)]
    selection = selection[selection.gross >= gross_slider.value]
    selection = selection[selection.metascore >= rating_slider.value]
    return selection

def update():
    df = select()
    #title	year	genre	imdb_rating	metascore	director	stars	gross
    source.data = dict(title=df['title'], year=df['year'], genre=df['genre'], imdb_rating=df['imdb_rating'],
                      metascore=df['metascore'], director=df['director'], stars=df['stars'], gross=df['gross'])
    
    actors_data = list(zip(*get_actors(source.data).most_common(10)))
    actors_source.data = dict(actors=actors_data[0], number=actors_data[1])
    top_actors.x_range.factors = actors_data[0]
    
    directors_data = list(zip(*get_directors(source.data).most_common(10)))
    directors_source.data = dict(directors=directors_data[0], number=directors_data[1])
    top_directors.x_range.factors = directors_data[0]
    
    genres_data = list(zip(*get_genres(source.data).most_common(10)))
    genre_source.data = dict(genre=genres_data[0], number=genres_data[1])
    top_genres.x_range.factors = genres_data[0]
    
    
update()

year_min.on_change('value', lambda attr, old, new: update())
year_max.on_change('value', lambda attr, old, new: update())
rating_slider.on_change('value', lambda attr, old, new: update())
gross_slider.on_change('value', lambda attr, old, new: update())


layout = row(column(plot, year_min, year_max, gross_slider, rating_slider), column(top_actors, top_directors, top_genres))

curdoc().add_root(layout)
curdoc().title = "Movies"


