import sqlite3
from sqlite3 import Error

import os
import textwrap

def get_db_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print(f"Error '{e}' occured")
    return connection

def execute_read_query(connection, query, params=None):
    cursor = connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    return result

def close_db_connection(connection):
    if connection:
        connection.close()
        return
    else:
        return

def print_about(chosen_actor, connection):
    query = "SELECT about FROM actors WHERE name = ?;"
    about = execute_read_query(connection, query, (chosen_actor, ))
    text = textwrap.fill(about[0][0], width=100, replace_whitespace=False)
    print(text)
    print("\n")

def print_movie_names_and_years(connection, chosen_actor):
    query = """
        SELECT movies.name, movies.year FROM actors 
        JOIN actors_play_movies ON actors.id = actorId 
        JOIN movies ON movies.id = actors_play_movies.movieId
        WHERE actors.name = ?;
        """
    movie_names_and_years = execute_read_query(connection, query, (chosen_actor, ))
    clear_terminal()
    print(f"{chosen_actor}'s movies:\n")
    for movie_name_and_year in movie_names_and_years:
        print(f"{movie_name_and_year[0]}, Year: {movie_name_and_year[1]}")
    print("\n")

def print_awards(connection, chosen_actor):
    query = """
        SELECT awards.name, awards.win, awards.year, 
        awards.category, movies.name FROM awards 
        JOIN actors ON awards.actorId = actors.id 
        JOIN movies on awards.movieId = movies.id 
        WHERE actors.name = ? AND awards.year = ?;
        """
    years_query = """
        SELECT awards.year FROM awards 
        JOIN actors ON awards.actorId = actors.id 
        JOIN movies on awards.movieId = movies.id 
        WHERE actors.name = ?
        ORDER BY awards.year
        """
    
    years = execute_read_query(connection, years_query, (chosen_actor, ))
    print(f"{chosen_actor} has awards between {years[0][0]} and {years[-1][-1]}\n")
    year = input("Enter the year: ")
    awards = execute_read_query(connection, query, (chosen_actor, year))
    clear_terminal()
    if len(awards) == 0:
        print(f"{chosen_actor} has no awards in {year}\n")
    else:
        print(f"{chosen_actor}'s awards in {year}:\n")
        for award in awards:
            print(f"{award[0]}, {award[1]}, {award[3]}, Year: {award[2]}, Movie: {award[4]}")
        print("\n")

def print_genres(connection, chosen_actor):
    query = """
        SELECT DISTINCT genre FROM actors 
        JOIN actors_play_movies ON actors.id = actorId 
        JOIN movies ON movies.id = actors_play_movies.movieId 
        JOIN genres ON actors_play_movies.movieId = genres.movieId 
        WHERE actors.name = ?;
        """
    genres = execute_read_query(connection, query, (chosen_actor, ))
    clear_terminal()
    print(f"{chosen_actor}'s movie genres:\n")
    for genre in genres:
        print(genre[0])
    print("\n")

def print_average_rating(connection, chosen_actor):
    query_avg_rating_overall = """
        SELECT AVG(movies.rating) as avg
        FROM actors JOIN actors_play_movies ON actors.id = actorId 
        JOIN movies ON movies.id = actors_play_movies.movieId
        WHERE actors.name = ?;
        """
    query_avg_rating_each_year = """
        SELECT movies.year, AVG(movies.rating) as avg
        FROM actors JOIN actors_play_movies ON actors.id = actorId 
        JOIN movies ON movies.id = actors_play_movies.movieId
        WHERE actors.name = ?
        GROUP BY movies.year
        ORDER BY movies.year;
        """
    
    print(f"{chosen_actor}'s average movie ratings:\n")

    avg_rating_overall = execute_read_query(connection, query_avg_rating_overall, (chosen_actor, ))
    print(f"Overall average rating: {round(float(avg_rating_overall[0][0]), 2)}")

    avg_rating_each_year = execute_read_query(connection, query_avg_rating_each_year, (chosen_actor, ))
    for entry in avg_rating_each_year:
        print(f"Average rating in {entry[0]}: {round(float(entry[1]), 2)}")
    print("\n")

def print_top_five_movies(connection, chosen_actor):
    query = """
        SELECT movies.name, movies.year, genres.genre, 
        AVG(movies.rating) as avg
        FROM actors JOIN actors_play_movies ON actors.id = actorId 
        JOIN movies ON movies.id = actors_play_movies.movieId
        JOIN genres ON movies.id = genres.movieId
        WHERE actors.name = ?
        GROUP BY movies.name
        ORDER BY avg DESC
        LIMIT 5;
        """
    movies = execute_read_query(connection, query, (chosen_actor, ))
    print(f"{chosen_actor}'s top 5 movies:\n")
    for index, movie in enumerate(movies):
        print(f"{index+1}: {movie[0]}, {round(float(movie[3]), 2)}, {movie[2]}, Year: {movie[1]}")
    print("\n")

def print_options():
    print("\nEnter the option you want to choose: ")
    print("1. About actor/actress")
    print("2. All time movie names and years")
    print("3. Awards in different years")
    print("4. Movie genres")
    print("5. Average rating of movies (overall and each year)")
    print("6. Top five movies, their respective years and genre")

def print_control_flow():
    print("1. Choose a different actor/actress")
    print("2. Show options")
    print("3. Exit program")

def choose_actor(actors):
    choice = input("Enter the number or name of the actor you want to choose: ")
    choice_is_valid = False
    chosen_actor = None
    while True:
        for actor in actors:
            if choice == str(actor[0]) or choice.lower() == actor[1].lower():
                chosen_actor = actor[1]
                choice_is_valid = True
                break
        if choice_is_valid:
            break
        choice = input("Invalid choice! Please re-enter the id or name of the actor you want to choose: ")
    return chosen_actor



def clear_terminal():
    #clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

def print_actors(actors):
    print("List of Actors:")
    for actor in actors:
        print(f"{actor[0]}. {actor[1]}")

connection = get_db_connection('./database.sqlite')
actors = execute_read_query(connection, 'SELECT ranking, name FROM actors')

show_actor_list = True
while True:
    if show_actor_list:
        print_actors(actors)
        chosen_actor = choose_actor(actors)

        clear_terminal()

    print(f"You chose: {chosen_actor}")
    value = None
    while True:
        print_options()
        choice = input()
        clear_terminal()
        try:
            value = int(choice)
            if value >= 1 and value <= 6:
                break
            print("Invalid choice! Choose between 1-6.")
        except ValueError:
            print("Invalid input! Please enter a valid integer.")
    if value == 1:
        print_about(chosen_actor, connection)
    elif value == 2:
        print_movie_names_and_years(connection, chosen_actor)
    elif value == 3:
        print_awards(connection, chosen_actor)
    elif value == 4:
        print_genres(connection, chosen_actor)
    elif value == 5:
        print_average_rating(connection, chosen_actor)
    elif value == 6:
        print_top_five_movies(connection, chosen_actor)

    value = None
    while True:
        print_control_flow()
        choice = input()
        clear_terminal()
        try:
            value = int(choice)
            if value >= 1 and value <= 3:
                break
            print("Invalid choice! Choose between 1-3.")
        except ValueError:
            print("Invalid input! Please enter a valid integer.")

    if value == 1:
        show_actor_list = True
    elif value == 2:
        show_actor_list = False
    elif value == 3:
        break


