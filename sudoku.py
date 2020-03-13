import pygame
import time
import random
import copy
import tkinter as tk
from tkinter import messagebox
import os
import sys

pygame.init()
mainfont = pygame.font.SysFont('Courier',40, bold=True)
mainfont2 = pygame.font.SysFont('Courier New',40)
timefont = pygame.font.SysFont('Courier', 20)
pencilfont = pygame.font.SysFont('Courier', 14)

class Grid:    
    def __init__(self, rows, cols, width, height, win, board, answers):
        self.rows = rows
        self.cols = cols
        self.squares = [[Square(i, j, width, height, board[i][j], answers[i][j]) for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.win = win
        self.mistakes = 0
        self.selected = None
        
    def draw(self):
        gap = self.width / self.rows
        for i in range(self.rows+1):
            if i % 3 == 0:
                pygame.draw.line(self.win, (0,0,0), (0, i*gap), (self.width, i*gap),3)
                pygame.draw.line(self.win, (0,0,0), (i * gap, 0), (i * gap, self.height),3)
            else:
                pygame.draw.line(self.win, (0,0,0), (0, i*gap), (self.width, i*gap))
                pygame.draw.line(self.win, (0,0,0), (i * gap, 0), (i * gap, self.height))
        for i in range(self.rows):
            for j in range(self.cols):
                self.squares[i][j].draw(self.win)
        if self.selected:
            if self.squares[self.selected[1]][self.selected[0]].locked == False:
                pygame.draw.rect(self.win, (255, 0, 0), (self.selected[0]*gap, self.selected[1]*gap, gap, gap), 3)
    
    def click(self,pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / self.rows
            x = pos[0] // gap
            y = pos[1] // gap
            self.selected = (int(x),int(y))
                
    def pencil(self,value):
        if self.selected:
            if self.squares[self.selected[1]][self.selected[0]].locked == False:
                self.squares[self.selected[1]][self.selected[0]].pencil = value
        
    def clear(self):
        if self.selected:
            if self.squares[self.selected[1]][self.selected[0]].locked == False:
                self.squares[self.selected[1]][self.selected[0]].pencil = 0
                self.squares[self.selected[1]][self.selected[0]].value = 0
        
    def submit(self):
        if self.selected:
            if self.squares[self.selected[1]][self.selected[0]].locked == False:
                if self.squares[self.selected[1]][self.selected[0]].pencil != 0:
                    self.squares[self.selected[1]][self.selected[0]].value = \
                    self.squares[self.selected[1]][self.selected[0]].pencil
                    if self.squares[self.selected[1]][self.selected[0]].answer == \
                    self.squares[self.selected[1]][self.selected[0]].value:
                        self.squares[self.selected[1]][self.selected[0]].locked = True
                    else:
                        self.mistakes += 1
                    self.squares[self.selected[1]][self.selected[0]].pencil = 0
                    
    def solve(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if not self.squares[i][j].locked:
                    self.squares[i][j].value = self.squares[i][j].answer
                    self.squares[i][j].locked = True
                    self.squares[i][j].lockedred = True
                    self.mistakes += 1
                    
    def verify(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if not self.squares[i][j].value == self.squares[i][j].answer:
                    return False
        return True
                
class Square:
    def __init__(self, row, col, width, height, value, answer):
        self.value = value
        self.answer = answer
        self.lockedred = False
        if self.value != self.answer:
            self.locked = False
        else:
            self.locked = True
        self.pencil = ""
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        
    def draw(self,win):
        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap
        if self.value != 0:
            if self.lockedred == True:
                text = mainfont.render(str(self.value),1,(255,0,0))
            elif self.value != self.answer:
                text = mainfont2.render(str(self.value),1,(255,0,0))
            else:
                text = mainfont.render(str(self.value),1,(0,0,0))
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))
        if self.pencil != 0:
            text = pencilfont.render(str(self.pencil),1,(128,128,128))
            win.blit(text, (x + 5, y + 5))
            
class Generator:
    def newBoard(self):
        self.board = [[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0]]
        self.dfs()
        self.removed = 0
        
    def makeBoard(self,difficulty):
        if difficulty == "easy":
            while self.removed < 25:
                self.remove()
        if difficulty == "medium":
            while self.removed < 40:
                self.remove()
        if difficulty == "hard":
            while self.removed < 50:
                self.remove()

    def remove(self):
        x = random.randint(0,8)
        y = random.randint(0,8)
        while self.board[x][y] == 0:
            x = random.randint(0,8)
            y = random.randint(0,8)
        prevBoard1 = copy.deepcopy(self.board)
        self.board[x][y] = 0
        self.removed += 1
        prevBoard2 = copy.deepcopy(self.board)
        if self.dfs():
            self.board = prevBoard2
        else:
            self.board = prevBoard1
            self.removed -= 1


    def findUnassigned(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return row, col
        return -1, -1
    
    def isValid(self,row,col,num):
        if num in self.board[row]:
            return False
        if num in list(zip(*self.board))[col]:
            return False
        if num in [self.board[x][y] for x in range(row-row%3,row-row%3+3) for y in range(col-col%3,col-col%3+3)]:
            return False
        return True
    
    def dfs(self):
        row,col = self.findUnassigned()
        if row == -1 or col == -1:
            return True
        numbersList = list(range(1,10))
        random.shuffle(numbersList)
        for i in numbersList:
            if self.isValid(row,col,i):
                self.board[row][col] = i
                if self.dfs():
                    return True
        self.board[row][col] = 0
        return False

def redraw_window(win, board, time, mistakes):
    win.fill((255,255,255))
    time = timefont.render("Time: " + time, 1, (0,0,0))
    win.blit(time, (540 - 160, 560))
    mistakes = timefont.render("Mistakes: " + str(mistakes), 1, (0,0,0))
    win.blit(mistakes, (30, 560))
    board.draw()

def format_time(secs):
    sec = secs%60
    minute = secs//60
    if sec < 10:
        strsec = "0" + str(sec)
    else:
        strsec = str(sec)
    mat = " " + str(minute) + ":" + strsec
    return mat
    
def newGame(difficulty):  
    
    mygenerator = Generator()
    mygenerator.newBoard()
    answers = mygenerator.board
    mygenerator.makeBoard(difficulty)
    myboard = mygenerator.board
    
    win = pygame.display.set_mode((540,600))
    pygame.display.set_caption("Sudoku")
    board = Grid(9,9,540,540,win,myboard,answers)
    running = True
    start = time.time()
    
    while running:
        play_time = round(time.time()-start)
        formatted_time = format_time(play_time)
        
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                running = False
            if event.type is pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                board.click(pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    board.pencil(1)
                if event.key == pygame.K_2:
                    board.pencil(2)
                if event.key == pygame.K_3:
                    board.pencil(3)
                if event.key == pygame.K_4:
                    board.pencil(4)
                if event.key == pygame.K_5:
                    board.pencil(5)
                if event.key == pygame.K_6:
                    board.pencil(6)
                if event.key == pygame.K_7:
                    board.pencil(7)
                if event.key == pygame.K_8:
                    board.pencil(8)
                if event.key == pygame.K_9:
                    board.pencil(9)
                if event.key == pygame.K_DELETE:
                    board.clear()
                if event.key == pygame.K_BACKSPACE:
                    board.clear()
                if event.key == pygame.K_SPACE:
                    board.solve()
                if event.key == pygame.K_RETURN:
                    board.submit()
                
        redraw_window(win,board,formatted_time,board.mistakes)
        pygame.display.update()
        if board.verify() == True:
            tk.Tk().wm_withdraw()
            result = messagebox.askokcancel("Program Finished", ("You finished the " + difficulty + " Sudoku in " +\
                                                                 str(formatted_time) + " with " + str(board.mistakes) +\
                                                                 " mistakes, would you like to play again?"))
            if result == True:
                os.execl(sys.executable,sys.executable, *sys.argv)
            else:
                pygame.quit()
        
mydifficulty = None

def setDifficulty(difficulty):
    global mydifficulty
    mydifficulty = difficulty
    window.quit()
    window.destroy()

window = tk.Tk()
window.title("Sudoku Settings")
tk.Label(window, text="Choose Difficulty: ", pady = 10).pack()
    
tk.Button(window,text="easy",width=20,padx=20,command=lambda: setDifficulty("easy")).pack(fill="x")
tk.Button(window,text="medium",width=20,padx=20,command=lambda: setDifficulty("medium")).pack(fill="x")
tk.Button(window,text="hard",width=20,padx=20,command=lambda: setDifficulty("hard")).pack(fill="x")

window.mainloop()
newGame(mydifficulty)
pygame.quit()