# -*- coding: latin-1 -*-

# hosting functions for ElfdesTages main script

# import relevant modules
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def select_squad(player_list):
    """algorithm to select best eleven players, according to possible formations

    Parameters
    ----------
    player_list : list
        a list containing information for all players in the start formation of the teams
        fields are playerName (str), teamName (str), position (str), grade (float),
        strength (float), age (int), goals (int)

    Returns
    -------
    goalie, defenders, midfielders, strikers : list
        lists containing the same infromation as player_list for the individual positions
        length of lists is goalie: 1, defenders: 5, midfielders: 5, strikers: 3
    countD, countM, countS : int
        number of additionally selected players per positions (defender, midfielder, striker)
        initially 3 defenders, 3 midfielders and 1 striker is selected, up to 2 additional
        players are then added per position, defining the formation of the squad
    """

    #
    # input: player_list: array containing
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

    # get maximum of 5 best defenders, considering maximum numbers per position
    count = 0
    count_lv = 0
    count_lv_max = 1
    count_rv = 0
    count_rv_max = 1
    count_lib = 0
    count_lib_max = 1
    count_md = 0
    count_md_max = 2
    i = 0
    defenders = []
    defense_pos = ['LV','RV','LIB','MD'] # LVRV not given here
    while count < 5:
        position = player_list[i][2]
    #    if any(position in x for x in defense_pos):
        if position == 'LV':
            count_lv += 1
            if count_lv <= count_lv_max:
                defenders.append(player_list[i])
                count += 1
        if position == 'RV':
            count_rv += 1
            if count_rv <= count_rv_max:
                defenders.append(player_list[i])
                count += 1
        if position == 'LIB':
            count_lib += 1
            if count_lib <= count_lib_max:
                defenders.append(player_list[i])
                count += 1
        if position == 'MD':
            count_md += 1
            if count_md <= count_md_max:
                defenders.append(player_list[i])
                count += 1
        i = i + 1

    # get maximum of 5 best midfielders, considering maximum numbers per position
    count = 0
    count_lm = 0
    count_lm_max = 2
    count_rm = 0
    count_rm_max = 2
    count_zm = 0
    count_zm_max = 3
    # two LMs are only possible if there is at least one RM selected (and the other way round)
    i = 0
    midfielders = []
    midfield_pos = ['LM','RM', 'ZM'] # LMRM not given here
    while count < 5:
    # hier ist noch was falsch beim Vergleich der lm/rm counts wenn zwei lm/rm gewaehlt werden
        position = player_list[i][2]
    #    if any(position in x for x in defense_pos):
        if position == 'LM':
            count_lm += 1
            if count_lm <= count_lm_max:
                midfielders.append(player_list[i])
                if count_lm == count_lm_max:
                    idx_lm2 = count # needed to potentially replace LM by next player in list
                count += 1
        if position == 'RM':
            count_rm += 1
            if count_rm <= count_rm_max:
                midfielders.append(player_list[i])
                if count_rm == count_rm_max:
                    idx_rm2 = count # needed to potentially replace RM by next player in list
                count += 1
        if position == 'ZM':
            count_zm += 1
            if count_zm <= count_zm_max:
                midfielders.append(player_list[i])
                count += 1
        i = i + 1
    # check if there are two LMs or RMs
    if count_lm == 2 and count_rm == 0:
        # replace last LM in list by next non-LM player
        i = 5 # start with 6th player in list
        found = 0
        while found == 0:
            position = player_list[i][2]
            if position == 'RM' or position == 'ZM':
                midfielders[idx_lm2] = player_list[i]
                found = 1
            i = i + 1
    if count_rm == 2 and count_lm == 0:
        # replace last RM in list by next non-RM player
        i = 5 # start with 6th player in list
        found = 0
        while found == 0:
            position = player_list[i][2]
            if position == 'LM' or position == 'ZM':
                midfielders[idx_rm2] = player_list[i]
                found = 1
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
    # sort players according to grade, goals, then strength, then age
    three_of_six.sort(key=lambda x: (x[3], -x[6], x[4], x[5]))


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

    return goalie, defenders, midfielders, strikers, countD, countM, countS


