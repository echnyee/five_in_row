import sys
import time
import socket
import struct
import fileinput

LEN = 20
WID = 20
MY_CHESS = 1
OP_CHESS = 2
ROW = '-'
NUM = 3
pic = [[]] * LEN
ID = 6
DEBUG = False
WIN_FIVE = 500
LIVE_LACK_FIVE = 28
LIVE_FOUR = 100
LIVE_THREE = 22
LIVE_LACK_FOUR = 20
LIVE_TWO = 5
LIVE_LACK_THREE = 4
DEAD_FOUR = 40
DEAD_THREE = 5
DEAD_TWO = 1
VERDICT = None

for i in range(0, LEN):
    pic[i] = [0] * WID

step = 1
first_step = (10, 10)

def main():
    global pic
    x, y = decide_step(pic)
    robot_step(x, y)
    show_whole_pic(pic)
    if VERDICT:
        print '='*50 + 'You ' + VERDICT
        sys.exit()
    get_and_store_input()
    if VERDICT:
        print '='*50 + 'You ' + VERDICT
        sys.exit()

def decide_step(pic):
    global step
    if step == 1:
        step += 1
        return first_step
    else:
        next_x, next_y = find_candidate()
        step += 1
        return next_x, next_y

def find_candidate():
    global VERDICT
    y = 20
    offence_list = []
    defence_list = []
    candidate_list = []
    for line in pic:
        x = 1
        for point in line:
            if point == 0:
                offence_score, step_to_win = search_four_directions(x, y, MY_CHESS)
                if offence_score > 0:
                    offence_list.append([x,y,offence_score,step_to_win])
                defence_score, step_to_win = search_four_directions(x, y, OP_CHESS)
                if defence_score > 0:
                    defence_list.append([x,y,defence_score,step_to_win])
                total_score = offence_score + defence_score
                if total_score > 0:
                    candidate_list.append([x,y,total_score])
            x += 1
        y -= 1

    sorted_o = sorted(offence_list, key=lambda c: c[2], reverse=True)
    sorted_d = sorted(defence_list, key=lambda c: c[2], reverse=True)
    sorted_c = sorted(candidate_list, key=lambda c: c[2], reverse=True)

    offence_highest_score = 0
    defence_highest_score = 0

    if sorted_o:
        offence_highest_score = sorted_o[0][2]
    if sorted_d:
        defence_highest_score = sorted_d[0][2]
    if offence_highest_score >= 500:
        VERDICT = 'LOSE'
    return sorted_c[0][0], sorted_c[0][1]

def search_four_directions(x, y, chess_value):
    score = 0
    shortest_step = 5
    horizon = ((1,0),(-1,0))
    vertical = ((0,1),(0,-1))
    right_45 = ((1,1),(-1,-1))
    left_45 = ((-1,1),(1,-1))
    if (x,y) == (10,11):
        DEBUG = True
    else:
        DEBUG = False
    combo_h = check_combo([[x,y]], horizon, (False, False), chess_value)
    #if DEBUG:
    #    print 'combo is ===========', (combo_h, chess_value)
    DEBUG = False
    combo_v = check_combo([[x,y]], vertical, (False, False), chess_value)
    combo_r = check_combo([[x,y]], right_45, (False, False), chess_value)
    combo_l = check_combo([[x,y]], left_45, (False, False), chess_value)
    if len(combo_h) > 3:
        pic[LEN-y][x-1] = chess_value
        # pretend to make a point here, for check score usage
        tmp_s, step = cal_combo_score(combo_h, chess_value)
        score += tmp_s
        if step < shortest_step:
            shortest_step = step
        pic[LEN-y][x-1] = 0
    if len(combo_v) > 3:
        pic[LEN-y][x-1] = chess_value
        # pretend to make a point here, for check score usage
        tmp_s, step = cal_combo_score(combo_v, chess_value)
        score += tmp_s
        if step < shortest_step:
            shortest_step = step
        pic[LEN-y][x-1] = 0
    if len(combo_r) > 3:
        pic[LEN-y][x-1] = chess_value
        # pretend to make a point here, for check score usage
        tmp_s, step = cal_combo_score(combo_r, chess_value)
        score += tmp_s
        if step < shortest_step:
            shortest_step = step
        pic[LEN-y][x-1] = 0
    if len(combo_l) > 3:
        pic[LEN-y][x-1] = chess_value
        # pretend to make a point here, for check score usage
        tmp_s, step = cal_combo_score(combo_l, chess_value)
        score += tmp_s
        if step < shortest_step:
            shortest_step = step
        pic[LEN-y][x-1] = 0
    return score, shortest_step

