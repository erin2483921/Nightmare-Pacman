import heapq  
from collections import deque
from settings import *
import base64

def neighbors(x, y, map):
    #tìm các ô liền kề
    neighbors = []
    for dx, dy in DIRECTIONS: #lấy các chỉ số chỉ trên dưới trái phải
        nx, ny = x + dx, y + dy
        # Nằm trong bản đồ và ô đó không phải là tường (map == 0)
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and map[ny][nx] == 0:
            neighbors.append((nx, ny))
    return neighbors


def heuristic(a, b):
    #tính chi phí từ node a đến node b
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star_search(map, start, goal):

    #ưuu tiên node có tổng chi phí f(n) = g(n) + h(n) nhỏ nhất

    frontier = [] # Tạo hàng đợi ưu tiên
    heapq.heappush(frontier, (0, start)) # Đưa node gốc vào Hàng đợi ưu tiên (ưu tiên = 0)
    came_from = {start: None}            # Dictionary lưu vết: {node_hiện_tại: node_cha}
    cost = {start: 0}                    # Dictionary lưu g(n): Chi phí thực tế từ gốc tới node
    
    while frontier: #Duyệt qua hàng đợi
        _, current = heapq.heappop(frontier)# Lấy ra node có f(n) nhỏ nhất
        if current == goal:    # nếu là goal thì dừng
            break

        for next_node in neighbors(*current, map):
            new_cost = cost[current] + 1  # Tính g(n) mới (mỗi bước tốn 1 chi phí)
            # Nếu node kề chưa đi qua hoặc tìm được đường đi tới nó có chi phí rẻ hơn thì cập nhật g(n) đưa vào hàng đợi ưu tiển và lưu lại đường đi
            
            if next_node not in cost or new_cost < cost[next_node]:
                cost[next_node] = new_cost                        # Cập nhật g(n)
                priority = new_cost + heuristic(goal, next_node)  # Tính f(n) = g(n) + h(n)
                heapq.heappush(frontier, (priority, next_node))  # Đẩy vào Priority Queue
                came_from[next_node] = current                   # Lưu vết
    return reconstruct_path(came_from, start, goal)



def bfs_search(map, start, goal):
    # Thuật toán BFS duyệt theo chiều rộng, lan tỏa đểu ra xung quanh
    frontier = deque([start])    # Khởi tạo hàng đợi 2 đầu
    came_from = {start: None}    # Lưu đường đi
    
    while frontier: # Duyệt qua các phần tử trong hàng đợi
        current = frontier.popleft() # Lấy node bên trái của hàng đợi
        if current == goal: #nếu là đích thì dừng
            break

        for next_node in neighbors(*current, map): #Duyệt các node liền kề với nó
            if next_node not in came_from:        # Kiểm tra xem đã đi qua node này hay chưa
                frontier.append(next_node)       # Đẩy node kề vào cuối hàng đợi
                came_from[next_node] = current    # Đánh dấu đã thăm và lưu vết
                
    return reconstruct_path(came_from, start, goal)



def greedy_bfs_search(map, start, goal):

    # Thuật toán Tham lam, chỉ nhìn vào h(n) để đi về hướng đích không màn tới cost chỉ cần đến đích nhanh nhất

    frontier = []
    heapq.heappush(frontier, (0, start)) # Hàng đợi ưu tiên
    came_from = {start: None}            # Lưu dấu vết
    
    while frontier:
        _, current = heapq.heappop(frontier) # Lấy ra node gần đích nhất theo ước lượng h(n)
        if current == goal: break            # nếu tới đích thì dừng
        
        for next_node in neighbors(*current, map):  
            if next_node not in came_from:                      
                priority = heuristic(goal, next_node)           
                heapq.heappush(frontier, (priority, next_node))  
                came_from[next_node] = current                    
                
    return reconstruct_path(came_from, start, goal)


def reconstruct_path(came_from, start, goal):
    if goal not in came_from: return [] 

    current = goal
    path = []
    while current != start:         
        path.append(current)        
        current = came_from[current]
        
    path.reverse() 
    return path

def decrypt(data):
    ciphertext = base64.b64decode(data)
    flag_part_1 = "VzF7SV80bV9hXw=="
    key = base64.b64decode(flag_part_1)

    return bytes(
        value ^ key[i % len(key)]
        for i, value in enumerate(ciphertext)
    )
