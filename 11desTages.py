# -*- coding: latin-1 -*-


# script to read website information from anstoss-online.de
# incl. login with user account
# implemented in python3 (using windows, version 3.7)
# Author: Thomas Fuhrmann, December 2018

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
import operator
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


###########################################################
# define the following variables                          #
country_id = 168 # Portugal                               #
# league_id = 240 # 2nd                                     #
# league_id = 304 # 3rd                                     #
# year = 2019  # Year of interest (2018 for 2018/19 season) #
# match_day = 4 # match day of interest #                   #
###########################################################
username = 'Tommy Fury'                                   #
password = 'mein_passwort'                                #
###########################################################


# read variables from command line: league year match_day
# e.g. 11desTages.py 2 2019 5
league = int(sys.argv[1])
year = int(sys.argv[2])
match_day = int(sys.argv[3])


if league == 1:
    league_id = 11
if league == 2:
    league_id = 240
if league == 3:
    league_id = 304


# Welcome
print('')
print('Elf des Tages fuer Spieltag %i der Saison %i/%i, %ia Divisao.' % (match_day, year, year+1, league))
print('')


# url for the country and league
urls = list()
url_id = 'https://www.anstoss-online.de/?do=land;land_id=' + str(country_id) + ';wettbewerb_st_id=' \
 + str(league_id) + ';spieltag_nr=' + str(match_day) + ';start_jahr=' + str(year)
page = requests.get(url_id)
soup = BeautifulSoup(page.content, 'html.parser')
table1 = soup.find('table', attrs={'class':'daten_tabelle'})
player_sa = []
for row in table1.find_all('tr')[1:]:
    # dataset contains all records, i.e. Team1, -, Team2, Ergebnis, Spielbericht
    dataset = list(td.get_text() for (td) in row.find_all('td'))
    # find the url for a particular match
    link = row.find_all('a')
    url_suffix = link[2].get('href')
    url_match = 'https://www.anstoss-online.de' + url_suffix[2:]
    # save to url list
    urls.append(url_match)
    # get the player strengths and ages for team 1
    team1 = dataset[0]
    url_suffix = link[0].get('href')
    url_team = 'https://www.anstoss-online.de/' + url_suffix[:-1] + ';detail=kader'
    page = requests.get(url_team)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table', attrs={'class':'daten_tabelle'})
    for row in table.find_all('tr')[1:]:
        # dataset contains all records, i.e. Position, Spieler, Stärke, Alter, ...
        dataset1 = list(td.get_text() for (td) in row.find_all('td'))
        player = dataset1[1]
        strength = float(dataset1[2])
        age = int(dataset1[3])
        player_sa.append([player, team1, strength, age])
    # get the player strengths and ages for team 2
    team2 = dataset[2]
    url_suffix = link[1].get('href')
    url_team = 'https://www.anstoss-online.de/' + url_suffix[:-1] + ';detail=kader'
    page = requests.get(url_team)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table', attrs={'class':'daten_tabelle'})
    for row in table.find_all('tr')[1:]:
        # dataset contains all records, i.e. Position, Spieler, Stärke, Alter, ...
        dataset2 = list(td.get_text() for (td) in row.find_all('td'))
        player = dataset2[1]
        strength = float(dataset2[2])
        age = int(dataset2[3])
        player_sa.append([player, team2, strength, age])


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
player_list = []
# loop over all match day urls
match = 0
for url in urls:
    match = match + 1
    print('Ich lese gerade die Noten des %i. Spiels' % match)
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
    team1 = dataset[0]
    team2 = dataset[1]
    # read both data tables named daten_tabelle
    tables = soup.find_all('table', attrs={'class':'daten_tabelle'})
    # read all rows of table for 1st team
    for row in tables[0].find_all("tr")[1:]:
        # dataset contains all records, i.e. Position, Nr., Spieler, Note
        dataset = list(td.get_text() for (td) in row.find_all("td"))
        # only the last two records (Spieler and Note) are used
        position = dataset[0]
        player = dataset[2]
        grade = dataset[3]
        if grade!= '':
            for row in player_sa:
                if row[0] == player and row[1] == team1:
                    strength = row[2]
                    age = row[3]
                    break
            # for player, grade, position, strength, age in zip(players, grades, positions, strenghts, ages):
            player_list.append([player, team1, position, float(grade), strength, age])
            #player_dict.setdefault(player, []).append([float(grade), position, team1, strength, age])
    # read all rows of table for 2nd team
    for row in tables[1].find_all("tr")[1:]:
        # dataset contains all records, i.e. Position, Nr., Spieler, Note
        dataset = list(td.get_text() for (td) in row.find_all("td"))
        # only the last two records (Spieler and Note) are used
        position = dataset[0]
        player = dataset[2]
        grade = dataset[3]
        if grade!= '':
            for row in player_sa:
                if row[0] == player and row[1] == team2:
                    strength = row[2]
                    age = row[3]
                    break
            # save player name and corresponding grade to dictionary
            player_list.append([player, team2, position, float(grade), strength, age])
            #player_dict.setdefault(player, []).append([float(grade), position, team2, strength, age])