def check_combo(combo, (postive_move, negative_move), (postive_space_flag, negative_space_flag), chess_value):
    if chess_value == MY_CHESS:
        op_chess_value = OP_CHESS
    else:
        op_chess_value = MY_CHESS
    # postive_move: right, top, right-top, right-bottom
    # negative_move: left, bottom, left-top, left-bottom
    if postive_move == (0, 0) and negative_move == (0, 0):
        return combo
    if negative_move != (0, 0):
        x_after_negmove = combo[0][0]+negative_move[0]
        y_after_negmove = combo[0][1]+negative_move[1]
        if block_after_move(x_after_negmove, y_after_negmove, op_chess_value):
            # stored whole pic structure is different with x,y axis
            negative_move = (0, 0)
            # block
            if not negative_space_flag:
                # don't want to add space and blocker both to the combo
                combo.insert(0, [-1, -1])
        elif pic[LEN-y_after_negmove][x_after_negmove-1] == 0:
            if negative_space_flag:
                # two space here, I don't look further here
                negative_move = (0, 0)
            else:
                combo.insert(0, [x_after_negmove, y_after_negmove])
                negative_space_flag = True
        else:
            negative_space_flag = False
            combo.insert(0, [x_after_negmove, y_after_negmove])
    if postive_move != (0, 0):
        x_after_posmove = combo[-1][0]+postive_move[0]
        y_after_posmove = combo[-1][1]+postive_move[1]
        if block_after_move(x_after_posmove, y_after_posmove, op_chess_value):
            postive_move = (0, 0)
            if not postive_space_flag:
                # don't want to add space and blocker both to the combo
                combo.append([-1,-1])
        elif pic[LEN-y_after_posmove][x_after_posmove-1] == 0:
            if postive_space_flag:
                postive_move = (0, 0)
            else:
                combo.append([x_after_posmove, y_after_posmove])
                postive_space_flag = True
        else:
            postive_space_flag = False
            combo.append([x_after_posmove, y_after_posmove])
    return check_combo(combo, (postive_move, negative_move), (postive_space_flag, negative_space_flag), chess_value)

def cal_combo_score(combo, self_chess_value):
    (neg_s, pos_s) = check_sides(combo, self_chess_value)
    return  cal_by_len_side(combo, neg_s, pos_s)

def check_sides(combo, self_chess_value):
    if self_chess_value == MY_CHESS:
        op_chess_value = OP_CHESS
    elif self_chess_value == OP_CHESS:
        op_chess_value = MY_CHESS
    neg_side = 'alive'
    pos_side = 'alive'
    if combo[0] == [-1, -1]:
        if pic[LEN-combo[1][1]][combo[1][0]-1] == self_chess_value:
            neg_side = 'dead'
    elif pic[LEN-combo[0][1]][combo[0][0]-1] == op_chess_value:
        neg_side = 'dead'
    if combo[-1] == [-1, -1]:
        if pic[LEN-combo[-2][1]][combo[-2][0]-1] == self_chess_value:
            pos_side = 'dead'
    elif pic[LEN-combo[-2][1]][combo[-2][0]-1] == op_chess_value:
        pos_side = 'dead'

    return (neg_side, pos_side)

