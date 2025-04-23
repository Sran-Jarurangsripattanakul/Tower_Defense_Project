# Tower Defense Game - Project Description  

## **Overview**  
This project is a **Python-based Tower Defense game** built using **Pygame** and **PyTMX** for map loading. The game follows classic tower defense mechanics where players place defensive towers along a path to stop waves of enemies from reaching their destination.  

### **Key Features (Implemented & Planned)**  

#### **Core Gameplay**  
✅ **Pathfinding:** Enemies follow a predefined path extracted from TMX maps.  
✅ **Tower Mechanics:** Basic towers that target and damage enemies within range.  
✅ **Enemy System:** Enemies move along the path and can take damage before being defeated.  
❌ **Wave System:** Currently missing—enemies spawn continuously without structured waves.  
❌ **Currency & Economy:** No money system for building/upgrading towers.  
❌ **Win/Lose Conditions:** No end-game logic (e.g., base health, victory conditions).  

#### **Map & Level System**  
✅ **TMX Map Loading:** Supports tile-based maps with defined paths.  
✅ **Multiple Levels:** Basic level selection menu with progress tracking.  
❌ **Dynamic Difficulty:** Levels do not yet scale in difficulty.  

#### **UI & Visuals**  
✅ **Main Menu & Level Select:** Basic navigation between screens.  
✅ **Tower & Enemy Placeholders:** Simple shapes for debugging.  
❌ **Polished Sprites & Animations:** Missing detailed graphics for towers, enemies, and projectiles.  
❌ **Health Bars & UI Feedback:** No visual indicators for enemy health or tower stats.  

#### **Technical Aspects**  
✅ **Object-Oriented Design:** Clean separation of game logic (enemies, towers, maps).  
✅ **JSON Save System:** Tracks level completion status.  
❌ **Optimizations:** No performance handling for large enemy counts.  
❌ **Error Handling:** Missing robust checks for missing assets.  

---

## **How It Works**  
1. **Main Menu:** Players can start the game, select levels, or quit.  
2. **Level Selection:** Shows locked/unlocked levels (saved via JSON).  
3. **Gameplay:**  
   - Enemies spawn and follow a path.  
   - Pre-placed towers attack enemies in range.  
   - No player tower placement yet (planned feature).  
4. **Game Loop:**  
   - Enemies move → Towers shoot → Enemies die or reach the end.  
   - Currently infinite; no win/lose state.  

---

## **Future Improvements**  
- **Wave System:** Structured enemy waves with increasing difficulty.  
- **Tower Shop:** Let players buy/upgrade towers using in-game currency.  
- **Visual Polish:** Add sprites, animations, and sound effects.  
- **More Levels:** Expand with varied maps and enemy types.  
- **Game Balance:** Adjust tower stats, enemy health, and spawn rates.  

---

## **Dependencies**  
- **Pygame** (2D rendering)  
- **PyTMX** (TMX map loading)  

This project is **functional but incomplete**, serving as a foundation for a full tower defense game. With additional features and polish, it could become a complete, engaging experience.
