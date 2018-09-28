import numpy as np
import sys

class Board:
    def __init__(self):
        self.board_array = []
        self.opp_board_array = []
        self.hit_count = {'C': 5, 'B': 4, 'R': 3, 'S': 3, 'D': 2}

    # read the board from file into an array
    def read_in_board(self, fileName):
        try:
            with open(fileName, 'r+') as myfile:
                board_raw = myfile.read()
            char_array_board = list(board_raw)
            rm_newline = list(filter(('\n').__ne__, char_array_board))
            self.board_array = np.reshape(rm_newline, (-1, 10))
        except FileNotFoundError:
            print("Error, cannot find board file")
            sys.exit(0)

    # returns the players own board.
    def get_board(self):
        return self.board_array

    # formats and returns the opponent board.
    def get_opp_board(self):
        # init a list of the correct size
        temp = []
        for i in range(100):
            temp.append('E')
        self.opp_board_array = np.reshape(temp, (-1, 10))

        # Fill out opponent board with required values
        for y in range(9):
            for x in range(9):
                if(self.board_array[x][y] == 'X'):
                    self.opp_board_array[x][y] = 'X'
                elif(self.board_array[x][y] == 'O'):
                    self.opp_board_array[x][y] = 'O'
                else:
                    self.opp_board_array[x][y] = '_'
        return self.opp_board_array


    # determine where the client fired on the board
    def check_hit(self, x, y):
        if(x < 0 or x > 9 or y < 0 or y > 9):
            return "OUT_OF_BOUNDS"
        if(self.board_array[x][y] == '_'):
            self.board_array[x][y] = 'O'
            return "MISS"
        if(self.board_array[x][y] == 'X' or self.board_array[x][y] == 'O'):
            return "ALREADY_HIT"
        else:
            ret = "HIT"
            if(self.board_array[x][y] == 'C'):
                self.hit_count['C'] -= 1
                if(self.hit_count['C'] <= 0):
                        ret = "SUNKC"
            elif(self.board_array[x][y] == 'B'):
                self.hit_count['B'] -= 1
                print(self.hit_count)
                if(self.hit_count['B'] <= 0):
                        ret = "SUNKB"
            elif(self.board_array[x][y] == 'R'):
                self.hit_count['R'] -= 1
                print(self.hit_count)
                if(self.hit_count['R'] <= 0):
                        ret = "SUNKR"
            elif(self.board_array[x][y] == 'S'):
                self.hit_count['S'] -= 1
                print(self.hit_count)
                if(self.hit_count['S'] <= 0):
                        ret = "SUNKS"
            elif(self.board_array[x][y] == 'D'):
                self.hit_count['D'] -= 1
                print(self.hit_count)
                if(self.hit_count['D'] <= 0):
                        ret = "SUNKD"
            self.board_array[x][y] = 'X'
            return ret