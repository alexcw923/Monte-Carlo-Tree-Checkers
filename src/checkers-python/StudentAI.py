from random import randint
from BoardClasses import Move
from BoardClasses import Board
from math import sqrt, log
from copy import deepcopy
import time

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
# python3 AI_Runner.py 8 8 2 l /Users/alex/Desktop/Checkers_Student/src/checkers-python/main.py ./Sample_AIs/Random_AI/main.py
# python3 AI_Runner.py 8 8 2 l ./Sample_AIs/Random_AI/main.py /Users/alex/Desktop/Checkers_Student/src/checkers-python/main.py 
# python3 AI_Runner.py 8 8 2 l /home/alexcw2/Checkers_Student/src/checkers-python/main.py ./Sample_AIs/Random_AI/main.py
# python3 main.py 8 8 2 m 0

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        
        self.root = None
        
        
    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        
        
        if not self.root or len(self.root.children) == 0 or len(self.root.untried) > 0:           #init the tree
            
            obj = MCTSNode(self.board, self.color)
            self.root = obj.build()
        else:                                                       #move to opponent node
            for child, m in self.root.children.items():
                if m.seq == move.seq:
                    # print("in")
                    child.parent = None
                    self.root = child          
        best_move = self.root.best_move()
        

        self.board.make_move(best_move,self.color)
        next_child = self.root.best_child(0)
        next_child.parent = None
        self.root = next_child
        return best_move




    
class MCTSNode():  
    opponent = {1:2,2:1} 
    def __init__(self, state : Board, color : int, parent = None):        
        if not hasattr(MCTSNode, 'player_color'):
            MCTSNode.player_color = color     #class/static variable

        self.win_count = 0
        self.num_simulation = 0 
        
        self.state = state
        self.parent = parent
        self.color = color
        self.children = dict()
      
        
        self.untried = self.state.get_all_possible_moves(color)

    def build(self):
        # time_limit = 20
        # start = time.time()         #the variable that holds the starting time
        # elapsed, num_sim = 0, 0                 #the variable that holds the number of seconds elapsed.
        
        
        # while elapsed < time_limit:
        #     Node = self.select()
        #     res = Node.simulate()
        #     Node.backprop(res, Node.color)
            
        #     elapsed = time.time() - start
        #     num_sim += 1
        iteration = 5000
        for _ in range(iteration):
            Node = self.select()
            res = Node.simulate()
            Node.backprop(res, Node.color)
            
        return self
        
    def best_move(self) -> Move:
        return self.children[self.best_child(0)]

    def best_child(self, c):
        children_uct = {calc_uct(child, c) : child for child in self.children}
        
        return children_uct[max(children_uct.keys())]
    
    def select(self):
        curr = self
        while is_win(curr.color, curr.state) == 0:
            if len(curr.untried) != 0:
                return curr.expand()
            else:
                curr = curr.best_child(sqrt(2))
        return curr

    def expand(self):
        next_move = self.untried[len(self.untried) - 1].pop()
        if len(self.untried[len(self.untried) - 1]) == 0:
            self.untried.remove(self.untried[len(self.untried) - 1])
            
        copy_state = deepcopy(self.state)
        copy_state.make_move(next_move, self.color)
        child = MCTSNode(state = copy_state, color = MCTSNode.opponent[self.color], parent = self)
        self.children[child] = next_move
        
        return child
    
    def simulate(self) -> int:
        curr = deepcopy(self.state)
        colorCurr = self.color
        count, count_limit = 0, 25
        while is_win(colorCurr, curr) == 0:
            #random rollout
            if count == count_limit:
                return -1
            moves = curr.get_all_possible_moves(colorCurr)
            index = randint(0,len(moves)-1)
            inner_index = randint(0,len(moves[index])-1)
            move = moves[index][inner_index]
            
            #flip
            curr.make_move(move, colorCurr)
            colorCurr = MCTSNode.opponent[colorCurr]
            count += 1
            
        return is_win(colorCurr, curr)

    def backprop(self, result : str, node_color : int):
        self.num_simulation += 1
        
        if result == -1 and self.color != MCTSNode.player_color and self.color != node_color:
            self.win_count += 0.5
        elif result != self.color:         #need change
            self.win_count += 1

        if self.parent:
            self.parent.backprop(result, node_color)     

            
def calc_uct(Node, c = sqrt(2)) -> float:
    si = Node.num_simulation
    sp = Node.parent.num_simulation
    wi = Node.win_count

    return wi / si + c * sqrt(log(sp) / si)

def is_win(turn : int, state : Board):
    if turn == "W":
        turn = 2
    elif turn == "B":
        turn = 1
    if state.tie_counter >= state.tie_max:
        return -1
    W_has_move = True
    B_has_move = True
    
    if len(state.get_all_possible_moves(1)) == 0:
        if turn == 1:
            B_has_move = False
    elif len(state.get_all_possible_moves(2)) == 0:
        if turn == 2:
            W_has_move = False

    if W_has_move and not B_has_move:
        return 2
    elif not W_has_move and B_has_move:
        return 1

    W = True
    B = True

    for row in range(state.row):
        for col in range(state.col):
            checker = state.board[row][col]
            if checker.color == 'W':
                W = False
            elif checker.color == 'B':
                B = False
            if not W and not B:
                return 0
    if W:
        return 2
    elif B:
        return 1
    else:
        return 0
    