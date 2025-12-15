"""
Create ALL level files (level1.txt through level500.txt)
ENHANCED: Much more coins, mixed enemies, more power-ups!
- More coins everywhere (2-3x increase)
- Better enemy variety and mixing
- More strategic power-up placement
- Exciting long levels from level 3+
"""
import os
import random

# Create levels directory
os.makedirs('levels', exist_ok=True)

# ============================================
# LEVEL 1 - Tutorial (Simple)
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
# LEVEL 2 - Basic Learning
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
print("✅ Created levels/level1.txt")

with open('levels/level2.txt', 'w') as f:
    f.write(level2.strip())
print("✅ Created levels/level2.txt")

# Advanced generator for levels 3-500
WIDTH = 280
HEIGHT = 13
SECTION_WIDTH = 70

def create_level_3():
    """Enhanced tutorial level - MORE COINS, MORE ENEMIES, MORE FUN!"""
    return """.....C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C...
.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.....###...###...###.
........S.......C.......C.......H.......C.......C.......U.......C.......C.......D.......C.......C...........C.......C...........C.......C...........C.......C...........C.......C...........C.......C...........C.......C...........C.......C...........C.......C...........C.......C.......
...C...###...C...###...###...C...###...###...C...###...###...C...###...###...C...###...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###...C...###
.###.......E.###.......###.E.###.......###.......###.F.....J.......###.......###.......###.E.....K.......###.......###.......###.E.....F.......###.......###.......###.E.....J.......###.......###.......###.F.....K.......###.......###.......###.E.....F.......###.......###.......###...
P.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C.....C...
###########.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.####
........C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C...
....#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.###.###.#########.###.##
.....C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C.......C.....C.....C...
...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^...........^.......^.......
########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.#######.#########.######
..............C...........F...............C.......B...............C...........F...............C...........T...............C...........F...............C...........B...............C...........F...............C...........T...............C...........F...............C.............................CG
##########################################################################.#######################################################################.#######################################################################.#######################################################################.#######"""

def get_enemy_types_for_level(level_num):
    """Return available enemy types based on level number."""
    types = ['E', 'F']  # Basic enemies always available
    
    if level_num >= 51:
        types.append('J')  # Jumpers
    if level_num >= 151:
        types.append('K')  # Chargers
    if level_num >= 301:
        types.append('B')  # Bombers
    if level_num >= 451:
        types.append('T')  # Spinners
        
    return types

def generate_coin_line(section_width, density='high'):
    """Generate a line of coins with specified density."""
    coins = ['.'] * section_width
    
    if density == 'high':
        # Every 3-5 spaces
        for i in range(0, section_width, random.randint(3, 5)):
            if i < section_width:
                coins[i] = 'C'
    elif density == 'medium':
        # Every 5-8 spaces
        for i in range(0, section_width, random.randint(5, 8)):
            if i < section_width:
                coins[i] = 'C'
    elif density == 'low':
        # Every 10-15 spaces
        for i in range(0, section_width, random.randint(10, 15)):
            if i < section_width:
                coins[i] = 'C'
    
    return coins

def place_mixed_enemies(line, section_width, num_enemies, available_types):
    """Place varied enemies across the line."""
    enemy_positions = []
    
    # Calculate spacing
    if num_enemies > 0:
        spacing = section_width // (num_enemies + 1)
        
        for i in range(num_enemies):
            pos = (i + 1) * spacing + random.randint(-5, 5)
            if 5 < pos < section_width - 5:
                enemy_positions.append(pos)
    
    # Place enemies with variety
    for i, pos in enumerate(enemy_positions):
        if line[pos] == '.':
            # Mix enemy types for variety
            enemy_type = random.choice(available_types)
            line[pos] = enemy_type

