import random
from Pacman import Pacman
from Ghost import Ghost
from settings import *


class GameState:
    def __init__(self):
        self.generate_maze()
        self.pacman = Pacman(GRID_SIZE//2, GRID_SIZE//2)
        self.ghosts = [
            Ghost(1, 1, 'ASTAR', RED, 'ghost_red'),              
            Ghost(GRID_SIZE-2, 1, 'BFS', BLUE, 'ghost_blue'),               
            Ghost(1, GRID_SIZE-2, 'GREEDY', GREEN, 'ghost_green') 
        ]
        
        self.crystals = self.spawn_items(300, set())
        self.red_crystals = self.spawn_items(3, self.crystals)
        self.purple_crystals = self.spawn_items(3, self.crystals.union(self.red_crystals))
        self.phase = 1
        self.exit_pos = None

    def generate_maze(self):
        self.maze = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        for i in range(GRID_SIZE):
            self.maze[0][i] = self.maze[GRID_SIZE-1][i] = 1
            self.maze[i][0] = self.maze[i][GRID_SIZE-1] = 1
        for _ in range(600):
            rx, ry = random.randint(2, GRID_SIZE-3), random.randint(2, GRID_SIZE-3)
            self.maze[ry][rx] = 1
        self.maze[GRID_SIZE//2][GRID_SIZE//2] = 0

    def spawn_items(self, count, exclude_set):
        items = set()
        while len(items) < count:
            rx, ry = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
            if self.maze[ry][rx] == 0 and (rx, ry) != (self.pacman.x, self.pacman.y) and (rx, ry) not in exclude_set:
                items.add((rx, ry))
        return items

    def check_phase(self):
        if self.phase == 1 and self.pacman.crystals >= 50:
            self.phase = 2
            self.exit_pos = (2, GRID_SIZE-3) if self.pacman.x > GRID_SIZE//2 else (GRID_SIZE-3, 2)
            self.maze[self.exit_pos[1]][self.exit_pos[0]] = 0 