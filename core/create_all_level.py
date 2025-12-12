"""
Create ALL level files (level1.txt through level500.txt)
FIXED: Proper finish flag markers and power-up collision
Run this once to generate all level files
"""
import os

# Create levels directory
os.makedirs('levels', exist_ok=True)

# ============================================
# LEVEL 1 - Tutorial
# ============================================
level1 = """
..........................................
..........................................
.....C.........C.........C................
....###.......###.......###...............
P...................E.....................
########..............................####
............C.........C...................
........#########.#########...............
..........................................
..........................^...............
.................................####.....
.....................................C...G
######################################.###
"""

# ============================================
# LEVEL 2 - Basic platforming
# ============================================
level2 = """
..........................................
.........S............................C...
........###..........................###..
..C............................C..........
.###.......E..................###.........
P.........................................
####.......................###............
...........C.........C....................
.......########.########..................
.............................^............
................................###.......
........................................CG
######################################.###
"""

# Write level 1 and 2
with open('levels/level1.txt', 'w') as f:
    f.write(level1.strip())
print("✓ Created levels/level1.txt")

with open('levels/level2.txt', 'w') as f:
    f.write(level2.strip())
print("✓ Created levels/level2.txt")

# Now run the advanced generator for levels 3-500
import random

WIDTH = 280
HEIGHT = 13
SECTION_WIDTH = 70

def create_level_3():
    """Tutorial level with power-ups"""
    return """..........................................................................C...............C...............C.......................................C.....C.....C...................................C.....C.................C...C...C.................................C..............................
..........................................................................###.............###.............###......................................###...###...###.................................###...###................###.###.###...............................###.............................
........S.....................................................................E.................E.....................................E.............................E.....................E.....................E.......................E.............................
...C...###............C...............C.......................................###.....................................................................##.....############.............C...C.......................................############.###..........................................................
.###..............H..###.............###..............................................C.....C.....C.....................................................C................................................................C.....C.......................................................
P.................###................E.........................................#################.....................................................############.###..........J.............................................############.###..........................................................
###.....................................................................##................................................................................................................................................................................................................
........C.....C.....C.....................................................................................C...................................................................C..........................................C............................C...............................
....#################..............................................................................########.###.###.###................................................############.....................................................###############........................................................
...........................C...C...C......................................^..................................................................^......^......................................^...............########............^................................^...............
...........^...........#############..................^.......................########...............................................^.........................................########.....................................^......................^...............########............^...............
..............................................................C...........F...........................C...............................F...............................................................C...........F..................................................................C.......G
##################################################################.####################################.#######################################################################.#######################################################################.#######"""

