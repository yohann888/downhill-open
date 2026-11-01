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

## Customize

Start with the knobs and recipes below. For asset generation, hosting, and provider setup, see the tool sections in [README.md](README.md).

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

## Make it deeper

- **Daily seeded course:** Pass a calendar-derived seed into `createTerrain(seed)` and `createObstacles(terrain, seed)` in `src/world`, then regenerate pickups from the same terrain. Add the date or seed to the board key in `tools/api/modal_api.py` so each daily course has its own leaderboard.
- **Trick system:** Extend the air state and landing logic in `src/main.js`, with bike orientation from `src/physics/bike.js`, to count spins and flips. Award time for completed tricks and scale it by landing angle, then update `validate_run()` in `tools/api/board.py` for the new timing rules.
- **Career and unlocks:** Use `RIDER_OPTIONS` and preference storage in `src/rider-preference.js`, plus the menu wiring in `src/main.js`, to unlock riders and bikes after events. Add bike handling presets in `src/physics/constants.js` and save the unlocked IDs with career progress.
- **Friend ghost races:** The game records and samples ghosts through `createRecorder()` and `sampleGhost()` in `src/ghost.js`, and submits runs through `src/api.js`. Add a compact share link or ghost endpoint, then load the shared ghost for head-to-head checkpoint splits in `src/main.js`.
- **Desert and snow biomes:** Extend `createTerrain()` in `src/world/terrain.js` and material setup in `src/render/world.js` with biome-specific textures from `public/assets/textures/`. Tune `MU_TRAIL` and `MU_OFF` in `src/physics/constants.js` so each surface has its own grip.
- **Weather that changes grip:** Rain visuals already flow through `world.setRain()` from `src/main.js`; pass the weather state into `stepBike()` in `src/physics/bike.js` and adjust surface grip in `src/physics/constants.js`. Keep the visual and physics states tied to the same weather selection.
- **More courses or trail branches:** Add course definitions around `createTerrain()`, `createObstacles()`, and `createPickups()` in `src/world`, then let the selected terrain's checkpoints drive splits in `src/main.js`. Give each course or branch its own API board key so runs and ghosts are compared on the same route.
- **Time-attack medals:** Use finish handling and `medalBadge()` in `src/main.js` to award bronze, silver, and gold against fixed course time targets. Keep target medals separate from leaderboard rank, and validate any new run fields in `tools/api/board.py`.

Any change to run time, penalties, bonuses, or ghost duration must stay in sync with the server plausibility checks in `validate_run()` in `tools/api/board.py`. Otherwise the leaderboard can reject a run when its recorded ghost duration no longer matches the accepted time.

## Swap the art

Replace GLBs in `public/assets/models/` with files under the same names, or add entries to `tools/assets/manifest.json` and generate them through Modal. Replace audio files in `public/assets/audio/` under the same names, or update `MUSIC_TRACKS` in `src/audio.js` when changing music choices. The otter obstacle can be rebranded in `src/world/obstacles.js`, `src/render/otter.js`, and the commentary prompt in `tools/api/modal_api.py`; the Built with Devin badges are in `index.html` and `site/index.html`.

## Security

Never put provider keys in `VITE_` variables. If hosting the API, keep server-side run validation in `tools/api/board.py` and the daily TTS cap in `tools/api/modal_api.py`.
