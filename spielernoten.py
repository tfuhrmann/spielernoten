# script to read website information from anstoss-online.de
# incl. login with user account
# implemented in python3 (using windows, version 3.7)
# Author: Thomas Fuhrmann, December 2018

# the following modules need to be installed first by executing:
# pip install lxml
# pip install requests
# pip install bs4


# import relevant modules
import sys, os
from lxml import html
import requests
from bs4 import BeautifulSoup


###########################################################
# define the following variables                          #
team = 'FV Pacos de Ferreira' # Team of interest          #
#team = 'DVD Santa Clara' # Team of interest              #
year = 2018  # Year of interest (2018 for 2018/19 season) #
match_day_start = 1 # Period of interest: start match day #
match_day_end = 15 # end match day                        #
username = 'Tommy Fury'                                   #
password = 'mein_password'                                #
###########################################################


# Welcome
print('')
print('Hi. Ich kann Spielernoten aus Spielberichten von anstoss-online.de auslesen.')
print('Gerne berechne ich dir Durchschnittsnoten der Spieler aus dem Team %s fuer die\
 Spieltage %i bis %i der Saison %i/%i.' % (team, match_day_start, match_day_end, year, year+1))
print('')


# get the urls of match reports for one team for all match days of interest
urls = list()
match_day = match_day_start
while match_day <= match_day_end:
    # url for 2 divisao in Portugal, change for other leagues
    url_portugal2 = 'https://www.anstoss-online.de/?do=land;land_id=168;wettbewerb_st_id=240;spieltag_nr='\
     + str(match_day) + ';start_jahr=' + str(year)
    page = requests.get(url_portugal2)
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

# dictioniary to save players and corresponding grades
player_dict = {}
match_day = match_day_start
# loop over all match day urls
for url in urls:
    print('Ich lese gerade die Noten des %i. Spieltags' % match_day)
    # read html information from match day page
    result = session_requests.get(
	url,
	headers = dict(referer = url)
    )
    soup = BeautifulSoup(result.content, 'html.parser')
    # match reports contain two data tables with the name daten_tabelle,
    # one for each team, team_idx is used to select the right one
    teams_line = soup.find('tr')
    dataset = list(td.get_text() for (td) in teams_line.find_all('td'))
    if dataset[0] == team:
        team_idx = 0
    if dataset[1] == team:
        team_idx = 1
    # read both data tables named daten_tabelle
    tables = soup.find_all('table', attrs={'class':'daten_tabelle'})
    # save player names and grades to a list
    players = []
    grades = []
    # read all rows of table for selected team
    for row in tables[team_idx].find_all("tr")[1:]:
        # dataset contains all records, i.e. Position, Nr., Spieler, Note
        dataset = list(td.get_text() for (td) in row.find_all("td"))
        # only the last two records (Spieler and Note) are used
        player = dataset[2]
        grade = dataset[3]
        players.append(player)
        grades.append(grade)
    # save player name and corresponding grade to dictionary
    for player, grade in zip(players, grades):
        player_dict.setdefault(player, []).append(grade)
    match_day = match_day + 1
print('')


# filename of outputfile
outfile = 'spielernoten_' + str(year) + '_' + str(match_day_start) + '-' + \
          str(match_day_end) + '.csv'
os.remove(outfile) if os.path.exists(outfile) else None
f = open(outfile, 'a')
print('Spielername, Anzahl benotete Spiele, Durchschnittsnote', file=f)
# loop over all players in dictionary to calculate average grade
for key, value in player_dict.items():
    count = 0
    sum = 0
    # get all grades for one player and number of graded matches
    for grade in value:
        if grade != '':
            sum = sum + float(grade)
            count = count + 1
    # avoid division by zero when calculating average grade
    if count > 0:
        average_grade = sum/count
        # print output to screen and to file
        print('%s, %i benotete Spiele, Durchschnittsnote: %4.2f' % \
        (key, count, average_grade))
        print('%s, %i, %4.2f' % (key, count, average_grade), file=f)
f.close()

