#!/usr/local/bin/python3
# solve_luddy.py : Sliding tile puzzle solver
#
# Code by: Nikita Bafna, Neha Pai, Shivali Jejurkar (nibafna-nrpai-sjejurka)
#
# Based on skeleton code by D. Crandall, September 2019
#
import queue as Q
import sys
import heapq

# Moves for original and Circular variant
MOVES = {"R": (0, -1), "L": (0, 1), "D": (-1, 0), "U": (1, 0)}

# Moves defined for Luddy variant
MOVES_LUDDY = {"A": (2, 1), "B": (2, -1), "C": (-2, 1), "D": (-2, -1), "E": (1, 2), "F": (1, -2), "G": (-1, 2),
               "H": (-1, -2)}


def rowcol2ind(row, col):
    return row * 4 + col


def ind2rowcol(ind):
    return (int(ind / 4), ind % 4)


def valid_index(row, col):
    return 0 <= (row) <= 3 and 0 <= (col) <= 3


def swap_ind(list, ind1, ind2):
    return list[0:ind1] + (list[ind2],) + list[ind1 + 1:ind2] + (list[ind1],) + list[ind2 + 1:]


def swap_tiles(state, row1, col1, row2, col2):
    return swap_ind(state, *(sorted((rowcol2ind(row1, col1), rowcol2ind(row2, col2)))))


def printable_board(row):
    return ['%3d %3d %3d %3d' % (row[j:(j + 4)]) for j in range(0, 16, 4)]


# return a list of possible successor states
def successorsOriginal(state):
    (empty_row, empty_col) = ind2rowcol(state.index(0))
    return [(swap_tiles(state, empty_row, empty_col, empty_row + i, empty_col + j), c) \
            for (c, (i, j)) in MOVES.items() if valid_index(empty_row + i, empty_col + j)]


def successorsLuddy(state):
    (empty_row, empty_col) = ind2rowcol(state.index(0))
    return [(swap_tiles(state, empty_row, empty_col, empty_row + i, empty_col + j), c) \
            for (c, (i, j)) in MOVES_LUDDY.items() if valid_index(empty_row + i, empty_col + j)]


def successorsCircular(state):
    (empty_row, empty_col) = ind2rowcol(state.index(0))
    list_of_successors = []
    for (c, (i, j)) in MOVES.items():
        if empty_row + i == -1:
            i = i + 4
        elif empty_row + i == 4:
            i = i - 4
        if empty_col + j == -1:
            j = j + 4
        elif empty_col + j == 4:
            j = j - 4
        if valid_index(empty_row + i, empty_col + j):
            list_of_successors.append((c, (i, j)))
    return [(swap_tiles(state, empty_row, empty_col, empty_row + i, empty_col + j), c) \
            for (c, (i, j)) in list_of_successors]


# check if we've reached the goal
def is_goal(state):
    return sorted(state[:-1]) == list(state[:-1]) and state[-1] == 0


def calculateManhattan(initial_state):
    goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]
    return (sum(abs(b % 4 - g % 4) + abs(b // 4 - g // 4)
                for b, g in ((initial_state.index(i), goal_state.index(i)) for i in range(1, 16))))


def calculateMisplaced(initial_state):
    goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]
    heuristic = 0
    for i in range(1, 16):
        if initial_state.index(i) != goal_state.index(i):
            heuristic += 1
    return heuristic


def horizontalConflict(state):
    linearConflict = 0
    for row in range(4):
        maxS = -1
        for column in range(4):
            posValue = getPosValue(state, row, column)
            if (posValue != 0 and (posValue - 1) // 4 == row):
                if posValue > maxS:
                    maxS = posValue
                else:
                    linearConflict += 2
    return linearConflict


def verticalConflict(state):
    linearConflict = 0
    for column in range(4):
        maxS = -1
        for row in range(4):
            posValue = getPosValue(state, row, column)
            if posValue != 0 and posValue % 4 == column + 1:
                if posValue > maxS:
                    maxS = posValue
                else:
                    linearConflict += 2
    return linearConflict


def getPosValue(s, row, col):
    arr = []
    temp = []
    for i in range(16):
        if i == 0:
            temp = [s[i]]
        elif i % 4 != 0:
            temp.append(s[i])
        else:
            arr.append(temp)
            temp = [s[i]]
    arr.append(temp)
    return arr[row][col]


def linearConflict(state):
    return horizontalConflict(state) + verticalConflict(state)


def findLocation(initial_state):
    for i in range(0, 16):
        if initial_state[i] == 0:
            return int(i / 4)


def getCountOfInv(initial_state):
    inv_count = 0
    for i in range(0, 15):
        for j in range(i + 1, 16):
            if initial_state[i] > initial_state[j] and initial_state[i] != 0 and initial_state[j] != 0:
                inv_count += 1
    return inv_count


# The solver! - using AStar

def solveA(initial_board, variant):
    came_from = {}
    cost_so_far = {}
    came_from[initial_board] = None
    cost_so_far[initial_board] = 0
    fringe = []
    heapq.heappush(fringe, (0, initial_board, "", 0))
    gscore = 0
    fscore = 0
    close_set = set()
    while fringe:

        a = heapq.heappop(fringe)
        current = a[1]
        route_so_far = a[2]
        gscore = a[3] + 1

        if is_goal(current):
            return (route_so_far)

        if variant == "original":
            functionCall = successorsOriginal
        elif variant == "circular":
            functionCall = successorsCircular
        else:
            functionCall = successorsLuddy

        for (succ, move) in functionCall(current):

            if succ not in close_set:
                if variant == "luddy":
                    heapq.heappush(fringe, (gscore + calculateMisplaced(succ), (succ), route_so_far + move, gscore))
                    # print(priority)
                else:
                    heapq.heappush(fringe, (gscore + calculateManhattan(succ), (succ), route_so_far + move, gscore))

        close_set.add(current)

    return False


# test cases
if __name__ == "__main__":
    if (len(sys.argv) != 3):
        raise (Exception("Error: expected 2 arguments"))

    start_state = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            start_state += [int(i) for i in line.split()]

    variant = sys.argv[2].lower()

    if len(start_state) != 16:
        raise (Exception("Error: couldn't parse start state file"))

    print("Start state: \n" + "\n".join(printable_board(tuple(start_state))))

    solution = ""
    if variant == "original":
        if findLocation(start_state) % 2 == 0:
            if getCountOfInv(start_state) % 2 != 0:
                print("Solving...")
                route = solveA(tuple(start_state), variant)
            else:
                solution = "Inf"
                print("Inf")
        else:
            if getCountOfInv(start_state) % 2 == 0:
                print("Solving...")
                route = solveA(tuple(start_state), variant)
            else:
                solution = "Inf"
                print("Inf")
        if solution != "Inf":
            print("Solution found in " + str(len(route)) + " moves:" + "\n" + route)
    else:
        print("Solving...")
        route = solveA(tuple(start_state), variant)
        print("Solution found in " + str(len(route)) + " moves:" + "\n" + route)