print('')


# sort players according to grade, then strength, then age
player_list.sort(key=lambda x: (x[3], x[4], x[5]))


print('')
# get best goalkeeper
count = 0
i = 0
goalie = []
while count < 1:
    position = player_list[i][2]
    if position == 'TW':
        goalie = player_list[i]
        count = count + 1
    i = i + 1


# get 5 best defenders
count = 0
i = 0
defenders = []
defense_pos = ['LV','RV','LIB','MD'] # LV RV not given here
while count < 5:
    position = player_list[i][2]
    if any(position in x for x in defense_pos):
        defenders.append(player_list[i])
        count = count + 1
    i = i + 1


# get 5 best midfielders
count = 0
i = 0
midfielders = []
midfield_pos = ['LM','RM', 'ZM'] # LM RM not given here
while count < 5:
    position = player_list[i][2]
    if any(position in x for x in midfield_pos):
        midfielders.append(player_list[i])
        count = count + 1
    i = i + 1


# get 3 best strikers
count = 0
i = 0
strikers = []
while count < 3:
    position = player_list[i][2]
    if position == 'ST':
        strikers.append(player_list[i])
        count = count + 1
    i = i + 1


three_of_six = []
three_of_six.append(defenders[3])
three_of_six.append(defenders[4])
three_of_six.append(midfielders[3])
three_of_six.append(midfielders[4])
three_of_six.append(strikers[1])
three_of_six.append(strikers[2])
# sort players according to grade, then strength, then age
three_of_six.sort(key=lambda x: (x[3], x[4], x[5]))
print('')


# add defenders/midfielders/strikers to formation of the day
countD = 0
countM = 0
countS = 0
position = three_of_six[0][2]
if any(position in x for x in defense_pos):
    countD = countD + 1
if any(position in x for x in midfield_pos):
    countM = countM + 1
if position == 'ST':
    countS = countS + 1
position = three_of_six[1][2]
if any(position in x for x in defense_pos):
    countD = countD + 1
if any(position in x for x in midfield_pos):
    countM = countM + 1
if position == 'ST':
    countS = countS + 1
position = three_of_six[2][2]
if any(position in x for x in defense_pos):
    countD = countD + 1
if any(position in x for x in midfield_pos):
    countM = countM + 1
if position == 'ST':
    countS = countS + 1


# print to command line, file and as image overlay
print('Elf des %i. Spieltages:' % match_day)


# make dir if it doesn't exist yet
dirname = str(league) + 'a'
if not os.path.exists(dirname):
    os.mkdir(dirname)

# output file
savefile = str(league) + 'a/11_des_Tages_Spieltag' + str(match_day) + '.txt'
text_file = open(savefile, "w")
text_file.write('Name                           Team                         Position Note Stärke Alter\n')
text_file.write('--------------------------------------------------------------------------------------\n')

# input image
img = Image.open("soccer_field.jpg")
draw = ImageDraw.Draw(img)


# function for text overlays
def draw_text(bbox, text):
    font = ImageFont.truetype("gishabd.ttf", 20)
    x1, y1, x2, y2 = bounding_box
    w, h = draw.textsize(text, font=font)
    x = (x2 - x1 - w)/2 + x1
    y = (y2 - y1 - h)/2 + y1
#    draw.rectangle([x1-10, y1, x2+10, y2], (255,255,255,100))
# opacity is not working
    draw.text((x, y), text, (0,0,0), align='center', font=font)


print('Tor')
text_file.write('Tor:\n')
print(goalie)
text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
(goalie[0], goalie[1], goalie[2], goalie[3], goalie[4], goalie[5]))
text = goalie[0] + ' (' + str(goalie[3]) + ')\n' + goalie[1]
bounding_box = [448, 650, 686, 700]
draw_text(bounding_box, text)

