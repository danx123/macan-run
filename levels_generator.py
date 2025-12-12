"""
Generate level3.txt to level500.txt for platformer game
Run this script to create all level files with varied layouts
"""
import os
import random

# Create levels directory if it doesn't exist
os.makedirs('levels', exist_ok=True)

# Template dimensions: 70 chars wide, 13 rows tall
WIDTH = 70
HEIGHT = 13

def create_level_3():
    return """..........................................................................
..........................................................................
..........................................................................
..C...............C...............C.......................................
.###.............###.............###......................................
P.................E.................E.....................................
###.....................................................................##
........C.....C.....C.....................................................
....#################.....................................................
...........................C...C...C......................................
...........^...........#############..................^...................
..............................................................C...........F
##################################################################.#######"""

def create_level_4():
    return """..........................................................................
..........................................................................
.........C.......C.......C....................................................
........###.....###.....###...................................................
P...........................................E.................................
####................................................................##########
............C...........C...........C.........................................
....########...........###.........###........................................
.......................................C......................................
.....................^.............####.......................................
...............########################...................^...................
..................................................................C.......F
##################################################################.#######"""

def create_level_5():
    return """..........................................................................
..........................................................................
..........................................................................
....C...C...C.....................................C.......................
...###.###.###...................................###......................
P.....................E.................E.................................
######..............................................................######
....................C.....C.....C.........................................
............############.###.###..........................................
.......^..................................................................
...########...............................................^...............
.....................................................C....................F
##################################################################.#######"""

def create_level_6():
    return """..........................................................................
..........................................................................
.C.................................C......................................
###...............................###.....................................
P......C.................E................................................
####..###............................................................#####
................C.....................................................
........############..........C...C...C...................................
...................................###.###.###............................
..............^...........................................................
..................########................................^...............
.........................................................C................F
##################################################################.#######"""

def create_level_7():
    return """..........................................................................
..........................................................................
..........................................................................
..C.....C.....C...................................C.....C.................
.###...###...###.................................###...###................
P.............................E.....................E.....................
#####...............................................................######
.............C................................................................
.....############.............C...C.......................................
...........................########.......................................
................^.................................................^.......
.....................................................................C....F
##################################################################.#######"""

def create_level_8():
    return """..........................................................................
..........................................................................
........C.........C.........C.................................................
.......###.......###.......###................................................
P...................................E.....................................
######........................................................................
..............C.......C.......C...........................................
......########.###.###.###................................................
..........................................C...............................
..................................########................................
...............^..........................................^...............
..............................................................C...........F
##################################################################.#######"""

def create_level_9():
    return """..........................................................................
..........................................................................
..........................................................................
.C...C...C.................................C..............................
###.###.###...............................###.............................
P...................E.......................E.............................
#####...............................................................######
................C.....C.......................................................
....############.###..........................................................
.............................................C............................
......................^...............########............^...............
..................................................................C.......F
##################################################################.#######"""

def create_level_10():
    return """..........................................................................
..........................................................................
.....C.........C.........C....................................................
....###.......###.......###...................................................
P.......................................E.................................
#######.................................................................######
....................C.....C...........................................
............############.###..........................................
.......^..................................................................
...########...........................................C...................
..............................................########....................
.....................................................................C....F
##################################################################.#######"""

