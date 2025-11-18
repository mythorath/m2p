# Animation Assets

This directory contains sprite sheets and animation assets for the game.

## Miner Sprite Sheet

### miner-sprites.png

**Format**: PNG with transparency
**Size**: 384x192 pixels (64x64 per frame, 6 frames wide, 3 rows)
**Style**: 8-bit/pixel art

**Layout**:
```
Row 0 (Idle):     [Frame 0] [Frame 1] [Frame 2] [Frame 3] [---] [---]
Row 1 (Mining):   [Frame 0] [Frame 1] [Frame 2] [Frame 3] [Frame 4] [Frame 5]
Row 2 (Celebrate):[Frame 0] [Frame 1] [Frame 2] [Frame 3] [Frame 4] [Frame 5] [Frame 6] [Frame 7]
```

### Creating the Sprite Sheet

If you don't have a sprite sheet yet, you can:

1. **Use a pixel art tool** like:
   - Aseprite
   - Piskel (free, browser-based)
   - GIMP

2. **Download free sprites** from:
   - [OpenGameArt.org](https://opengameart.org/)
   - [itch.io](https://itch.io/game-assets/free/tag-sprites)
   - [Kenney.nl](https://kenney.nl/assets)

3. **Commission an artist** on:
   - Fiverr
   - DeviantArt
   - ArtStation

### Animation States

#### Idle (4 frames)
- Breathing animation
- Slight up/down movement
- Frame duration: 500ms

#### Mining (6 frames)
- Pickaxe swing motion
- Impact frame
- Recovery
- Frame duration: 150ms

#### Celebrating (8 frames)
- Jump/victory pose
- Arm movements
- Happy expression
- Frame duration: 200ms

## Alternative: CSS-Only Animations

If you don't have a sprite sheet, the `MinerSprite` component includes CSS-only fallback animations. To use them:

```javascript
<MinerSprite state="mining" size={64} useSpriteSheet={false} />
```

The CSS animations will create a simple miner character using colored shapes.

## Adding Your Sprite Sheet

1. Create or download a sprite sheet following the format above
2. Save it as `miner-sprites.png` in this directory
3. Set `useSpriteSheet={true}` in the `MinerSprite` component
4. Adjust frame counts in `MinerSprite.js` if your sprite sheet has different dimensions

## Performance Notes

- Keep sprite sheets as small as possible
- Use PNG-8 for simple pixel art (smaller file size)
- Consider using `image-rendering: pixelated` for crisp pixel art scaling
- Optimize PNGs with tools like TinyPNG or ImageOptim
