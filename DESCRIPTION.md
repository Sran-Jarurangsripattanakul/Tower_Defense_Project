# Tower Defense

A Python/Pygame tower-defense game where you place & upgrade towers to stop waves of enemies.

---

## 📝 Project Overview

This project is a Tower Defense game. The player places towers to prevent waves of enemies from reaching a base. Towers have different attack types, and enemies grow tougher each wave. Clearing all 15 waves on one map unlocks the next map.

---

## 🔍 Genre & Inspiration

A well-known example in this genre is **Bloons Tower Defense**, where you place monkey towers to pop balloons.  
My version focuses on:

- Simpler mechanics  
- Basic AI-controlled enemy movement  
- Data tracking & analysis for performance

---

## 🎮 Gameplay Concept

- **Grid-based map** with predefined tower slots  
- **15 waves** per level; bosses on waves 5, 10, 15  
- **Towers** auto-attack any enemy in range  
- **Budget** is earned from defeated enemies  
- **Game over** when base HP drops to 0 or after wave 15  
- **Unlock progression**: Completing wave 15 on level N unlocks level N+1  

---

## 🚀 Key Features

- **Tower types**:  
  - Archer (fast, single-target)  
  - Cannon (area-damage)  
  - Magic (piercing)  
  - Ice (slow effect)  
- **Enemy variety**:  
  - Level 1: Goblin, Orc, Troll, Boss  
  - Level 2: Slime, Werewolf, Werebear, OrcRider  
- **Resource management**: Earn money → build & upgrade towers  
- **Speed toggle**, **pause**, **restart**  

---

## 🏗️ Object-Oriented Design

| Class         | Responsibilities                                        |
|--------------:|:--------------------------------------------------------|
| **GameManager** | Game loop, waves, stats logging, UI buttons           |
| **Map**         | Load TMX maps, draw tiles & path, tower slot positions |
| **Tower**       | Attack logic, upgrades, sell/refund                    |
| **Enemy**       | Movement along path, animations, health & damage      |
| **Projectile**  | Travel to target, apply damage                         |

---

## ⚙️ Algorithms

1. **Pathfinding**  
   Enemies follow a precomputed A★ path across tiles.  
2. **Target sorting**  
   Towers choose the closest/enemy‐least‐health based on proximity.  
3. **Event-driven**  
   Towers fire when an enemy enters range; waves spawn on timer or button.  
4. **Dynamic difficulty**  
   Enemy HP/speed scale with wave number.

---

## 📊 Data Tracking & Analysis

We record per-wave metrics to `game_stats.csv`:

| Wave | Enemies Defeated | Towers Placed | Placement Effectiveness | Damage Dealt | Wave Time (ms) | Currency Spent |
|:----:|:----------------:|:-------------:|:-----------------------:|:------------:|:--------------:|:--------------:|
|  1   |        …         |      …        |           …             |      …       |       …        |       …        |

### 🔢 Why these metrics?

- **Enemies Defeated**: Balances wave difficulty  
- **Placement Efficiency**: Strategy effectiveness  
- **Damage Dealt**: Tower power vs. enemy bulk  
- **Wave Time**: Pacing & difficulty spikes  
- **Resource Utilization**: Spending vs. performance  

We’ll collect **≥ 50 waves** worth of data (across sessions) and visualize via Pandas & Matplotlib:

- **Line graph** for enemies/wave  
- **Scatter** for placement efficiency  
- **Bar chart** for damage  
- **Histogram** for wave times  
- **Pie chart** for avg spending

A simple viewer script (`stats_viewer.py`) or Jupyter notebook can generate these charts.

---

## 📅 Weekly Milestones

| Week                    | Goals                                                     |
|:------------------------|:----------------------------------------------------------|
| 26 Mar –  2 Apr         | Basic map & tower placement                               |
|  3 Apr –  9 Apr         | Enemy AI movement & pathfinding                           |
| 10 Apr – 16 Apr         | Shooting mechanics, damage, upgrades                      |
| 17 Apr – 23 Apr         | UI polish, resource tracking                              |
| 24 Apr – 11 May         | Data collection, analysis tooling, bugfixes, final demo   |

---

## 📐 UML Class Diagram

![Image](https://github.com/user-attachments/assets/319b5df5-b243-4b4c-ad49-c3f39a9b8df4)

*(Place your `tower_defense_class_diagram.png` under `assets/uml/`.)*

---

## 📂 Repo Structure

```text
TowerDefense/
├── assets/
│   ├── maps/
│   ├── enemy/
│   ├── icon/
│   └── uml/
├── screenshots/
│   ├── gameplay/
│   └── visualization/
├── main_menu.py
├── game_manager.py
├── maps.py
├── enemy.py
├── tower.py
├── projectile.py
├── stats_viewer.py
├── game_stats.csv
├── README.md
├── DESCRIPTION.md
├── requirements.txt
└── LICENSE
