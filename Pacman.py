import pygame
from settings import *

class Entity:
    """Lớp cơ sở cho các thực thể có thể di chuyển và có hướng (Pacman, Ghost)"""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.dx, self.dy = 0, 0
        self.move_counter = 0
        self.facing = 0 # 0: Right, 1: Left, 2: Up, 3: Down
        self.anim_tick = 0

    def update_facing(self, dx, dy):
        if dx == 1: self.facing = 0
        elif dx == -1: self.facing = 1
        elif dy == -1: self.facing = 2
        elif dy == 1: self.facing = 3

    def get_frame_index(self):
        """Tính toán index của ảnh trong mảng 8 frame dựa trên hướng và thời gian"""
        # Mỗi hướng chiếm 2 frames: (facing * 2) + frame_động (0 hoặc 1)
        # Thay đổi frame mỗi 15 ticks
        dynamic_frame = (self.anim_tick // 15) % 2 
        return (self.facing * 2) + dynamic_frame

class Pacman(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.crystals = 0
        self.vision_timer = 0  
        self.speed_timer = 0   
        self.next_dx, self.next_dy = 0, 0 
        self.move_delay = 6   

    def set_direction(self, dx, dy):
        self.next_dx, self.next_dy = dx, dy

    def update_move(self, maze):
        self.anim_tick += 1 # Luôn tăng để tạo hiệu ứng nhai
        
        if self.move_counter == 0:
            if self.next_dx != 0 or self.next_dy != 0:
                nx, ny = self.x + self.next_dx, self.y + self.next_dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and maze[ny][nx] == 0:
                    self.dx, self.dy = self.next_dx, self.next_dy
                    self.update_facing(self.dx, self.dy)
                    
            if self.dx != 0 or self.dy != 0:
                nx, ny = self.x + self.dx, self.y + self.dy
                if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and maze[ny][nx] == 0):
                    self.dx, self.dy = 0, 0
                    
            if self.dx != 0 or self.dy != 0:
                self.move_counter += 1
        else:
            self.move_counter += 1
            if self.move_counter >= self.move_delay:
                self.x += self.dx
                self.y += self.dy
                self.move_counter = 0

    def update_buffs(self):
        if self.vision_timer > 0: self.vision_timer -= 1
        if self.speed_timer > 0: self.speed_timer -= 1

    def dash(self, game):
        """Kỹ năng lướt tức thì đến khi đụng tường và gom vật phẩm"""
        # 1. Xác định hướng lướt: Ưu tiên hướng đang di chuyển, hoặc hướng quay mặt
        dash_dx, dash_dy = self.dx, self.dy
        if dash_dx == 0 and dash_dy == 0:
            dash_dx, dash_dy = self.next_dx, self.next_dy
            
        # Nếu vẫn đang đứng yên hoàn toàn, lấy hướng đang quay mặt 
        if dash_dx == 0 and dash_dy == 0:
            if self.facing == 0: dash_dx, dash_dy = 1, 0    # Phải
            elif self.facing == 1: dash_dx, dash_dy = -1, 0 # Trái
            elif self.facing == 2: dash_dx, dash_dy = 0, -1 # Lên
            elif self.facing == 3: dash_dx, dash_dy = 0, 1  # Xuống
            
        if dash_dx == 0 and dash_dy == 0: 
            return # Không có hướng thì không làm gì cả

        # 2. Hủy trạng thái đang trượt dở dang của LERP
        self.move_counter = 0
        self.dx, self.dy = 0, 0
        self.next_dx, self.next_dy = 0, 0

        # 3. Lặp liên tục để lướt đi trong 1 khung hình
        while True:
            nx, ny = self.x + dash_dx, self.y + dash_dy
            
            # Kiểm tra xem ô tiếp theo có phải tường không
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and game.maze[ny][nx] == 0:
                # Cập nhật vị trí
                self.x, self.y = nx, ny
                
                # --- NHẶT PHA LÊ NGAY TRÊN ĐƯỜNG LƯỚT ---
                pos = (self.x, self.y)
                if pos in game.crystals:
                    game.crystals.remove(pos)
                    self.crystals += 1
                    game.check_phase()
                if pos in game.red_crystals:
                    game.red_crystals.remove(pos)
                    self.vision_timer = 60 * 5  # FPS * 5
                if pos in game.purple_crystals:
                    game.purple_crystals.remove(pos)
                    self.speed_timer = 60 * 5   # FPS * 5
            else:
                break # Đụng tường thì thoát vòng lặp ngay lập tức
