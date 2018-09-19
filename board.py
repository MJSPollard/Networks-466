
class Board:
    #need to read in file and manipulate
    def read_in_board(self, fileName):
        print(fileName)
        return(fileName)

    def print_board(self, fileName):
        print(fileName)
        return(fileName)

    def check_hit(self, x, y):
        print("bounds")
        # change to board.length - check out of bounds
        if(x < 0 or x > 9 or y < 0 or y > 9):
            return "OUT_OF_BOUNDS"
      # if(array[x][y] == ' '):
      # return "MISS"
        else:
            return "HIT"