def generate_section(section_type, level_num, section_num, num_enemies, num_coins, num_spikes, num_powerups):
    """Generate enhanced section with MORE content!"""
    lines = [['.' for _ in range(SECTION_WIDTH)] for _ in range(HEIGHT)]
    
    random.seed(level_num * 1000 + section_num)
    powerup_types = ['S', 'H', 'U', 'D']
    available_enemies = get_enemy_types_for_level(level_num)
    
    # Row 1: Floating coins (high density!)
    coins_row1 = generate_coin_line(SECTION_WIDTH, 'high')
    for i, c in enumerate(coins_row1):
        if c == 'C' and random.random() > 0.3:  # 70% chance to place
            lines[1][i] = 'C'
    
    # Row 2: Power-ups with platforms (MORE power-ups!)
    if num_powerups > 0:
        powerup_count = min(num_powerups, 3)  # Up to 3 power-ups per section
        for p in range(powerup_count):
            powerup_pos = random.randint(10, SECTION_WIDTH - 15)
            powerup_type = random.choice(powerup_types)
            lines[2][powerup_pos] = powerup_type
            # Platform under power-up
            for j in range(powerup_pos - 3, min(powerup_pos + 4, SECTION_WIDTH)):
                lines[3][j] = '#'
    
    # Row 3: Coin trail
    coins_row3 = generate_coin_line(SECTION_WIDTH, 'medium')
    for i, c in enumerate(coins_row3):
        if c == 'C' and lines[3][i] == '.' and random.random() > 0.4:
            lines[3][i] = 'C'
    
    # Row 4: Platforms with coins
    platform_starts = [10, 30, 50]
    for start in platform_starts:
        if start + 10 < SECTION_WIDTH:
            # Coins on platform
            for i in range(start, min(start + 10, SECTION_WIDTH)):
                if random.random() > 0.5:
                    lines[3][i] = 'C'
                lines[4][i] = '#'
    
    # Row 5: ENEMIES! (Mixed types for variety)
    if section_num == 0:
        lines[5][0] = 'P'  # Player spawn
    
    place_mixed_enemies(lines[5], SECTION_WIDTH, num_enemies, available_enemies)
    
    # Add extra flying enemies
    if 'F' in available_enemies and random.random() > 0.4:
        fly_pos = random.randint(20, SECTION_WIDTH - 20)
        if lines[5][fly_pos] == '.':
            lines[5][fly_pos] = 'F'
    
    # Row 6: Main ground platform
    for i in range(SECTION_WIDTH):
        lines[6][i] = '#'
    
    # Row 7-8: Middle platforms with coins
    if section_type == 0:
        platform_start = 15
        for i in range(platform_start, min(platform_start + 20, SECTION_WIDTH)):
            lines[8][i] = '#'
            # Coins above platform
            if random.random() > 0.4:
                lines[7][i] = 'C'
    elif section_type == 1:
        # Multiple small platforms
        for start in [10, 30, 50]:
            if start + 8 < SECTION_WIDTH:
                for i in range(start, start + 8):
                    lines[8][i] = '#'
                    if random.random() > 0.5:
                        lines[7][i] = 'C'
    else:
        # Long platform with gaps
        for i in range(10, min(60, SECTION_WIDTH)):
            if i % 20 < 15:  # Create gaps
                lines[8][i] = '#'
                if random.random() > 0.6:
                    lines[7][i] = 'C'
    
    # Row 9: More coins!
    coins_row9 = generate_coin_line(SECTION_WIDTH, 'medium')
    for i, c in enumerate(coins_row9):
        if c == 'C' and random.random() > 0.5:
            lines[9][i] = 'C'
    
    # Row 10: Spikes with safe platforms
    spike_count = 0
    for i in range(0, SECTION_WIDTH, 8):
        if spike_count < num_spikes and random.random() > 0.3:
            if i < SECTION_WIDTH - 5:
                lines[10][i] = '^'
                spike_count += 1
        elif random.random() > 0.5:
            # Safe platform
            for j in range(i, min(i + 5, SECTION_WIDTH)):
                lines[10][j] = '#'
    
    # Row 11: Coins before finish
    if section_num == 3:
        # Power-up before finish
        if num_powerups > 2:
            powerup_pos = SECTION_WIDTH - 18
            lines[11][powerup_pos] = random.choice(powerup_types)
        
        # Coin trail to finish
        for i in range(SECTION_WIDTH - 25, SECTION_WIDTH - 5):
            if random.random() > 0.3:
                lines[11][i] = 'C'
        
        # FINISH FLAG
        lines[11][SECTION_WIDTH - 2] = 'G'
    else:
        # Regular coins
        coins_row11 = generate_coin_line(SECTION_WIDTH, 'low')
        for i, c in enumerate(coins_row11):
            if c == 'C':
                lines[11][i] = 'C'
    
    # Row 12: Bottom platform
    for i in range(SECTION_WIDTH):
        lines[12][i] = '#'
    
    if section_num == 3:
        # Open bottom for finish
        for i in range(SECTION_WIDTH - 10, SECTION_WIDTH - 1):
            if lines[12][i] != 'G':
                lines[12][i] = '.'
        lines[12][SECTION_WIDTH - 1] = '#'
        lines[12][SECTION_WIDTH - 2] = '#'
    
    return lines

