import numpy as np 
import copy 
import tkinter as tk
import tkinter.messagebox as messagebox

INF = 100000
def is_win_line(board, pos, length): #Kiểm tra xem vị trí pos có tạo nên đường thắng trong board không.
    x, y = pos 
    w, h = len(board[0]), len(board)
    symbol = board[y][x]
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)] 
    for dx, dy in directions:
        count = 1
        
        nx, ny = x + dx, y + dy
        while 0 <= nx < w and 0 <= ny < h and board[ny][nx] == symbol:
            count += 1
            nx, ny = nx + dx, ny + dy

        nx, ny = x - dx, y - dy
        while 0 <= nx < w and 0 <= ny < h and board[ny][nx] == symbol:
            count += 1
            nx, ny = nx - dx, ny - dy

        if count >= length:
            return True
    return False

class Caro:
    def __init__(self, w, h, line_len):
        self.w = w
        self.h = h
        self.line_len = line_len
        self.__board = np.full((h, w), None).tolist()
        self.sym = 'x'
        self.machine = 'o' if self.sym == 'x' else 'x'

    def to_move(self): #Trả về người chơi đến lượt đi.
        return self.sym

    def get_pos_actions(self): #Trả về tất cả các hành động có thể thực hiện (các ô trống) trên bảng.
        for y, row in enumerate(self.__board):
            for x, cell in enumerate(row):
                if cell is None:
                    yield x, y 

    def action(self, actions): # Thực hiện một hoặc nhiều hành động trên bảng trò chơi.
        if self.is_terminal():
            return

        for action in actions:
            x, y = action
            if (x, y) not in self.get_pos_actions():
                return

            self.__board[y][x] = self.sym
            self.sym = 'o' if self.sym == 'x' else 'x'

    def get_state(self): #Trả về trạng thái hiện tại của bảng trò chơi.
        return tuple(tuple(x) for x in self.__board)

    def is_terminal(self): #Kiểm tra xem trò chơi đã kết thúc chưa.
        for y in range(self.h):
            for x in range(self.w):
                if self.__board[y][x] is not None:
                    if is_win_line(self.__board, (x, y), self.line_len):
                        return True

        for y in range(self.h):
            for x in range(self.w):
                if self.__board[y][x] is None:
                    return False
        return True  

    def is_cut_off(self, depth): #Kiểm tra một node xem có phải điểm cut-off
        return True if self.is_terminal() or depth == 0 else False
            
    def count_three_lines(self, player): #Đếm số lượng đường thắng nhiều nhất mà người chơi player có thể có
        sim_game = copy.deepcopy(self.__board)  
        
        for y in range(self.h):
            for x in range(self.w):
                if sim_game[y][x] is None:
                    sim_game[y][x] = player 
        count = 0 

        for y in range(self.h): 
            line = sim_game[y][0:self.line_len] 
            if line.count(player) == self.line_len:
                count += 1
         
        for x in range(self.w): 
            line = [sim_game[i][x] for i in range(self.line_len)]
            if line.count(player) == self.line_len:  
                count += 1
         
        line = [sim_game[i][i] for i in range(self.line_len)]
        if line.count(player) == self.line_len:
            count += 1

        line = [sim_game[self.line_len - 1 - i][i] for i in range(self.line_len)]
        if line.count(player) == self.line_len:
            count += 1

        return count

    def eval(self, pos): # Trả về giá trị heuristic của một node trên cây trò chơi
        x, y = pos
        x_lines = self.count_three_lines('x')
        o_lines = self.count_three_lines('o')

        if is_win_line(self.__board, (x, y), self.line_len):  
            return INF if self.__board[y][x] == self.machine else -INF 
        else:
            return x_lines - o_lines  if self.machine == 'x' else o_lines-x_lines

    def show(self):
        for row in self.__board:
            for cell in row:
                if cell is None:
                    print('[ ]', end='')
                else:
                    print(f'[{cell}]', end='')
            print()

