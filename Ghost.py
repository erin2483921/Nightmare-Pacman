from Pacman import Entity
from algorithm import a_star_search, bfs_search, greedy_bfs_search
from settings import *


class Ghost(Entity):
    def __init__(self, x, y, algo, color, img_key):
        super().__init__(x, y)
        self.algo = algo
        self.color = color
        self.img_key = img_key
        self.path = []
        self.base_delay = 6
        self.current_delay = 6

    def update_path(self, maze, tx, ty):
        start_x = self.x + (self.dx if self.move_counter > 0 else 0)
        start_y = self.y + (self.dy if self.move_counter > 0 else 0)

        if self.algo == 'ASTAR': new_path = a_star_search(maze, (start_x, start_y), (tx, ty))
        elif self.algo == 'BFS': new_path = bfs_search(maze, (start_x, start_y), (tx, ty))
        elif self.algo == 'GREEDY': new_path = greedy_bfs_search(maze, (start_x, start_y), (tx, ty))
        self.path = new_path

    def move(self, phase, is_pacman_fast):
        self.anim_tick += 1
        self.current_delay = max(4, int(self.base_delay / 1.5)) if phase == 2 else self.base_delay
        if is_pacman_fast: self.current_delay *= 2
        
        if self.move_counter == 0:
            if self.path:
                next_node = self.path.pop(0)
                self.dx = next_node[0] - self.x
                self.dy = next_node[1] - self.y
                self.update_facing(self.dx, self.dy)
                if self.dx != 0 or self.dy != 0:
                    self.move_counter += 1
            else:
                self.dx, self.dy = 0, 0
        else:
            self.move_counter += 1
            if self.move_counter >= self.current_delay:
                self.x += self.dx
                self.y += self.dy
                self.move_counter = 0
                self.dx, self.dy = 0, 0