def generate_advanced_level(level_num):
    """Generate exciting level with LOTS of content!"""
    difficulty = min((level_num - 10) / 490.0, 1.0)
    
    # MORE of everything!
    num_enemies = min(2 + (level_num // 10), 12)  # More enemies!
    num_coins = min(10 + (level_num // 5), 40)    # MANY more coins!
    num_spikes = min((level_num // 20), 12)       # More spikes
    num_powerups = min(1 + (level_num // 15), 6)  # More power-ups!
    
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

# Generate level 3 (ENHANCED!)
with open('levels/level3.txt', 'w') as f:
    f.write(create_level_3())
print("✅ Created levels/level3.txt (ENHANCED with MORE content!)")

# Generate levels 4-500
print("\n" + "="*60)
print("🎮 Generating exciting levels 4-500...")
print("   More coins! More enemies! More fun!")
print("="*60)

milestones = [
    (50, "🎯 Basic Enemies (E, F) + LOTS of coins!"),
    (150, "🦘 Added Jumpers (J) + Even MORE coins!"),
    (300, "🐂 Added Chargers (K) + Power-up bonanza!"),
    (450, "💣 Added Bombers (B) + Coin festival!"),
    (500, "⚙️ Added Spinners (T) - ULTIMATE CHALLENGE!")
]

for i in range(4, 501):
    level_data = generate_advanced_level(i)
    filename = f'levels/level{i}.txt'
    with open(filename, 'w') as f:
        f.write(level_data)
    
    # Show progress at milestones
    for milestone, description in milestones:
        if i == milestone:
            print(f"\n{description}")
            print("="*60)
    
    if i <= 10 or i % 50 == 0:
        print(f"✅ Created {filename}")

print(f"\n{'='*60}")
print(f"🎉 Successfully created 500 EXCITING level files!")
print(f"{'='*60}")
print("\n📊 Content Statistics:")
print(f"  💰 Coins per level: 10-40 (2-3x MORE than before!)")
print(f"  👾 Enemies per level: 2-12 (MIXED types for variety!)")
print(f"  🎁 Power-ups per level: 1-6 (Strategic placement!)")
print(f"  ⚠️  Spikes per level: 0-12 (Balanced challenge!)")
print("\n🎨 Level Features:")
print("  ✅ Floating coin trails (high density)")
print("  ✅ Platform coins (collect while jumping)")
print("  ✅ Mixed enemy types (no boring patterns!)")
print("  ✅ Strategic power-up placement")
print("  ✅ Exciting long maps (280 tiles wide!)")
print("\n📖 Marker Reference:")
print("  P = Player spawn")
print("  E = Ground enemy (red spiky)")
print("  F = Flying enemy (blue bird)")
print("  J = Jumper enemy (orange spring)")
print("  K = Charger enemy (purple bull)")
print("  B = Bomber enemy (black bomb)")
print("  T = Spinner enemy (purple blades)")
print("  C = Coin 💰 (LOTS of them!)")
print("  ^ = Spike")
print("  G = FINISH FLAG 🏁")
print("  S = Speed power-up ⚡")
print("  H = Health power-up ❤️")
print("  U = Triple Jump power-up ⬆️")
print("  D = Shield power-up 🛡️")
print(f"{'='*60}")
print("🚀 Levels are now MUCH MORE FUN to play!")
print("   Go collect those coins! 💰💰💰")
print(f"{'='*60}")
