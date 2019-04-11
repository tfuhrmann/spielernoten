# -*- coding: latin-1 -*-


# script to read website information from anstoss-online.de
# incl. login with user account
# implemented in python3 (using windows, version 3.7)
# Author: Thomas Fuhrmann, April 2019

# the following modules need to be installed first by executing:
# pip install lxml
# pip install requests
# pip install bs4
# pip install numpy
# pip install matplotlib


# import relevant modules
import sys, os
from lxml import html
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt


###########################################################
# define the following variables                          #
#player_id = 126153 # Jan Lubo                            #
player_id = 127583 # Sasa August                          #
year = 2018  # Year of interest (2018 for 2018/19 season) #
username = 'Tommy Fury'                                   #
password = 'mein_password'                                #
###########################################################

# get player name
url_player = 'https://www.anstoss-online.de/?do=spieler;spieler_id=' + str(player_id)
page = requests.get(url_player)
soup = BeautifulSoup(page.content, 'html.parser')
player_name = soup.find('h1').text
player_name = player_name[:-1]

# Welcome
print('')
print('Hi. Ich kann dir Infos zu einem Spieler von anstoss-online.de auslesen.')
print('Gerne gebe ich dir eine Übersicht über Noten, Einsatzzeiten, Tore und Karten des Spielers %s fuer die \
Saison %i/%i.' % (player_name, year, year+1))
print('')


# find the team of the player for the given period
table = soup.find('table', attrs={'class':'daten_tabelle'})
for row in table.find_all('tr')[1:]:
    # dataset contains Verein, Ab, Bis, ...
    dataset = list(td.get_text() for (td) in row.find_all('td'))
    start_date = dataset[1]
    end_date = dataset[2]
    start_year = int(start_date[6:10])
    start_month = int(start_date[3:5])
    end_year = int(end_date[6:10])
    end_month = int(end_date[3:5])
    count = 0
    if (year > start_year or (year == start_year and month >= 8)) and \
       (year < end_year or (year == end_year and month <= 6)):
        team = dataset[0]
        link = row.find_all('a')
        url_suffix = link[0].get('href')
        count = count + 1
if count == 0:
    print('Kein Team gefunden.')
    sys.exit()
elif count > 1:
    print('Achtung: Spieler war in der Saison %i/%1 bei mehreren Teams unter Vertrag. \
Nur Einsätze beim späteren Verein, %s werden ausgewertet.' % (year, year+1, team))
# hier könnte man auch Statistiken für mehrere Vereine implementieren
else:
    print('Einsätze in der Saison %i/%i für den Verein %s werden ausgewertet.' % (year, year+1, team))
url_team = 'https://www.anstoss-online.de' + url_suffix
page = requests.get(url_team)
soup = BeautifulSoup(page.content, 'html.parser')
rows = soup.select('tr')
for row in rows:
    dataset = list(td.get_text() for (td) in row.find_all('td'))
    if dataset[0] == 'Liga:':
        link = row.find_all('a')
        url_suffix = link[0].get('href')
url_league = 'https://www.anstoss-online.de/' + url_suffix[:-1]
page = requests.get(url_league)
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find('table', attrs={'class':'daten_tabelle'})
for row in table.find_all('tr')[1:]:
    # dataset contains all records, i.e. Team1, -, Team2, Ergebnis, Spielbericht
    dataset = list(td.get_text() for (td) in row.find_all('td'))
    if dataset[0] == team:
        # find the url for a particular team
        link = row.find_all('a')
        url_suffix = link[0].get('href')
        url_team = 'https://www.anstoss-online.de/' + url_suffix[:-1] + ';detail=kader'
    if dataset[2] == team:
        # find the url for a particular team
        link = row.find_all('a')
        url_suffix = link[1].get('href')
        url_team = 'https://www.anstoss-online.de/' + url_suffix[:-1] + ';detail=kader'
team_id = url_team.split('verein_id=',1)[1]
team_id = team_id[:-13]


# get the urls of match reports for one team for all match days of interest
urls = list()
match_day_start = 1
match_day_end = 34
match_day = match_day_start
while match_day <= match_day_end:
    # url for league and macht day
    url_match_day = url_league + 'spieltag_nr=' + str(match_day) + ';start_jahr=' + str(year)
    page = requests.get(url_match_day)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table', attrs={'class':'daten_tabelle'})
    for row in table.find_all('tr')[1:]:
        # dataset contains all records, i.e. Team1, -, Team2, Ergebnis, Spielbericht
        dataset = list(td.get_text() for (td) in row.find_all('td'))
        if dataset[0] == team or dataset[2] == team:
            # find the url for a particular match day
            link = row.find_all('a')
            url_suffix = link[2].get('href')
            url_match = 'https://www.anstoss-online.de' + url_suffix[2:]
    match_day = match_day + 1
    # save to url list
    urls.append(url_match)


# start session, login with given credentials
print('Da die Spielernoten nur fuer registrierte Nutzer sichtbar sind, werde ich\
 mich jetzt mit dem Account %s auf www.anstoss-online.de einloggen' % username)
print('')
session_requests = requests.session()
login_url = 'https://www.anstoss-online.de/content/fixed/login.php'
result = session_requests.get(login_url)
payload = {
    'login_name': username,
    'login_pw': password
}
result = session_requests.post(
	login_url,
	data = payload,
	headers = dict(referer=login_url)
)