def generate_advanced_level(level_num):
    """Generate varied levels with different layouts"""
    
    # Seed untuk konsistensi
    random.seed(level_num)
    
    # Calculate difficulty
    difficulty = min((level_num - 10) / 490.0, 1.0)
    num_enemies = min(1 + (level_num // 15), 6)
    num_coins = min(4 + (level_num // 8), 15)
    num_spikes = min((level_num // 25), 8)
    
    # Pilih layout pattern berdasarkan level
    layout_type = level_num % 8
    
    lines = []
    
    # Empty top rows
    for _ in range(3):
        lines.append('.' * WIDTH)
    
    # LAYOUT 1: Staircase ascending
    if layout_type == 0:
        # Row 4: Coins at different heights
        coin_row = ['.'] * WIDTH
        plat_row = ['.'] * WIDTH
        for i in range(min(3, num_coins)):
            pos = 8 + i * 18
            if pos < WIDTH - 5:
                coin_row[pos] = 'C'
                plat_row[pos-1:pos+2] = ['#'] * 3
        lines.append(''.join(coin_row))
        lines.append(''.join(plat_row))
        
        # Row 6: Player and enemy
        entity_row = ['.'] * WIDTH
        entity_row[0] = 'P'
        if num_enemies >= 1:
            entity_row[35] = 'E'
        lines.append(''.join(entity_row))
        
        # Row 7: Starting platform
        main_plat = ['#'] * 8 + ['.'] * (WIDTH - 18) + ['#'] * 10
        lines.append(''.join(main_plat))
        
        # Row 8-9: Ascending platforms
        mid_coin = ['.'] * WIDTH
        mid_plat = ['.'] * WIDTH
        step_start = 12
        for i in range(3):
            start = step_start + i * 15
            if start + 8 < WIDTH:
                mid_plat[start:start+8] = ['#'] * 8
                if i < num_coins - 3:
                    mid_coin[start + 3] = 'C'
        lines.append(''.join(mid_coin))
        lines.append(''.join(mid_plat))
    
    # LAYOUT 2: Gap jumping
    elif layout_type == 1:
        coin_row = ['.'] * WIDTH
        plat_row = ['.'] * WIDTH
        # Platforms with gaps
        plat_row[5:15] = ['#'] * 10
        coin_row[10] = 'C'
        plat_row[22:32] = ['#'] * 10
        coin_row[27] = 'C'
        plat_row[39:49] = ['#'] * 10
        coin_row[44] = 'C'
        lines.append(''.join(coin_row))
        lines.append(''.join(plat_row))
        
        entity_row = ['.'] * WIDTH
        entity_row[0] = 'P'
        if num_enemies >= 1:
            entity_row[25] = 'E'
        if num_enemies >= 2:
            entity_row[55] = 'E'
        lines.append(''.join(entity_row))
        
        main_plat = ['#'] * 5 + ['.'] * (WIDTH - 15) + ['#'] * 10
        lines.append(''.join(main_plat))
        
        mid_coin = ['.'] * WIDTH
        mid_plat = ['.'] * WIDTH
        mid_plat[15:40] = ['#'] * 25
        mid_coin[25] = 'C'
        lines.append(''.join(mid_coin))
        lines.append(''.join(mid_plat))
    
    # LAYOUT 3: Vertical challenges
    elif layout_type == 2:
        coin_row = ['.'] * WIDTH
        plat_row = ['.'] * WIDTH
        for i in range(min(4, num_coins)):
            pos = 10 + i * 12
            if pos < WIDTH - 5:
                coin_row[pos] = 'C'
                plat_row[pos-1:pos+2] = ['#'] * 3
        lines.append(''.join(coin_row))
        lines.append(''.join(plat_row))
        
        entity_row = ['.'] * WIDTH
        entity_row[0] = 'P'
        for i in range(min(2, num_enemies)):
            entity_row[25 + i * 20] = 'E'
        lines.append(''.join(entity_row))
        
        main_plat = ['#'] * 6 + ['.'] * (WIDTH - 16) + ['#'] * 10
        lines.append(''.join(main_plat))
        
        mid_coin = ['.'] * WIDTH
        mid_plat = ['.'] * WIDTH
        # Short scattered platforms
        positions = [12, 28, 44]
        for pos in positions:
            if pos + 6 < WIDTH:
                mid_plat[pos:pos+6] = ['#'] * 6
        lines.append(''.join(mid_coin))
        lines.append(''.join(mid_plat))
    
    # LAYOUT 4: Long platform with obstacles
    elif layout_type == 3:
        coin_row = ['.'] * WIDTH
        plat_row = ['.'] * WIDTH
        # Coins above long platform
        for i in range(min(5, num_coins)):
            pos = 15 + i * 10
            if pos < WIDTH - 5:
                coin_row[pos] = 'C'
        lines.append(''.join(coin_row))
        lines.append(''.join(plat_row))
        
        entity_row = ['.'] * WIDTH
        entity_row[0] = 'P'
        if num_enemies >= 1:
            entity_row[30] = 'E'
        if num_enemies >= 2:
            entity_row[50] = 'E'
        lines.append(''.join(entity_row))
        
        main_plat = ['#'] * 8 + ['.'] * (WIDTH - 18) + ['#'] * 10
        lines.append(''.join(main_plat))
        
        mid_coin = ['.'] * WIDTH
        mid_plat = ['.'] * WIDTH
        # One long platform
        mid_plat[10:55] = ['#'] * 45
        lines.append(''.join(mid_coin))
        lines.append(''.join(mid_plat))
    
    # LAYOUT 5: Zigzag pattern
    elif layout_type == 4:
        coin_row = ['.'] * WIDTH
        plat_row = ['.'] * WIDTH
        plat_row[8:18] = ['#'] * 10
        coin_row[13] = 'C'
        plat_row[35:45] = ['#'] * 10
        coin_row[40] = 'C'
        lines.append(''.join(coin_row))
        lines.append(''.join(plat_row))
        
        entity_row = ['.'] * WIDTH
        entity_row[0] = 'P'
        if num_enemies >= 1:
            entity_row[40] = 'E'
        lines.append(''.join(entity_row))
        
        main_plat = ['#'] * 10 + ['.'] * (WIDTH - 20) + ['#'] * 10
        lines.append(''.join(main_plat))
        
        mid_coin = ['.'] * WIDTH
        mid_plat = ['.'] * WIDTH
        mid_plat[20:35] = ['#'] * 15
        mid_coin[27] = 'C'
        lines.append(''.join(mid_coin))
        lines.append(''.join(mid_plat))
    
    # LAYOUT 6: Dense coins with tight platforms
    elif layout_type == 5:
        coin_row = ['.'] * WIDTH
        plat_row = ['.'] * WIDTH
        for i in range(min(6, num_coins)):
            pos = 10 + i * 8
            if pos < WIDTH - 5:
                coin_row[pos] = 'C'
                if i % 2 == 0:
                    plat_row[pos-2:pos+1] = ['#'] * 3
        lines.append(''.join(coin_row))
        lines.append(''.join(plat_row))
        
        entity_row = ['.'] * WIDTH
        entity_row[0] = 'P'
        for i in range(min(3, num_enemies)):
            entity_row[20 + i * 18] = 'E'
        lines.append(''.join(entity_row))
        
        main_plat = ['#'] * 7 + ['.'] * (WIDTH - 17) + ['#'] * 10
        lines.append(''.join(main_plat))
        
        mid_coin = ['.'] * WIDTH
        mid_plat = ['.'] * WIDTH
        mid_plat[12:25] = ['#'] * 13
        mid_plat[35:50] = ['#'] * 15
        lines.append(''.join(mid_coin))
        lines.append(''.join(mid_plat))
    
    # LAYOUT 7: Wave pattern
    elif layout_type == 6:
        coin_row = ['.'] * WIDTH
        plat_row = ['.'] * WIDTH
        positions = [12, 26, 40, 54]
        for i, pos in enumerate(positions):
            if pos < WIDTH - 5:
                coin_row[pos] = 'C'
                plat_row[pos-2:pos+3] = ['#'] * 5
        lines.append(''.join(coin_row))
        lines.append(''.join(plat_row))
        
        entity_row = ['.'] * WIDTH
        entity_row[0] = 'P'
        if num_enemies >= 1:
            entity_row[32] = 'E'
        if num_enemies >= 2:
            entity_row[58] = 'E'
        lines.append(''.join(entity_row))
        
        main_plat = ['#'] * 9 + ['.'] * (WIDTH - 19) + ['#'] * 10
        lines.append(''.join(main_plat))
        
        mid_coin = ['.'] * WIDTH
        mid_plat = ['.'] * WIDTH
        mid_plat[18:33] = ['#'] * 15
        mid_coin[25] = 'C'
        lines.append(''.join(mid_coin))
        lines.append(''.join(mid_plat))
    
    # LAYOUT 8: Mixed challenges
    else:
        coin_row = ['.'] * WIDTH
        plat_row = ['.'] * WIDTH
        plat_row[6:14] = ['#'] * 8
        plat_row[22:28] = ['#'] * 6
        plat_row[38:48] = ['#'] * 10
        coin_row[10] = 'C'
        coin_row[25] = 'C'
        coin_row[43] = 'C'
        lines.append(''.join(coin_row))
        lines.append(''.join(plat_row))
        
        entity_row = ['.'] * WIDTH
        entity_row[0] = 'P'
        if num_enemies >= 1:
            entity_row[28] = 'E'
        if num_enemies >= 2:
            entity_row[48] = 'E'
        lines.append(''.join(entity_row))
        
        main_plat = ['#'] * 6 + ['.'] * (WIDTH - 16) + ['#'] * 10
        lines.append(''.join(main_plat))
        
        mid_coin = ['.'] * WIDTH
        mid_plat = ['.'] * WIDTH
        mid_plat[14:35] = ['#'] * 21
        lines.append(''.join(mid_coin))
        lines.append(''.join(mid_plat))
    
    # Row 10: Extra coins
    row10 = ['.'] * WIDTH
    if num_coins > 8:
        row10[random.randint(20, 45)] = 'C'
    lines.append(''.join(row10))
    
    # Row 11: Spikes and platforms
    spike_row = ['.'] * WIDTH
    for i in range(num_spikes):
        spike_pos = 10 + i * 8 + random.randint(0, 4)
        if spike_pos < WIDTH - 5:
            spike_row[spike_pos] = '^'
    
    # Platform around spikes
    platform_start = 8 + (level_num % 12)
    platform_len = 10 + (level_num % 8)
    if platform_start + platform_len < WIDTH - 8:
        for i in range(platform_start, min(platform_start + platform_len, WIDTH - 8)):
            if spike_row[i] != '^':
                spike_row[i] = '#'
    
    lines.append(''.join(spike_row))
    
    # Row 12: Final coins and finish
    final_row = ['.'] * WIDTH
    if num_coins > 10:
        final_row[WIDTH - 12] = 'C'
    final_row[WIDTH - 1] = 'F'
    lines.append(''.join(final_row))
    
    # Row 13: Bottom platform with gap at end
    bottom = ['#'] * WIDTH
    bottom[WIDTH - 8:WIDTH - 1] = ['.'] * 7
    bottom[WIDTH - 1] = '#'
    lines.append(''.join(bottom))
    
    return '\n'.join(lines)

# Generate all levels
levels = {
    3: create_level_3(),
    4: create_level_4(),
    5: create_level_5(),
    6: create_level_6(),
    7: create_level_7(),
    8: create_level_8(),
    9: create_level_9(),
    10: create_level_10(),
}

# Add generated levels 11-500
for i in range(11, 501):
    levels[i] = generate_advanced_level(i)

# Write all level files
for level_num, level_data in levels.items():
    filename = f'levels/level{level_num}.txt'
    with open(filename, 'w') as f:
        f.write(level_data)
    print(f"Created {filename}")

print(f"\nSuccessfully created {len(levels)} level files (level3.txt to level500.txt)")
print("All files saved in 'levels/' directory")
print("\nLevel layouts cycle through 8 different patterns:")
print("0: Staircase ascending")
print("1: Gap jumping")
print("2: Vertical challenges")
print("3: Long platform with obstacles")
print("4: Zigzag pattern")
print("5: Dense coins with tight platforms")
print("6: Wave pattern")
print("7: Mixed challenges")
