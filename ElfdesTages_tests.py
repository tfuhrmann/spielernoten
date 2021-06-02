# hosting functions for 11desTages main script

# import relevant modules
import numpy as np
from ElfdesTages_functions import select_squad, generate_output_files


# load test file with sorted player list
filename = './tests/ElfdesTages_playerList_test.txt'
f = open(filename, 'r')
lines = f.readlines()

# default scenario
# append items to 2d list
player_list = []
for line in lines:
    # remove multiple spaces
    line = ' '.join(line.split())
    # split into components and convert to reuqired data format
    a1 = line.split(' ')[0]
    a2 = line.split(' ')[1]
    a3 = line.split(' ')[2]
    a4 = float(line.split(' ')[3])
    a5 = float(line.split(' ')[4])
    a6 = int(line.split(' ')[5])
    a7 = int(line.split(' ')[6])
    player_list.append([a1, a2, a3, a4, a5, a6, a7])

# sort players according to grade, then goals, then strength, then age
player_list.sort(key=lambda x: (x[3], -x[6], x[4], x[5]))

# call algorithm to select squad
goalie, defenders, midfielders, strikers, countD, countM, countS = select_squad(player_list)

print('----------')
print('Scenario 0')
print('----------')
filename_txt = 'tests/test0.txt'
filename_jpg = 'tests/test0.jpg'
generate_output_files(goalie, defenders, midfielders, strikers, countD, countM, countS,\
                      filename_txt, filename_jpg)
print('----------')
print('')


# Scenario 1: many LMs
positions = ['LM','LM','LM','LM','ZM','ZM','RM','ZM','ST','ST','ST','LIB',\
             'MD','MD','MD','LV','LV','RV','ST','ST','ST','ST','ST','TW']

# apply new positions vector to player list
i = 0
for position in positions:
    player_list[i][2] = position
    i += 1

# sort players according to grade, then goals, then strength, then age
player_list.sort(key=lambda x: (x[3], -x[6], x[4], x[5]))

# call algorithm to select squad
goalie, defenders, midfielders, strikers, countD, countM, countS = select_squad(player_list)

print('----------')
print('Scenario 1')
print('----------')
filename_txt = 'tests/test1.txt'
filename_jpg = 'tests/test1.jpg'
generate_output_files(goalie, defenders, midfielders, strikers, countD, countM, countS,\
                      filename_txt, filename_jpg)
print('----------')
print('')


# Scenario 2: many LMs, no good RM
positions = ['LM','LM','LM','LM','ZM','ST','ST','ZM','ST','ST','ST','LIB',\
             'MD','MD','MD','LV','LV','RV','ST','ST','ST','ST','RM','TW']

# apply new positions vector to player list
i = 0
for position in positions:
    player_list[i][2] = position
    i += 1

# sort players according to grade, then goals, then strength, then age
player_list.sort(key=lambda x: (x[3], -x[6], x[4], x[5]))

# call algorithm to select squad
goalie, defenders, midfielders, strikers, countD, countM, countS = select_squad(player_list)

print('----------')
print('Scenario 2')
print('----------')
filename_txt = 'tests/test2.txt'
filename_jpg = 'tests/test2.jpg'
generate_output_files(goalie, defenders, midfielders, strikers, countD, countM, countS,\
                      filename_txt, filename_jpg)
print('----------')
print('')


# Scenario 3: many LVs, no RV check
positions = ['LV','LV','MD','MD','LIB','ST','ST','ZM','ST','ST','ST','LIB',\
             'MD','MD','ZM','LM','LM','RM','ST','ST','ST','ST','RV','TW']

# apply new positions vector to player list
i = 0
for position in positions:
    player_list[i][2] = position
    i += 1

# sort players according to grade, then goals, then strength, then age
player_list.sort(key=lambda x: (x[3], -x[6], x[4], x[5]))

# call algorithm to select squad
goalie, defenders, midfielders, strikers, countD, countM, countS = select_squad(player_list)

print('----------')
print('Scenario 3')
print('----------')
filename_txt = 'tests/test3.txt'
filename_jpg = 'tests/test3.jpg'
generate_output_files(goalie, defenders, midfielders, strikers, countD, countM, countS,\
                      filename_txt, filename_jpg)
print('----------')
print('')