match_day = match_day_start
# save player names and grades to a list
match_days = []
grades = []
minutes_played = []
goals = []
yellow_cards = []
yellowred_cards = []
red_cards = []
# loop over all match day urls
for url in urls:
    print('Ich lese gerade Statistiken für den %i. Spieltag' % match_day)
    match_days.append(match_day)
    played = 0;
    # read html information from match day page
    result = session_requests.get(
	url,
	headers = dict(referer = url)
    )
    soup = BeautifulSoup(result.content, 'html.parser')
    # match reports contain two data tables with the name daten_tabelle,
    # one for each team, team_idx is used to select the right one
    teams_line = soup.find('tr')
    if teams_line == None:
        # when empty, break out of loop
        print('Spieltag ' + str(match_day) + ' wurde noch nicht ausgewertet. ' + \
        'Statistiken bis Spieltag ' + str(match_day-1) + ' werden ausgegeben.')
        break
    dataset = list(td.get_text() for (td) in teams_line.find_all('td'))
    if dataset[0] == team:
        team_idx = 0
    if dataset[1] == team:
        team_idx = 1
    # read both data tables named daten_tabelle
    tables = soup.find_all('table', attrs={'class':'daten_tabelle'})
    # read all rows of table for selected team
    for row in tables[team_idx].find_all("tr")[1:]:
        # dataset contains all records, i.e. Posfor row in tables[team_idx].find_all("tr")[1:]:ition, Nr., Spieler, Note
        dataset = list(td.get_text() for (td) in row.find_all("td"))
        # only the last two records (Spieler and Note) are used
        player = dataset[2]
        grade = dataset[3]
        if player == player_name and grade != '':
            played = 1
            grades.append(float(grade))
    if played == 1:
        match_id = url.split('spiel_id=',1)[1]
        match_id = match_id[:-1]
        url_stats = 'https://www.anstoss-online.de/content/getContent.php?dyn=statistiksystem;' + \
        'spiel_id=' + match_id + ';statistik=spiele_einsaetze;verein_id=' + team_id
        result = session_requests.get(
            url_stats,
            headers = dict(referer = url_stats)
        )
        soup = BeautifulSoup(result.content, 'html.parser')
        table = soup.find('table', attrs={'class':'daten_tabelle'})
        for row in table.find_all("tr")[1:]:
        # dataset contains all records, i.e. Posfor row in tables[team_idx].find_all("tr")[1:]:ition, Nr., Spieler, Note
            dataset = list(td.get_text() for (td) in row.find_all("td"))
            player = dataset[1]
            if player == player_name:
                minutes_played.append(int(dataset[8]))
        # open page containing info on goals and cards
        url_stats2 = 'https://www.anstoss-online.de/content/' + \
        'getContent.php?dyn=spielbericht;spiel_id=' + match_id
        result = session_requests.get(
            url_stats2,
            headers = dict(referer = url_stats2)
        )
        soup = BeautifulSoup(result.content, 'html.parser')
        raw = soup.find_all('script')
        text = str(raw)
        idx1 = text.find('var steno =')
        idx2 = text.find('var wechsel =')
        steno = text[idx1:idx2]
        player_string = 'spieler_id=' + str(player_id)
        idx = [n for n in range(len(steno)) if steno.find(player_string, n) == n]
        xgoal = 0
        ycard = 0
        yrcard = 0
        rcard = 0
        for i in range(len(idx)):
            test_str = (steno[idx[i]-90:idx[i]])
            if test_str.find('Tor') > 0:
                xgoal = xgoal + 1;
            if test_str.find('Gelbe Karte') > 0:
                ycard = 1;
            if test_str.find('Gelbrote Karte') > 0:
                yrcard = 1;
                ycard = 0;
            if test_str.find('Rote Karte') > 0:
                rcard = 1;
            # add red and yellow_red cards
        goals.append(xgoal)
        yellow_cards.append(ycard)
        yellowred_cards.append(yrcard)
        red_cards.append(rcard)
    if played == 0:
        grades.append(float('nan'))
        minutes_played.append(0)
        goals.append(0)
        yellow_cards.append(0)
        yellowred_cards.append(0)
        red_cards.append(0)
    match_day = match_day + 1
print('')


# filename of outputfile
outfile = 'stats_' + player_name + str(year) + '_' + str(match_days[0]) + '-' + \
          str(match_days[-1]) + '.csv'
os.remove(outfile) if os.path.exists(outfile) else None
f = open(outfile, 'a')
# print output to screen and to file
print('********************************************************************')
print('%s - Saison %i/%i' % (player_name, year, year+1))
print('********************************************************************')
print('Spieltag   Note  Minuten  Tore  GelbeKarte  GelbroteKarte  RoteKarte')
print('Spieltag, Note, Minuten, Tore, Gelbe Karten', file=f)
count = 0
grade_sum = 0
minutes_sum = 0
goal_sum = 0
y_card_sum = 0
yr_card_sum = 0
r_card_sum = 0
for match_day, grade, minutes, goal, y_card, yr_card, r_card in \
zip(match_days, grades, minutes_played, goals, yellow_cards, yellowred_cards, red_cards):
    if grade > 0:
        count = count + 1
        grade_sum = grade_sum + grade
        minutes_sum = minutes_sum + minutes
        goal_sum = goal_sum + goal
        y_card_sum = y_card_sum + y_card
        yr_card_sum = yr_card_sum + yr_card
        r_card_sum = r_card_sum + r_card
    print('      %2i    %3.1f       %2i    %2i           %i              %i          %i' \
    % (match_day, grade, minutes, goal, y_card, yr_card, r_card))
    print('%i, %4.2f, %i, %i, %i, %i, %i' % (match_day, grade, minutes, goal, y_card, yr_card, r_card), file=f)
f.close()
average_grade = round(grade_sum/count,2)
average_minutes = round(minutes_sum/count)
print('---------------------------------------------------------------------------')
print('  Total:   %4.2f       %2i    %2i          %2i             %2i         %2i' \
    % (average_grade, average_minutes, goal_sum, y_card_sum, yr_card_sum, r_card_sum))