def get_lib_idx(positions):
    """ function to return index of LIB (if a LIB was selected)
    Parameters
    ----------
    positions : list
        a list containing the positions of selected players
    Returns
    -------
    index of LIB (or -1 if no LIB in positions) : int
    """
    try:
       return positions.index('LIB')
    except ValueError:
       return -1


def draw_text(bounding_box, text, draw):
    """ function for text overlays
    Parameters
    ----------
    bounding_box :
        a list containing the bounding box position of the text object (4 values)
    text : str
        text to be drawn
    draw : PIL image draw object
    Returns
    -------
    -
    """
    font = ImageFont.truetype("calibrib.ttf", 20)
    x1, y1, x2, y2 = bounding_box
    w, h = draw.textsize(text, font=font)
    x = (x2 - x1 - w)/2 + x1
    y = (y2 - y1 - h)/2 + y1
    draw.text((x, y), text, (0,0,0), align='center', font=font)


def generate_output_files(goalie, defenders, midfielders, strikers, countD, countM, countS,\
                          filename_txt, filename_jpg):
    """function to generate the output text file and output image

    Parameters
    ----------
    goalie, defenders, midfielders, strikers : list
        lists containing the same infromation as player_list for the individual positions
        length of lists is goalie: 1, defenders: 5, midfielders: 5, strikers: 3
    countD, countM, countS : int
        number of additionally selected players per positions (defender, midfielder, striker)
        initially 3 defenders, 3 midfielders and 1 striker is selected, up to 2 additional
        players are then added per position, defining the formation of the squad
    filename_txt, filename_jpg : str
        path to output files for the text file and the image file

    Returns
    -------
    -
    """

    text_file = open(filename_txt, "w")
    text_file.write('Name                           Team                         Position Note Tore Stärke Alter\n')
    text_file.write('-------------------------------------------------------------------------------------------\n')

    # input image used as background
    img = Image.open("soccer_field.jpg")
    # PIL draw object
    draw = ImageDraw.Draw(img)


    # print goalie to text file and on image
    print('Tor')
    text_file.write('Tor:\n')
    print(goalie)
    text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
    (goalie[0], goalie[1], goalie[2], goalie[3], goalie[6], goalie[4], goalie[5]))
    text = goalie[0] + ' (' + str(goalie[3]) + ')\n' + goalie[1]
    bounding_box = [448, 650, 686, 700]
    draw_text(bounding_box, text, draw)


    # print defenders to text file and in image
    print('Abwehr')
    text_file.write('Abwehr:\n')
    # print 3 defenders
    if countD == 0:
        print(defenders[0])
        print(defenders[1])
        print(defenders[2])
        i = 0
        positions = [] # needed to select postion on the plot
        while i < 3:
            text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
            (defenders[i][0], defenders[i][1], defenders[i][2], defenders[i][3], defenders[i][6], defenders[i][4], defenders[i][5]))
            positions.append(defenders[i][2])
            i = i + 1
        # allocate a bounding box index according to following order: LV, MD, RV
        # LIB will always be in the centre
        bbox_idx = [0, 0, 0]
        bbox_idx_used = 0
        i = 0
        while i < 3:
            if positions[i] == 'LV':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 3:
            if positions[i] == 'MD':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 3:
            if positions[i] == 'RV':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        # check if LIB was selected
        idx_lib = get_lib_idx(positions)
        if idx_lib > -1:
            # move current player on bbox position 1 to bbox position 2
            idx_curr = bbox_idx.index(1)
            bbox_idx[idx_curr] = 2
            bbox_idx[idx_lib] = 1
        bounding_boxes = [[148, 460, 386, 510],[448, 460, 686, 510],[748, 460, 986, 510]]
        text = defenders[0][0] + ' (' + str(defenders[0][3]) + ')\n' + defenders[0][1]
        bounding_box = bounding_boxes[bbox_idx[0]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[1][0] + ' (' + str(defenders[1][3]) + ')\n' + defenders[1][1]
        bounding_box = bounding_boxes[bbox_idx[1]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[2][0] + ' (' + str(defenders[2][3]) + ')\n' + defenders[2][1]
        bounding_box = bounding_boxes[bbox_idx[2]][:]
        draw_text(bounding_box, text, draw)
    # 4 defenders
    if countD == 1:
        print(defenders[0])
        print(defenders[1])
        print(defenders[2])
        print(defenders[3])
        i = 0
        positions = [] # needed to select postion on the plot
        while i < 4:
            text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
            (defenders[i][0], defenders[i][1], defenders[i][2], defenders[i][3], defenders[i][6], defenders[i][4], defenders[i][5]))
            positions.append(defenders[i][2])
            i = i + 1
        # allocate a bounding box index according to following order: LV, MD, RV
        # LIB will be on position 2 or 3: LV-LIB-MD-RV or MD-LIB-MD-RV or LV-MD-LIB-MD
        bbox_idx = [0, 0, 0, 0]
        bbox_idx_used = 0
        i = 0
        while i < 4:
            if positions[i] == 'LV':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 4:
            if positions[i] == 'MD':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 4:
            if positions[i] == 'RV':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        # check if LIB was selected
        idx_lib = get_lib_idx(positions)
        if idx_lib > -1:
            # check if current players at bbox positions 1 and 2 are both MD (special case)
            idx_curr1 = bbox_idx.index(1)
            idx_curr2 = bbox_idx.index(2)
            if positions[idx_curr1] == 'MD' and positions[idx_curr1] == 'MD':
                # move current player on bbox position 2 to bbox position 3
                bbox_idx[idx_curr2] = 3
                bbox_idx[idx_lib] = 2
            else:
                # move current player on bbox position 1 to bbox position 2
                bbox_idx[idx_curr1] = 2
                bbox_idx[idx_lib] = 1
        bounding_boxes = [[48, 460, 286, 510],[306, 510, 544, 560],[590, 510, 828, 560],[848, 460, 1086, 510]]
        text = defenders[0][0] + ' (' + str(defenders[0][3]) + ')\n' + defenders[0][1]
        bounding_box = bounding_boxes[bbox_idx[0]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[1][0] + ' (' + str(defenders[1][3]) + ')\n' + defenders[1][1]
        bounding_box = bounding_boxes[bbox_idx[1]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[2][0] + ' (' + str(defenders[2][3]) + ')\n' + defenders[2][1]
        bounding_box = bounding_boxes[bbox_idx[2]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[3][0] + ' (' + str(defenders[3][3]) + ')\n' + defenders[3][1]
        bounding_box = bounding_boxes[bbox_idx[3]][:]
        draw_text(bounding_box, text, draw)
    # print 5 defenders
    if countD == 2:
        print(defenders[0])
        print(defenders[1])
        print(defenders[2])
        print(defenders[3])
        print(defenders[4])
        i = 0
        positions = [] # needed to select postion on the plot
        while i < 5:
            text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
            (defenders[i][0], defenders[i][1], defenders[i][2], defenders[i][3], defenders[i][6], defenders[i][4], defenders[i][5]))
            positions.append(defenders[i][2])
            i = i + 1
        # allocate a bounding box index according to following order: LV, MD, RV
        # LIB will always be in the centre: LV-MD-LIB-MD-RV
        bbox_idx = [0, 0, 0, 0, 0]
        bbox_idx_used = 0
        i = 0
        while i < 5:
            if positions[i] == 'LV':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 5:
            if positions[i] == 'MD':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 5:
            if positions[i] == 'RV':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        # check if LIB was selected
        idx_lib = get_lib_idx(positions)
        if idx_lib > -1:
            # move current player on bbox position 2/3 to bbox position 3/4
            idx_curr2 = bbox_idx.index(2)
            idx_curr3 = bbox_idx.index(3)
            bbox_idx[idx_curr2] = 3
            bbox_idx[idx_curr3] = 4
            bbox_idx[idx_lib] = 2
        bounding_boxes = [[48, 460, 286, 510],[248, 510, 486, 560],[448, 460, 686, 510],[648, 510, 886, 560],[848, 460, 1086, 510]]
        text = defenders[0][0] + ' (' + str(defenders[0][3]) + ')\n' + defenders[0][1]
        bounding_box = bounding_boxes[bbox_idx[0]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[1][0] + ' (' + str(defenders[1][3]) + ')\n' + defenders[1][1]
        bounding_box = bounding_boxes[bbox_idx[1]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[2][0] + ' (' + str(defenders[2][3]) + ')\n' + defenders[2][1]
        bounding_box = bounding_boxes[bbox_idx[2]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[3][0] + ' (' + str(defenders[3][3]) + ')\n' + defenders[3][1]
        bounding_box = bounding_boxes[bbox_idx[3]][:]
        draw_text(bounding_box, text, draw)
        text = defenders[4][0] + ' (' + str(defenders[4][3]) + ')\n' + defenders[4][1]
        bounding_box = bounding_boxes[bbox_idx[4]][:]
        draw_text(bounding_box, text, draw)
        # todo: special case for LIB -> make sure that LIB is between MDs in case two MDs are selected


    # print midfielders to text file and in image
    print('Mittelfeld')
    text_file.write('Mittelfeld:\n')
    # print 3 midfielders
    if countM == 0:
        print(midfielders[0])
        print(midfielders[1])
        print(midfielders[2])
        i = 0
        positions = [] # needed to select postion on the plot
        while i < 3:
            text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
            (midfielders[i][0], midfielders[i][1], midfielders[i][2], midfielders[i][3], midfielders[i][6], midfielders[i][4], midfielders[i][5]))
            positions.append(midfielders[i][2])
            i = i + 1
        # allocate a bounding box index according to following order: LM, ZM, RM
        bbox_idx = [0, 0, 0]
        bbox_idx_used = 0
        i = 0
        while i < 3:
            if positions[i] == 'LM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 3:
            if positions[i] == 'ZM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 3:
            if positions[i] == 'RM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        bounding_boxes = [[148, 270, 386, 320],[448, 270, 686, 320],[748, 270, 986, 320]]
        text = midfielders[0][0] + ' (' + str(midfielders[0][3]) + ')\n' + midfielders[0][1]
        bounding_box = bounding_boxes[bbox_idx[0]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[1][0] + ' (' + str(midfielders[1][3]) + ')\n' + midfielders[1][1]
        bounding_box = bounding_boxes[bbox_idx[1]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[2][0] + ' (' + str(midfielders[2][3]) + ')\n' + midfielders[2][1]
        bounding_box = bounding_boxes[bbox_idx[2]][:]
        draw_text(bounding_box, text, draw)
    # print 4 midfielders
    if countM == 1:
        print(midfielders[0])
        print(midfielders[1])
        print(midfielders[2])
        print(midfielders[3])
        i = 0
        positions = [] # needed to select postion on the plot
        while i < 4:
            text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
            (midfielders[i][0], midfielders[i][1], midfielders[i][2], midfielders[i][3], midfielders[i][6], midfielders[i][4], midfielders[i][5]))
            positions.append(midfielders[i][2])
            i = i + 1
        # allocate a bounding box index according to following order: LM, ZM, RM
        bbox_idx = [0, 0, 0, 0]
        bbox_idx_used = 0
        i = 0
        while i < 4:
            if positions[i] == 'LM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 4:
            if positions[i] == 'ZM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 4:
            if positions[i] == 'RM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        bounding_boxes = [[48, 270, 286, 320],[306, 320, 544, 370],[590, 320, 828, 370],[848, 270, 1086, 320]]
        text = midfielders[0][0] + ' (' + str(midfielders[0][3]) + ')\n' + midfielders[0][1]
        bounding_box = bounding_boxes[bbox_idx[0]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[1][0] + ' (' + str(midfielders[1][3]) + ')\n' + midfielders[1][1]
        bounding_box = bounding_boxes[bbox_idx[1]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[2][0] + ' (' + str(midfielders[2][3]) + ')\n' + midfielders[2][1]
        bounding_box = bounding_boxes[bbox_idx[2]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[3][0] + ' (' + str(midfielders[3][3]) + ')\n' + midfielders[3][1]
        bounding_box = bounding_boxes[bbox_idx[3]][:]
        draw_text(bounding_box, text, draw)
    # print 5 midfielders
    if countM == 2:
        print(midfielders[0])
        print(midfielders[1])
        print(midfielders[2])
        print(midfielders[3])
        print(midfielders[4])
        i = 0
        positions = [] # needed to select postion on the plot
        while i < 5:
            text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
            (midfielders[i][0], midfielders[i][1], midfielders[i][2], midfielders[i][3], midfielders[i][6], midfielders[i][4], midfielders[i][5]))
            positions.append(midfielders[i][2])
            i = i + 1
        # allocate a bounding box index according to following order: LM, ZM, RM
        bbox_idx = [0, 0, 0, 0, 0]
        bbox_idx_used = 0
        i = 0
        while i < 5:
            if positions[i] == 'LM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 5:
            if positions[i] == 'ZM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        i = 0
        while i < 5:
            if positions[i] == 'RM':
                bbox_idx[i] = bbox_idx_used
                bbox_idx_used += 1
            i = i + 1
        bounding_boxes = [[48, 270, 286, 320],[248, 320, 486, 370],[448, 270, 686, 320],[648, 320, 886, 370],[848, 270, 1086, 320]]
        text = midfielders[0][0] + ' (' + str(midfielders[0][3]) + ')\n' + midfielders[0][1]
        bounding_box = bounding_boxes[bbox_idx[0]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[1][0] + ' (' + str(midfielders[1][3]) + ')\n' + midfielders[1][1]
        bounding_box = bounding_boxes[bbox_idx[1]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[2][0] + ' (' + str(midfielders[2][3]) + ')\n' + midfielders[2][1]
        bounding_box = bounding_boxes[bbox_idx[2]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[3][0] + ' (' + str(midfielders[3][3]) + ')\n' + midfielders[3][1]
        bounding_box = bounding_boxes[bbox_idx[3]][:]
        draw_text(bounding_box, text, draw)
        text = midfielders[4][0] + ' (' + str(midfielders[4][3]) + ')\n' + midfielders[4][1]
        bounding_box = bounding_boxes[bbox_idx[4]][:]
        draw_text(bounding_box, text, draw)


    # print strikers to text file and in image
    print('Sturm')
    text_file.write('Sturm:\n')
    # print 1 striker
    if countS == 0:
        print(strikers[0])
        text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
        (strikers[0][0], strikers[0][1], strikers[0][2], strikers[0][3], strikers[0][6], strikers[0][4], strikers[0][5]))
        text = strikers[0][0] + ' (' + str(strikers[0][3]) + ')\n' + strikers[0][1]
        bounding_box = [448, 90, 686, 140]
        draw_text(bounding_box, text, draw)
    # print 2 strikers
    if countS == 1:
        print(strikers[0])
        print(strikers[1])
        i = 0
        while i < 2:
            text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
            (strikers[i][0], strikers[i][1], strikers[i][2], strikers[i][3], strikers[i][6], strikers[i][4], strikers[i][5]))
            i = i + 1
        text = strikers[0][0] + ' (' + str(strikers[0][3]) + ')\n' + strikers[0][1]
        bounding_box = [248, 90, 486, 140]
        draw_text(bounding_box, text, draw)
        text = strikers[1][0] + ' (' + str(strikers[1][3]) + ')\n' + strikers[1][1]
        bounding_box = [648, 90, 886, 140]
        draw_text(bounding_box, text, draw)
    # print 3 strikers
    if countS == 2:
        print(strikers[0])
        print(strikers[1])
        print(strikers[2])
        i = 0
        while i < 3:
            text_file.write('%-30s %-30s %-4s    %3.1f  %2i   %4.1f   %2i\n' % \
            (strikers[i][0], strikers[i][1], strikers[i][2], strikers[i][3], strikers[i][6], strikers[i][4], strikers[i][5]))
            i = i + 1
        text = strikers[0][0] + ' (' + str(strikers[0][3]) + ')\n' + strikers[0][1]
        bounding_box = [148, 90, 386, 140]
        draw_text(bounding_box, text, draw)
        text = strikers[1][0] + ' (' + str(strikers[1][3]) + ')\n' + strikers[1][1]
        bounding_box = [448, 90, 686, 140]
        draw_text(bounding_box, text, draw)
        text = strikers[2][0] + ' (' + str(strikers[2][3]) + ')\n' + strikers[2][1]
        bounding_box = [748, 90, 986, 140]
        draw_text(bounding_box, text, draw)


    # close text file
    text_file.close()


    # print licence
    font_small = ImageFont.truetype("arial.ttf", 14)
    draw.text((924, 751),'Background Image: Freepic.com',(255,255,255),align='center',font=font_small)
    img.save(filename_jpg)

