import random
import math
import time
from BaseAI import BaseAI

weight = [[200000,18,16,15],[12,10,10,15],[8,7,6,10],[2,1,1,3]]
defaultProbability  = 0.9

class IntelligentAgent(BaseAI):
    def getMove(self, grid):
        # S = time.time()
        global time_over
        time_over = False
        moveset = grid.getAvailableMoves()
        max_utility = -math.inf
        start_time = time.time()
        
        for one_move in moveset:
            clone_move = grid.clone()
            clone_move.move(one_move[0])
            alpha = -math.inf
            beta = math.inf
            (child, utility) = Minimize(clone_move, alpha, beta, 0, start_time)
            if utility > max_utility:
                move_choice = one_move[0]
                max_utility = utility
        
        # E = time.time()
        # print(E-S)
        
        clone_move = grid.clone()
        clone_move.move(move_choice)
        move_priority = [0,2,3,1]
        if clone_move.getCellValue((0,0)) == 0 or move_choice == 1 or time_over:
            for i in move_priority:
                for one_move in moveset:
                    if i == one_move[0]:
                        return one_move[0]
                        
        return move_choice
    
def Maximize(state, alpha, beta, depth, start_time):
    global time_over
    if time_over or (time.time() - start_time) > 0.2:
        time_over = True
        return (None, Utility(state))
    
    moveset = state.getAvailableMoves()
    
    if len(moveset) == 0 or depth == 2:
        return (None, Utility(state))
    
    max_child = None
    max_utility = -math.inf
    
    for child in moveset:
        (state, utility) = Minimize(child[1], alpha, beta, depth+1, start_time)
        if time_over or (time.time() - start_time) > 0.2:
            time_over = True
            return (None, utility)
        if utility > max_utility:
            max_child = child[1]
            max_utility = utility
        if max_utility >= beta:
            break
        if max_utility > alpha:
            alpha = max_utility     
    return (max_child, max_utility)
        
def Minimize(state, alpha, beta, depth, start_time):
    global time_over
    if time_over or (time.time() - start_time) > 0.2:
        time_over = True
        return (None, Utility(state))

    available_cell = state.getAvailableCells()
    if len(available_cell) == 0 or depth == 2:
        return (None, Utility(state))
    min_child = None
    min_utility = math.inf
    possible_cell = []
    for cell in available_cell:
        clone_grid2 = state.clone()
        clone_grid4 = state.clone()
        clone_grid2.insertTile(cell, 2)
        clone_grid4.insertTile(cell, 4)
        possible_cell.append((clone_grid2, clone_grid4))
    for child in possible_cell:
        (state2, utility2) = Maximize(child[0], alpha, beta, depth+1, start_time)
        (state4, utility4) = Maximize(child[1], alpha, beta, depth+1, start_time)
        if time_over or (time.time() - start_time) > 0.2:
            time_over = True
            return (None, defaultProbability*utility2 + (1-defaultProbability)*utility4)
        # Expectiminimax
        utility = defaultProbability*utility2 + (1-defaultProbability)*utility4
        if utility < min_utility:
            min_child = child[0]
            min_utility = utility
        if min_utility <= alpha:
            break
        if min_utility < beta:
            beta = min_utility
    return (min_child, min_utility)



def Grid_state(grid):
    state = []
    num = [0]*18
    for i in range(4):
        state_row = []
        for j in range(4):
            number_ij = grid.getCellValue((i, j))
            if number_ij:
                state_row += [int(math.log2(number_ij))]
            else:
                state_row += [0]
            if number_ij == 0:
                num[0] += 1
            else:
                num[int(math.log2(number_ij))]+=1
        state += [state_row]
    return state, num

def Grid_score(num):
    score = 0
    for i in range(2,18):
        if num[i]:
            score += 2**i*(i-1)*num[i]
    return score

def Grid_position_score(state, weight):
    score = 0
    for i in range(4):
        for j in range(4):
            if state[i][j]:
                score += weight[i][j]*2**state[i][j]
    return score

def special_debuff(grid, state_1D):
    debuff = 0
    num_zero_2 = 0
    num_zero_3 = 0
    num_zero_4 = 0
    for i in range(4,8):
        if state_1D[i] == 0:
            num_zero_2 += 1
    for i in range(8,12):
        if state_1D[i] == 0:
            num_zero_3 += 1
    for i in range(12,16):
        if state_1D[i] == 0:
            num_zero_4 += 1
    if num_zero_2 == 0 and num_zero_3 == 4 and len(grid.getAvailableMoves()) == 1:
        debuff = -2000000
    if num_zero_3 == 0 and num_zero_4 == 4 and len(grid.getAvailableMoves()) == 1:
        debuff = -2000000
    if (num_zero_4 == 4 or (num_zero_3 == 4 and num_zero_4 == 4)) and state_1D[3] == 0 and state_1D[7] == 0 and state_1D[11] == 0 and len(grid.getAvailableMoves()) == 2:
        debuff = -1000000
    return debuff

def Utility(grid):
    global weight
    state, num = Grid_state(grid)
    
    state_1D = []
    weight_1D = []
    for i in range(4):
        for j in range(4):
            state_1D += [state[i][j]]
            weight_1D += [weight[i][j]]
            

    score = Grid_score(num)
    position_score = Grid_position_score(state,weight)
    debuff_score = special_debuff(grid, state_1D)
    return score + position_score + debuff_score