def heuristic_alpha_beta_tree_search(game): 
    sim_game = copy.deepcopy(game)
    depth = 2
    uti, best_a = max_value(sim_game, -INF, INF, depth, (0, 0))  
    return best_a

def max_value(sim_game, alpha, beta, depth, pos): 
    if sim_game.is_cut_off(depth):
        return sim_game.eval(pos), None
 
    max_utility = -INF 
    best_action = None
    temp_action = None

    for action in sim_game.get_pos_actions():
        sim_game_copy = copy.deepcopy(sim_game)
        sim_game_copy.action([action])
        utility, temp_action = min_value(sim_game_copy, alpha, beta, depth - 1, action)

        if utility > max_utility:
            max_utility = utility
            best_action = action

        if max_utility >= beta:
            return max_utility, best_action

        alpha = max(alpha, max_utility)

    if best_action == None: 
        best_action = temp_action    
        
    return max_utility, best_action

def min_value(sim_game, alpha, beta, depth, pos):
    if sim_game.is_cut_off(depth):
        return sim_game.eval(pos), None

    min_utility = INF
    best_action = None
    temp_action = None

    for action in sim_game.get_pos_actions():
        sim_game_copy = copy.deepcopy(sim_game)
        sim_game_copy.action([action])
        utility, temp_action = max_value(sim_game_copy, alpha, beta, depth - 1, action)

        if utility < min_utility:
            min_utility = utility
            best_action = action

        if min_utility <= alpha:
            return min_utility, best_action

        beta = min(beta, min_utility)

    if best_action == None:
        best_action = temp_action    
    return min_utility, best_action

class CaroUI:
    def __init__(self, root, game):
        self.root = root
        self.game = game
        self.win_msg = None

        root.title("Tic Tac Toe")

        self.btns = [[None]*self.game.w for _ in range(self.game.h)]
        for row in range(self.game.h):
            for col in range(self.game.w):
                self.btns[row][col] = tk.Button(root, text=" ", font=('Helvetica', 32), width=3, height=1,
                                                command=lambda r=row, c=col: self.on_click(r, c)) 
                self.btns[row][col].grid(row=row, column=col, sticky="nsew") 

    def on_click(self, row, col): # Xử lý sự kiện khi người dùng click vào một ô trên bảng. 
        if not self.win_msg:
            human_action = (col, row) 
            self.game.action([human_action])
            ai_action = heuristic_alpha_beta_tree_search(self.game)
            if ai_action is not None:
                self.game.action([ai_action])

        for row in range(self.game.h):
            for col in range(self.game.w):
                if self.game.get_state()[row][col] == 'x':
                    self.btns[row][col].config(text="X", state=tk.DISABLED, disabledforeground="green")
                elif self.game.get_state()[row][col] == 'o':
                    self.btns[row][col].config(text="O", state=tk.DISABLED, disabledforeground="red")

        if is_win_line(self.game.get_state(), human_action, self.game.line_len):
            self.win_msg = 'Human win!'
            self.show_message_box(self.win_msg)
        elif ai_action is not None and is_win_line(self.game.get_state(), ai_action, self.game.line_len):
            self.win_msg = 'AI win!'
            self.show_message_box(self.win_msg)
        elif self.game.is_terminal():
            self.win_msg = 'It\'s a draw!'
            self.show_message_box(self.win_msg)
    

    def show_message_box(self, msg): # Hiển thị hộp thoại thông báo kết quả của trò chơi.
        messagebox.showinfo("Game Over", msg)
        self.reset_game()

    def reset_game(self): # Reset trò chơi để bắt đầu ván mới.
        self.game = Caro(self.game.w, self.game.h, self.game.line_len) 
        self.win_msg = None
        for row in range(self.game.h):
            for col in range(self.game.w):
                self.btns[row][col].config(text=" ", state=tk.NORMAL)

def main():
    line_len = 3
    game = Caro(3, 3, line_len)  
    root = tk.Tk() 
    
    caro_ui = CaroUI(root, game) 

    root.mainloop() 

if __name__ == "__main__":
    main()