print('Abwehr')
text_file.write('Abwehr:\n')
if countD == 0:
    print(defenders[0])
    print(defenders[1])
    print(defenders[2])
    i = 0
    while i < 3:
        text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
        (defenders[i][0], defenders[i][1], defenders[i][2], defenders[i][3], defenders[i][4], defenders[i][5]))
        i = i + 1
    # print defense 3
    text = defenders[0][0] + ' (' + str(defenders[0][3]) + ')\n' + defenders[0][1]
    bounding_box = [148, 460, 386, 510]
    draw_text(bounding_box, text)
    text = defenders[1][0] + ' (' + str(defenders[1][3]) + ')\n' + defenders[1][1]
    bounding_box = [448, 460, 686, 510]
    draw_text(bounding_box, text)
    text = defenders[2][0] + ' (' + str(defenders[2][3]) + ')\n' + defenders[2][1]
    bounding_box = [748, 460, 986, 510]
    draw_text(bounding_box, text)
if countD == 1:
    print(defenders[0])
    print(defenders[1])
    print(defenders[2])
    print(defenders[3])
    i = 0
    while i < 4:
        text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
        (defenders[i][0], defenders[i][1], defenders[i][2], defenders[i][3], defenders[i][4], defenders[i][5]))
        i = i + 1
    # print defense 4
    text = defenders[0][0] + ' (' + str(defenders[0][3]) + ')\n' + defenders[0][1]
    bounding_box = [48, 460, 286, 510]
    draw_text(bounding_box, text)
    text = defenders[1][0] + ' (' + str(defenders[1][3]) + ')\n' + defenders[1][1]
    bounding_box = [306, 510, 544, 560]
    draw_text(bounding_box, text)
    text = defenders[2][0] + ' (' + str(defenders[2][3]) + ')\n' + defenders[2][1]
    bounding_box = [590, 510, 828, 560]
    draw_text(bounding_box, text)
    text = defenders[3][0] + ' (' + str(defenders[3][3]) + ')\n' + defenders[3][1]
    bounding_box = [848, 460, 1086, 510]
    draw_text(bounding_box, text)
if countD == 2:
    print(defenders[0])
    print(defenders[1])
    print(defenders[2])
    print(defenders[3])
    print(defenders[4])
    i = 0
    while i < 5:
        text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
        (defenders[i][0], defenders[i][1], defenders[i][2], defenders[i][3], defenders[i][4], defenders[i][5]))
        i = i + 1
    # print defense 5
    text = defenders[0][0] + ' (' + str(defenders[0][3]) + ')\n' + defenders[0][1]
    bounding_box = [48, 460, 286, 510]
    draw_text(bounding_box, text)
    text = defenders[1][0] + ' (' + str(defenders[1][3]) + ')\n' + defenders[1][1]
    bounding_box = [248, 510, 486, 560]
    draw_text(bounding_box, text)
    text = defenders[2][0] + ' (' + str(defenders[2][3]) + ')\n' + defenders[2][1]
    bounding_box = [448, 460, 686, 510]
    draw_text(bounding_box, text)
    text = defenders[3][0] + ' (' + str(defenders[3][3]) + ')\n' + defenders[3][1]
    bounding_box = [648, 510, 886, 560]
    draw_text(bounding_box, text)
    text = defenders[4][0] + ' (' + str(defenders[4][3]) + ')\n' + defenders[4][1]
    bounding_box = [848, 460, 1086, 510]
    draw_text(bounding_box, text)

print('Mittelfeld')
text_file.write('Mittelfeld:\n')
if countM == 0:
    print(midfielders[0])
    print(midfielders[1])
    print(midfielders[2])
    i = 0
    while i < 3:
        text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
        (midfielders[i][0], midfielders[i][1], midfielders[i][2], midfielders[i][3], midfielders[i][4], midfielders[i][5]))
        i = i + 1
    # print midfield 3
    text = midfielders[0][0] + ' (' + str(midfielders[0][3]) + ')\n' + midfielders[0][1]
    bounding_box = [148, 270, 386, 320]
    draw_text(bounding_box, text)
    text = midfielders[0][0] + ' (' + str(midfielders[0][3]) + ')\n' + midfielders[0][1]
    bounding_box = [448, 270, 686, 320]
    draw_text(bounding_box, text)
    text = midfielders[0][0] + ' (' + str(midfielders[0][3]) + ')\n' + midfielders[0][1]
    bounding_box = [748, 270, 986, 320]
    draw_text(bounding_box, text)