def generate_section(section_type, level_num, section_num, num_enemies, num_coins, num_spikes, num_powerups):
    """Generate one section (70 chars wide) of a level"""
    lines = [['.' for _ in range(SECTION_WIDTH)] for _ in range(HEIGHT)]
    
    random.seed(level_num * 1000 + section_num)
    powerup_types = ['S', 'H', 'J', 'D']
    
    # Power-ups with platforms
    if section_num > 0 and num_powerups > 0 and random.random() > 0.5:
        powerup_pos = random.randint(10, SECTION_WIDTH - 15)
        powerup_type = random.choice(powerup_types)
        lines[2][powerup_pos] = powerup_type
        for j in range(powerup_pos - 3, min(powerup_pos + 4, SECTION_WIDTH)):
            lines[3][j] = '#'
    
    # Coins and platforms
    if section_type == 0:
        for i in range(min(3, num_coins)):
            pos = 8 + i * 18
            if pos < SECTION_WIDTH - 5:
                lines[3][pos] = 'C'
                for j in range(pos-2, min(pos+3, SECTION_WIDTH)):
                    lines[4][j] = '#'
    elif section_type == 1:
        positions = [10, 27, 44]
        for i, pos in enumerate(positions[:min(3, num_coins)]):
            if pos < SECTION_WIDTH - 5:
                lines[3][pos] = 'C'
                for j in range(pos-2, min(pos+3, SECTION_WIDTH)):
                    lines[4][j] = '#'
    elif section_type == 2:
        for i in range(min(4, num_coins)):
            pos = 10 + i * 12
            if pos < SECTION_WIDTH - 5:
                lines[3][pos] = 'C'
                for j in range(pos-1, min(pos+2, SECTION_WIDTH)):
                    lines[4][j] = '#'
    else:
        for i in range(min(5, num_coins)):
            pos = 15 + i * 10
            if pos < SECTION_WIDTH - 5:
                lines[3][pos] = 'C'
                for j in range(pos-1, min(pos+2, SECTION_WIDTH)):
                    lines[4][j] = '#'
    
    # Player and enemies
    if section_num == 0:
        lines[5][0] = 'P'
    
    for i in range(num_enemies):
        enemy_pos = 20 + i * 20
        if enemy_pos < SECTION_WIDTH - 5:
            enemy_type = 'F' if (level_num + i) % 3 == 0 and level_num > 5 else 'E'
            lines[5][enemy_pos] = enemy_type
    
    # Main platform
    if section_num == 0:
        for i in range(min(10, SECTION_WIDTH)):
            lines[6][i] = '#'
    
    for i in range(max(0, SECTION_WIDTH - 10), SECTION_WIDTH):
        lines[6][i] = '#'
    
    # Middle platforms
    if num_powerups > 1 and section_num == 2 and random.random() > 0.4:
        powerup_pos = random.randint(20, SECTION_WIDTH - 25)
        powerup_type = random.choice(powerup_types)
        lines[7][powerup_pos] = powerup_type
        for j in range(powerup_pos - 3, min(powerup_pos + 4, SECTION_WIDTH)):
            lines[8][j] = '#'
    
    if section_type == 0:
        platform_start = 12 + (section_num * 5)
        for i in range(platform_start, min(platform_start + 15, SECTION_WIDTH)):
            lines[8][i] = '#'
    elif section_type == 1:
        lines[8][10:25] = ['#'] * 15
        if 40 < SECTION_WIDTH:
            lines[8][40:55] = ['#'] * min(15, SECTION_WIDTH - 40)
    elif section_type == 2:
        for start in [12, 28, 44]:
            if start + 6 < SECTION_WIDTH:
                lines[8][start:start+6] = ['#'] * 6
    else:
        lines[8][10:50] = ['#'] * min(40, SECTION_WIDTH - 10)
    
    if num_coins > 5:
        mid_coin_pos = random.randint(20, SECTION_WIDTH - 20)
        if lines[7][mid_coin_pos] == '.':
            lines[7][mid_coin_pos] = 'C'
    
    if num_coins > 8 and random.random() > 0.5:
        lines[9][random.randint(20, SECTION_WIDTH - 20)] = 'C'
    
    # Spikes
    for i in range(num_spikes):
        spike_pos = 10 + i * 12
        if spike_pos < SECTION_WIDTH - 5:
            lines[10][spike_pos] = '^'
    
    platform_start = 8 + (section_num * 3)
    platform_len = 10 + (section_num * 2)
    for i in range(platform_start, min(platform_start + platform_len, SECTION_WIDTH - 8)):
        if lines[10][i] != '^':
            lines[10][i] = '#'
    
    # FINISH in last section
    if section_num == 3:
        if num_powerups > 2 and random.random() > 0.3:
            powerup_pos = SECTION_WIDTH - 18
            lines[11][powerup_pos] = random.choice(powerup_types)
        
        if num_coins > 10:
            lines[11][SECTION_WIDTH - 12] = 'C'
        
        # ✅ FINISH FLAG - USE 'G'
        lines[11][SECTION_WIDTH - 2] = 'G'
    
    # Bottom platform
    for i in range(SECTION_WIDTH):
        lines[12][i] = '#'
    
    if section_num == 3:
        for i in range(SECTION_WIDTH - 10, SECTION_WIDTH - 1):
            if lines[12][i] != 'G':
                lines[12][i] = '.'
        lines[12][SECTION_WIDTH - 1] = '#'
        lines[12][SECTION_WIDTH - 2] = '#'
    
    return lines

def generate_advanced_level(level_num):
    """Generate level by combining 4 sections"""
    difficulty = min((level_num - 10) / 490.0, 1.0)
    num_enemies = min(1 + (level_num // 15), 6)
    num_coins = min(4 + (level_num // 8), 15)
    num_spikes = min((level_num // 25), 8)
    num_powerups = min(1 + (level_num // 20), 4)
    
    section_types = [
        (level_num + 0) % 4,
        (level_num + 1) % 4,
        (level_num + 2) % 4,
        (level_num + 3) % 4
    ]
    
    all_sections = []
    for i in range(4):
        section_enemies = num_enemies // 4 + (1 if i < num_enemies % 4 else 0)
        section_coins = num_coins // 4 + (1 if i < num_coins % 4 else 0)
        section_spikes = num_spikes // 4 + (1 if i < num_spikes % 4 else 0)
        section_powerups = num_powerups // 4 + (1 if i < num_powerups % 4 else 0)
        
        section = generate_section(
            section_types[i], level_num, i,
            section_enemies, section_coins, section_spikes, section_powerups
        )
        all_sections.append(section)
    
    combined_lines = []
    for row in range(HEIGHT):
        row_line = []
        for section in all_sections:
            row_line.extend(section[row])
        combined_lines.append(''.join(row_line))
    
    return '\n'.join(combined_lines)

# Generate level 3
with open('levels/level3.txt', 'w') as f:
    f.write(create_level_3())
print("✓ Created levels/level3.txt")

# Generate levels 4-500
for i in range(4, 501):
    level_data = generate_advanced_level(i)
    filename = f'levels/level{i}.txt'
    with open(filename, 'w') as f:
        f.write(level_data)
    if i <= 10 or i % 50 == 0:
        print(f"✓ Created {filename}")

print(f"\n{'='*60}")
print(f"✅ Successfully created 500 level files!")
print(f"{'='*60}")
print("\nMarker Reference:")
print("  P = Player spawn")
print("  E = Ground enemy")
print("  F = Flying enemy")
print("  C = Coin")
print("  ^ = Spike")
print("  G = FINISH FLAG ✅")
print("  S = Speed power-up ⚡")
print("  H = Health power-up ❤️")
print("  J = Triple Jump power-up ↑")
print("  D = Shield power-up 🛡️")
print(f"{'='*60}")