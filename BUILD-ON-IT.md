# Build on Downhill

## Code map

- `src/main.js` starts the game, connects input and menus, creates the world, and runs the game loop.
- `src/physics/constants.js` holds bike and simulation values. `src/physics/bike.js` applies input, movement, collisions, and pickup effects.
- `src/world/terrain.js` builds the course profile and finish. `src/world/obstacles.js` places obstacles. `src/world/pickups.js` lays out boosts.
- `src/render/` builds the Three.js scene, terrain, riders, obstacles, pickups, and effects.
- `src/audio.js` loads and controls sound effects, music, and the selected track.
- `tools/assets/` contains the asset generation and fetch workflow. `tools/api/` contains the leaderboard and commentary service.

## Useful knobs

- Tune bike handling in `src/physics/constants.js`. The constants include mass, rolling resistance, grip, pedal power, steering, braking, and jump values. `stepBike()` in `src/physics/bike.js` uses them.
- Change the course length with `COURSE_LENGTH` in `src/world/terrain.js`.
- Adjust obstacle types, spacing, and seeded placement in `createObstacles()` in `src/world/obstacles.js`.
- Change boost types and course positions in `PICKUP_LAYOUT` in `src/world/pickups.js`. Pickup effects are in `applyPickup()` in `src/physics/bike.js`.
- Add music choices to `MUSIC_TRACKS` near the top of `src/audio.js`. Audio files load from `public/assets/audio/`.
- Rider choices are in `RIDER_OPTIONS` in `src/rider-preference.js`. Portraits and models are loaded by `src/main.js`.

## Recipes

### Add an obstacle

1. Add a type and placement rule in `createObstacles()` in `src/world/obstacles.js`.
2. Add or reuse a model in `public/assets/models/` and include its name in the `modelNames` list in `src/main.js`.
3. Add its world rendering in `buildWorld()` in `src/render/world.js`.
4. Check its collision shape in `obstacleFootprintAt()` in `src/physics/bike.js`. Logs use segment endpoints; other obstacles use their radius or ellipse.

### Add a music track

1. Put the audio file in `public/assets/audio/`.
2. Add its `id` and `label` to `MUSIC_TRACKS` in `src/audio.js`.
3. Start the game and select it in the music menu. The menu is built from the track list.

### Add a power-up

1. Add a type and course fraction to `PICKUP_LAYOUT` in `src/world/pickups.js`.
2. Add its effect to `applyPickup()` in `src/physics/bike.js`.
3. Add a model branch in `buildPickups()` in `src/render/pickups.js`.
4. Update the pickup message and sound in the pickup handling section of `src/main.js`.

### Tune the bike

1. Change the relevant value in `src/physics/constants.js`.
2. Trace its use in `stepBike()` in `src/physics/bike.js`.
3. Run `npm test` and adjust the physics tests if the intended behavior changed.

### Add a rider

1. Add the rider ID and label to `RIDER_OPTIONS` in `src/rider-preference.js`.
2. Add a portrait at `public/assets/rider-<id>.png` and a model at `public/assets/models/rider-<id>.glb`.
3. Add the model name to `modelNames` in `src/main.js`.
4. Check the rider setup and rig behavior in `src/render/rider.js`.

## Ideas to explore

- Daily courses with a fixed random seed
- A trick system with score combos
- Career events and unlocks
- Friend ghost races
- New mountain biomes
- Weather that changes grip
- Multiplayer ghosts