if countM == 1:
    print(midfielders[0])
    print(midfielders[1])
    print(midfielders[2])
    print(midfielders[3])
    i = 0
    while i < 4:
        text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
        (midfielders[i][0], midfielders[i][1], midfielders[i][2], midfielders[i][3], midfielders[i][4], midfielders[i][5]))
        i = i + 1
    # print midfield 4
    text = midfielders[0][0] + ' (' + str(midfielders[0][3]) + ')\n' + midfielders[0][1]
    bounding_box = [48, 270, 286, 320]
    draw_text(bounding_box, text)
    text = midfielders[1][0] + ' (' + str(midfielders[1][3]) + ')\n' + midfielders[1][1]
    bounding_box = [306, 320, 544, 370]
    draw_text(bounding_box, text)
    text = midfielders[2][0] + ' (' + str(midfielders[2][3]) + ')\n' + midfielders[2][1]
    bounding_box = [590, 320, 828, 370]
    draw_text(bounding_box, text)
    text = midfielders[3][0] + ' (' + str(midfielders[3][3]) + ')\n' + midfielders[3][1]
    bounding_box = [848, 270, 1086, 320]
    draw_text(bounding_box, text)
if countM == 2:
    print(midfielders[0])
    print(midfielders[1])
    print(midfielders[2])
    print(midfielders[3])
    print(midfielders[4])
    i = 0
    while i < 5:
        text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
        (midfielders[i][0], midfielders[i][1], midfielders[i][2], midfielders[i][3], midfielders[i][4], midfielders[i][5]))
        i = i + 1
    # print midfield 5
    text = midfielders[0][0] + ' (' + str(midfielders[0][3]) + ')\n' + midfielders[0][1]
    bounding_box = [48, 270, 286, 320]
    draw_text(bounding_box, text)
    text = midfielders[1][0] + ' (' + str(midfielders[1][3]) + ')\n' + midfielders[1][1]
    bounding_box = [248, 320, 486, 370]
    draw_text(bounding_box, text)
    text = midfielders[2][0] + ' (' + str(midfielders[2][3]) + ')\n' + midfielders[2][1]
    bounding_box = [448, 270, 686, 320]
    draw_text(bounding_box, text)
    text = midfielders[3][0] + ' (' + str(midfielders[3][3]) + ')\n' + midfielders[3][1]
    bounding_box = [648, 320, 886, 370]
    draw_text(bounding_box, text)
    text = midfielders[4][0] + ' (' + str(midfielders[4][3]) + ')\n' + midfielders[4][1]
    bounding_box = [848, 270, 1086, 320]
    draw_text(bounding_box, text)
print('Sturm')
text_file.write('Sturm:\n')
if countS == 0:
    print(strikers[0])
    text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
    (strikers[0][0], strikers[0][1], strikers[0][2], strikers[0][3], strikers[0][4], strikers[0][5]))
    # print offense 1
    text = strikers[0][0] + ' (' + str(strikers[0][3]) + ')\n' + strikers[0][1]
    bounding_box = [448, 90, 686, 140]
    draw_text(bounding_box, text)
if countS == 1:
    print(strikers[0])
    print(strikers[1])
    i = 0
    while i < 2:
        text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
        (strikers[i][0], strikers[i][1], strikers[i][2], strikers[i][3], strikers[i][4], strikers[i][5]))
        i = i + 1
    # print offense 2
    text = strikers[0][0] + ' (' + str(strikers[0][3]) + ')\n' + strikers[0][1]
    bounding_box = [248, 90, 486, 140]
    draw_text(bounding_box, text)
    text = strikers[1][0] + ' (' + str(strikers[1][3]) + ')\n' + strikers[1][1]
    bounding_box = [648, 90, 886, 140]
    draw_text(bounding_box, text)
if countS == 2:
    print(strikers[0])
    print(strikers[1])
    print(strikers[2])
    i = 0
    while i < 3:
        text_file.write('%-30s %-30s %-4s    %3.1f  %4.1f   %2i\n' % \
        (strikers[i][0], strikers[i][1], strikers[i][2], strikers[i][3], strikers[i][4], strikers[i][5]))
        i = i + 1
    # print offense 3
    text = strikers[0][0] + ' (' + str(strikers[0][3]) + ')\n' + strikers[0][1]
    bounding_box = [148, 90, 386, 140]
    draw_text(bounding_box, text)
    text = strikers[1][0] + ' (' + str(strikers[1][3]) + ')\n' + strikers[1][1]
    bounding_box = [448, 90, 686, 140]
    draw_text(bounding_box, text)
    text = strikers[2][0] + ' (' + str(strikers[2][3]) + ')\n' + strikers[2][1]
    bounding_box = [748, 90, 986, 140]
    draw_text(bounding_box, text)

# close text file
text_file.close()


# print licence
font_small = ImageFont.truetype("arial.ttf", 14)
draw.text((924, 751),'Background Image: Freepic.com',(255,255,255),align='center',font=font_small)
# save as new image
savename = str(league) + 'a/11_des_Tages_Spieltag' + str(match_day) + '.jpg'
img.save(savename)
print('')

