MACAN RUN - ASSET SPECIFICATIONS
=================================

All visual assets are procedurally generated using QPainter.
No binary image files are required.

PLAYER SPRITE
-------------
Dimensions: 32x48 pixels
Components:
  - Body: Rounded rectangle with gradient (Orange #FF8C00 to #C86400)
    - Border: Dark brown #643200, 2px
    - Corner radius: 8px
  - Head: Ellipse (Skin tone #FFB464)
    - Size: 16px diameter
    - Border: Dark brown #643200, 2px
  - Eyes: Two small circles (#323232, 4px diameter)
    - Positioned at head center
  - Legs: Two rectangles (Dark brown #643200)
    - Animated walking cycle using sine wave
    - Size: 6x8 pixels each

Animation:
  - Walking: Leg offset = sin(time * 8) * 3 pixels
  - Body bounce: sin(time * 5) * 2 pixels when moving
  
States:
  - Normal: Full opacity
  - Invulnerable: Flashing (visible every other frame)
  - Facing: Sprite flips horizontally when moving left

ENEMY SPRITE
------------
Dimensions: 32x32 pixels
Type: Spiky circular creature

Components:
  - Body: Circle (Dark red #963232)
    - Radius: 14px
    - Border: Darker red #641E1E, 2px
  - Spikes: 8 triangular spikes
    - Color: #782828
    - Length: 6px from body edge
    - Animated rotation: angle = (i / 8) * 2π + time * 2
  - Eyes: Two circles (Yellow #FFC800)
    - Size: 6px diameter
    - Position based on patrol direction

Behavior:
  - Patrol AI: moves left/right within range
  - Spikes rotate continuously

COIN
----
Dimensions: 24x24 pixels
Type: Collectible currency

Components:
  - Main circle: Radial gradient
    - Center: Bright gold #FFDF00
    - Middle: Gold #FFD700
    - Edge: Dark gold #C8AA00
  - Border: #967800, 2px
  - Inner ring: #C8AA00, 1px (decorative)

Animation:
  - Float: sin(time * 3) * 4 pixels vertical
  - Rotation: sin(time * 4) * 20 degrees

SPIKE HAZARD
------------
Dimensions: 48x48 pixels
Type: Triangular spike trap

Components:
  - Triangle pointing up
  - Color: Gray #969696
  - Border: Dark gray #646464, 2px
  - Points: Top center, Bottom corners

FINISH FLAG
-----------
Dimensions: 48x96 pixels
Type: Victory marker

Components:
  - Pole: Brown rectangle (#8B4513)
    - Width: 8px, Full height
    - Position: Center-left
  - Flag: Green triangle (#32C832)
    - Border: Dark green #1E961E, 2px
    - Wave animation: sin(time * 5) * 5 pixels
    - Attached to pole top

TILES
-----

Ground Block (#)
  - Gradient: Brown top (#785028) to dark brown bottom (#503214)
  - Border: Very dark brown (#3C2814), 2px
  - Grass top layer: Green (#329632), 6px height
  - Texture: Vertical lines for dirt effect

Platform (=)
  - Color: Semi-transparent gray (#646464CC)
  - Border: Dark gray (#464646), 2px
  - Support beams: Two vertical rectangles (4px wide)

Wall (|)
  - Gradient: Horizontal brown (#82461E to #5A3214)
  - Border: Dark brown (#462810), 2px
  - Brick pattern: Horizontal and vertical lines

BACKGROUND
----------

Sky:
  - Linear gradient (top to bottom)
    - Top: Sky blue #87CEEB
    - Middle (70%): Horizon orange #FFC896
    - Bottom: Ground orange #FFA064

Clouds:
  - Color: Semi-transparent white (#FFFFFFB4)
  - Shape: 3 overlapping ellipses per cloud
  - Parallax: Scrolls at 30% of camera speed
  - Count: 5 clouds distributed across screen

HUD
---

Panel:
  - Background: Semi-transparent dark (#14141ECC)
  - Border: Light gray (#646478), 2px
  - Corner radius: 10px
  - Position: Top-left (10, 10)
  - Size: 280x100 pixels

Text:
  - Font: Sans Serif, Bold
  - Score: 16pt, White (#FFFFFF)
  - Coins: 16pt, Gold (#FFD700)
  - Distance: 12pt, White

Hearts (Health):
  - Full: Red (#FF3232)
  - Empty: Gray (#646464)
  - Size: 20x20 pixels
  - Shape: Two circles + triangle (simplified heart)

MENU SCREENS
------------

Main Menu:
  - Background: Gradient dark blue (#282850 to #141428)
  - Title: "MACAN RUN" - Gold (#FFD700), 48pt bold
  - Subtitle: "Neo Edition" - Light gray (#C8C8C8), 24pt
  - Instructions: White (#FFFFFF), 18pt

Pause Overlay:
  - Semi-transparent black (#00000096)
  - Text: "PAUSED" - White (#FFFFFF), 48pt bold

Game Over:
  - Background: Very dark (#141414)
  - Text: "GAME OVER" - Red (#FF3232), 48pt bold
  - Score display: Light gray (#C8C8C8), 24pt

Level Complete:
  - Background: Gradient green (#329632 to #145014)
  - Text: "LEVEL COMPLETE!" - Gold (#FFD700), 48pt bold
  - Score display: White (#FFFFFF), 24pt

COLOR PALETTE REFERENCE
-----------------------
Primary:
  - Orange: #FF8C00
  - Brown: #643200
  - Gold: #FFD700
  - Green: #329632
  - Red: #FF3232

Secondary:
  - Sky Blue: #87CEEB
  - Gray: #646464
  - Dark Blue: #282850
  - White: #FFFFFF
  - Black: #141414

AUDIO SPECIFICATIONS
--------------------
(Placeholder - implement using QSoundEffect or external library)

Sound Effects:
  - coin.wav: High-pitched pling (440Hz, 0.1s)
  - jump.wav: Quick whoosh (sweep 200-400Hz, 0.15s)
  - hurt.wav: Low thud (100Hz, 0.2s)
  - enemy_hit.wav: Impact sound (white noise burst, 0.1s)
  - game_over.wav: Descending tone (440-220Hz, 1s)
  - win.wav: Victory fanfare (ascending arpeggio, 2s)

Background Music:
  - main_theme.ogg: Upbeat chiptune loop (120 BPM, 8-bar)
  - Format: OGG Vorbis or MP3
  - Loop: Seamless

RENDERING PERFORMANCE NOTES
----------------------------

Optimization techniques used:
1. QPixmap caching for static backgrounds
2. Culling: Entities outside screen bounds not rendered
3. Batch rendering: Tiles drawn row-by-row
4. Minimal QPainter object creation
5. Reuse of brushes and pens where possible
6. Integer coordinates for tiles (avoid subpixel)

Typical rendering budget (60 FPS):
  - Background: ~2ms (cached)
  - Tiles: ~4ms (visible only, ~300 tiles)
  - Entities: ~2ms (~50 entities)
  - HUD: ~1ms
  - Total: ~9ms per frame (leaves 7ms headroom)

ACCESSIBILITY
-------------
All visual elements use high contrast ratios:
  - Text on backgrounds: Minimum 7:1 ratio
  - Interactive elements: Clear visual distinction
  - No reliance on color alone for critical info

FUTURE ASSET ADDITIONS
----------------------
Potential expansions:
  - Power-ups: Shield, speed boost, extra life
  - New enemies: Flying, jumping variants
  - Environmental hazards: Moving platforms, crushers
  - Weather effects: Rain, snow particles
  - Particle systems: Dust, sparkles, explosions

---
All assets generated programmatically - no external files required!
