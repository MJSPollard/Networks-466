import numpy as np
import sys

class Board:
    def __init__(self):
        self.board_array = []
        self.hit_count = {'C': 5, 'B': 4, 'R': 3, 'S': 3, 'D': 2}
        print(self.hit_count)

    def read_in_board(self, fileName):
        try:
            with open(fileName, 'r+') as myfile:
                board_raw = myfile.read()
            char_array_board = list(board_raw)
            rm_newline = list(filter(('\n').__ne__, char_array_board))
            self.board_array = np.reshape(rm_newline, (-1, 10))
            print(self.board_array)
        except FileNotFoundError:
            print("Error, cannot find board file")
            sys.exit(0)

        return(self.board_array)

    def print_board(self):
        # print(np.matrix(self.board_as_list))
        print("hello")

    def check_hit(self, x, y):
        if(x < 0 or x > 9 or y < 0 or y > 9):
            return "OUT_OF_BOUNDS"
        if(self.board_array[x][y] == '_'):
            return "MISS"
        if(self.board_array[x][y] == 'X'):
            return "ALREADY_HIT"
        else:
            if(self.board_array[x][y] == 'C'):
                self.hit_count['C'] -= 1
                print(self.hit_count)
                #mark with X
                #check if value = 0 if so, sunk
            elif(self.board_array[x][y] == 'B'):
                self.hit_count['B'] -= 1
                print(self.hit_count)
            elif(self.board_array[x][y] == 'R'):
                self.hit_count['R'] -= 1
                print(self.hit_count)
            elif(self.board_array[x][y] == 'S'):
                self.hit_count['S'] -= 1
                print(self.hit_count)
            elif(self.board_array[x][y] == 'D'):
                self.hit_count['D'] -= 1
                print(self.hit_count)
            # check here if sunk
            return "HIT"