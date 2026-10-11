import heapq  
from collections import deque
from settings import *
import base64

def neighbors(x, y, map):
    neighbors = []
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and map[ny][nx] == 0:
            neighbors.append((nx, ny))
    return neighbors

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(map, start, goal):
    frontier = [] 
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost = {start: 0}
    while frontier: 
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        for next_node in neighbors(*current, map):
            new_cost = cost[current] + 1
            if next_node not in cost or new_cost < cost[next_node]:
                cost[next_node] = new_cost
                priority = new_cost + heuristic(goal, next_node)
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current
    return reconstruct_path(came_from, start, goal)

def bfs_search(map, start, goal):
    frontier = deque([start]) 
    came_from = {start: None}
    while frontier: 
        current = frontier.popleft() 
        if current == goal:
            break
        for next_node in neighbors(*current, map): 
            if next_node not in came_from:
                frontier.append(next_node) 
                came_from[next_node] = current        
    return reconstruct_path(came_from, start, goal)

def greedy_bfs_search(map, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start)) 
    came_from = {start: None} 
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal: break  
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