def cal_by_len_side(combo, neg_s, pos_s):
    # return score and steps to win
    num = get_combo_number(combo)
    if neg_s == 'alive' and pos_s == 'alive':
        #both side is free
        if num == 5:
            if len(combo) == 7:
                # just one step is needed to win
                return (WIN_FIVE, 1)
            else:
                return (LIVE_LACK_FIVE, 2)
        elif num == 4:
            if len(combo) == 6:
                return (LIVE_FOUR, 2)
            else:
                return (LIVE_LACK_FIVE, 2)
        elif num == 3:
            if len(combo) == 5:
                return (LIVE_THREE, 3)
            else:
                return (LIVE_LACK_FOUR, 3)
        elif num == 2:
            if len(combo) == 4:
                return (LIVE_TWO, 4)
            else:
                return (LIVE_LACK_THREE, 4)
        else:
            return (0, 5)
    elif neg_s == 'alive' or pos_s == 'alive':
        # only one side is free
        if num == 5:
            if len(combo) == 7:
                return (WIN_FIVE, 1)
            else:
                print 'lack five==='
                print combo
                return (LIVE_LACK_FIVE, 2)
        elif num == 4:
            if len(combo) == 6:
                return (DEAD_FOUR, 2)
            else:
                return (LIVE_LACK_FIVE, 2)
        elif num == 3:
            return (DEAD_THREE, 3)
        elif num == 2:
            return (DEAD_TWO, 4)
        else:
            return (0, 5)
    elif neg_s == 'dead' and pos_s == 'dead':
        if num == 5:
            if len(combo) == 7:
                return (WIN_FIVE, 1)
            else:
                return (LIVE_LACK_FIVE, 2)
        elif num == 4 and len(combo) == 7:
            # usually we won't count combo for both side blocked, but if the remaining part can be 5, then it's worth considering
            return (15, 2)
        else:
            return (0, 5)

def get_combo_number(combo):
    num = 0
    valid_c = combo[1:-1]
    for c in valid_c:
        if pic[LEN-c[1]][c[0]-1] != 0:
            num += 1
    return num

def block_after_move(x, y, op_chess_value):
    if x > WID or x < 1 or y > LEN or y < 1:
        return True
    elif pic[LEN-y][x-1] == op_chess_value:
        return True
    else:
        return False

def two_space(xy1, xy2):
    if pic[LEN-xy1[1]][xy1[0]-1] == 0 and pic[LEN-xy2[1]][xy2[0]-1] == 0:
        # 2 empty point, I won't look after this
        return True
    else:
        return False

def robot_step(x, y):
    if (x,y) != (0,0):
        print '============robot step:', (x, y)
        store_whole_pic(x, y, MY_CHESS)
    return

def get_and_store_input():
    global VERDICT
    coordinate = raw_input("please input your coordinate in this format 'x y' : ")
    tmp = coordinate.split()
    x = int(tmp[0])
    y = int(tmp[1])
    score, _step_to_win = search_four_directions(x, y, OP_CHESS)
    if score >= 500:
        VERDICT = 'WIN'
    store_whole_pic(x, y, OP_CHESS)

def store_whole_pic(x, y, value):
    global pic
    pic[LEN-y][x-1] = value

def show_whole_pic(pic):
    print '    =====================I\'m light blue====================\n'
    y_axis = LEN
    x_axis = 1
    last_line = '      '
    for line in pic:
        if y_axis < 10:
            first_line = str(y_axis) + '     '
        else:
            first_line = str(y_axis) + '    '
        if x_axis < 10:
            last_line += str(x_axis) + ' '*NUM
        else:
            last_line += str(x_axis) + ' '*(NUM-1)
        y_axis -= 1
        x_axis += 1
        second_line = '      '
        for chess in line:
            first_line += match_chess_to_string(chess)
            second_line += '|' + ' '*NUM
        print first_line[0:-3]
        if y_axis != 0:
            print second_line
    print ' '
    print last_line

def match_chess_to_string(chess):
    if chess == 1:
        return '\033[92m' + 'O' + '\033[0m' + ROW*NUM
    elif chess == 2:
        return '\033[93m' + 'X' + '\033[0m' + ROW*NUM
    else:
        return ' ' + ROW*NUM


while True:
    main()
