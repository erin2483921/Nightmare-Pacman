# 🦇 Nightmare Pacman - Survival Horror

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)

## 📖 1. Introduction

**Nightmare Pacman** is a 2D game developed in Python using Pygame. Inspired by the legendary arcade game Pac-Man and the horror game Dark Deception, it features eerie dark pixel art and delivers a fast-paced survival experience with a punishing level of difficulty.

## 🎮 2. Gameplay Mechanics

The game has two phases, with increasing tension:

* **Phase 1 (Collection):** Guide Pacman through a dark maze, evade three relentless ghosts, and collect all **300 crystals** scattered across the map.
* **Phase 2 (Escape):** Once all 300 crystals have been collected, an exit portal appears in a corner of the map. The ghosts enter a "Rage" state, and you must escape the maze while they pursue you.

### ✨ Special Features and Abilities

* **Dash (Instant Dash — `Q` Key):** Pacman dashes in a straight line until hitting a wall, collecting every item along the way.
* **Buff System (Power-ups):**
  * 🔴 *Red Crystal:* Slows down the ghosts.
  * 🟣 *Purple Crystal:* Increases Pacman's movement speed for 5 seconds.

## 🧠 3. Algorithms in Action

The project's technical highlight is the "brain" behind each of the three ghosts. Each ghost uses a different pathfinding algorithm, making the chases intense and unpredictable:

* 🔴 **Red Ghost — `A* (A-Star) Search`:** Uses an efficient shortest-path algorithm to reach Pacman's position. This ghost can navigate detours and cut the player off.
* 🔵 **Blue Ghost — `BFS (Breadth-First Search)`:** Explores the maze breadth-first to find the shortest path. Although it may use more computational resources than A*, it provides persistent and accurate pursuit.
* 🟢 **Green Ghost — `Greedy Best-First Search`:** Uses a greedy algorithm guided by a heuristic. This reckless ghost tends to head straight toward Pacman, sometimes getting caught around wall corners and giving the player a chance to escape. :v

## 🏗️ 4. Data Structures

### 📊 Data Structures Used

* **Priority Queue (`heapq`):** Used for the frontier in **A*** and **Greedy Best-First Search** to prioritize nodes with the lowest priority value. Heap insertion and removal take `O(log N)` time.
* **Queue (`collections.deque`):** Used in **BFS** for `O(1)` enqueue and dequeue operations.
* **Set:** Stores crystal coordinates (`game.crystals`). Membership checks and removals when Pacman collects a crystal take `O(1)` time on average.
* **2D Array:** Stores and represents the maze (`maze`) as a `50x50` grid.
* **Dictionary:** Records predecessor relationships to reconstruct paths.
* **Tuple:** Stores coordinates.

## 🛠️ 5. Installation and How to Play

**If you have Python installed:**

1. Clone this repository:

   ```bash
   git clone <...>
   ```

2. Install Pygame:

   ```bash
   pip install pygame
   ```

3. Run the game:

   ```bash
   python main.py
   ```

**Alternatively, download the `.exe` file directly from the Releases section.**
