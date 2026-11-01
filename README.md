# Downhill

Downhill is a 3D downhill biking game for the browser. Ride a procedural mountain course, avoid obstacles, collect boosts, and race for a place on the leaderboard.

Play it at [devkick.com/downhill](https://devkick.com/downhill/).

## Run locally

```sh
npm install && npm run dev
```

Run the tests and production build with:

```sh
npm test
npm run build
```

The shared leaderboard and commentary are optional. Copy `.env.example` to `.env.local` and set `VITE_API_BASE` to your Modal app URL to use your own backend.

## How the game was built

### Devin

Downhill's code was built in Devin sessions from plain-language feature requests and bug reports, often with screenshots. Each change went through a PR. Devin Review caught bugs before merge, and a Devin security scan reviewed this repo before release. A fork can use the same workflow for features, bug reports, and review. See [Devin docs](https://docs.devin.ai).

Example prompts for Devin:

- "Add a new obstacle type: a fallen boulder that you must steer around, with a crash message."
- "Add a daily seeded course."
- "Make night mode foggier."
- "Add a trick system that rewards clean spins and flips."

### Meshy

`tools/assets/manifest.json` describes models by text prompt or reference image. `tools/assets/modal_app.py` reads the manifest and runs Meshy text-to-3D, image-to-3D, and optional rigging jobs on Modal. Add a `"rig": true` field to rig a character. For image-to-3D, add an `"image": "ref/your-reference.png"` field and put a supported image in `tools/assets/ref/`.

Example text-to-3D manifest entry:

```json
{ "name": "boulder", "prompt": "large weathered granite boulder with patches of lichen", "polycount": 2000 }
```

After configuring the Modal secret described below, generate one model and fetch optimized GLBs into `public/assets/models/`:

```sh
modal run tools/assets/modal_app.py --kind models --only boulder
MODELS_ONLY=1 tools/assets/fetch.sh
```

Forks can add or edit manifest entries, then use the same Modal job and fetch script for new game assets. See [asset setup](tools/assets/README.md).

### ElevenLabs

The asset manifest defines generated sound effects, music loops, and voice lines. `tools/assets/modal_app.py` runs the generation jobs, and `tools/assets/fetch.sh` copies their output into `public/assets/audio/`. The game API also uses ElevenLabs text-to-speech for optional otter commentary audio in `tools/api/modal_api.py`; commentary text is still available without voice audio.

Generate the audio asset groups with:

```sh
modal run tools/assets/modal_app.py --kind sfx
modal run tools/assets/modal_app.py --kind music
modal run tools/assets/modal_app.py --kind voice
tools/assets/fetch.sh
```

A fork can change the prompts and voice settings in `tools/assets/manifest.json`, or replace local audio files while keeping their names.

### Rosebud AI

Rosebud generated the sky texture and the first rider and bike models (`rider-body` and `bike-frame` in the manifest are marked `Rosebud rosie-3d`). Devin called Rosebud's developer asset API after a one-time login, following Rosebud's [asset instructions](https://rosebud.ai/developer-assets/AGENTS.md). Early builds were also published to rosebud.ai/play with the Rosebud CLI:

```sh
npm install -g @rosebudai/cli
npm run build
rosebud publish --directory ./dist --title "My Downhill" --description "A downhill bike game"
rosebud update --directory ./dist
```

The game is now hosted on Cloudflare Pages instead. Rosebud is optional for forks.

### Modal

Modal runs the Meshy and ElevenLabs asset jobs and hosts the shared leaderboard and commentary API in `tools/api/modal_api.py`. Asset jobs use the `downhill-assets` secret and volume. The API uses the `downhill-api` secret. Set these environment variables in the shell before creating the secrets:

```sh
modal secret create downhill-assets MESHY_API_KEY="$MESHY_API_KEY" ELEVENLABS_API_KEY="$ELEVENLABS_API_KEY" --force
modal volume create downhill-assets
modal secret create downhill-api GEMINI_API_KEY="$GEMINI_API_KEY" ELEVENLABS_API_KEY="$ELEVENLABS_API_KEY" ELEVENLABS_VOICE_ID="$ELEVENLABS_VOICE_ID" --force
modal deploy tools/api/modal_api.py
```

Set `VITE_API_BASE` to the deployed API URL when building the site. `GEMINI_API_KEY` enables commentary text; `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` enable commentary audio. The API returns text without audio if the voice key or ID is unset; per-client and daily caps on commentary and runs live in `tools/api/board.py`.

```sh
VITE_API_BASE="https://<your-modal-app>.modal.run" npm run build:site
```

### Cloudflare Pages

Build the wrapper site and game, then deploy the generated `site-dist/` directory:

```sh
npm run build:site
npx wrangler pages deploy site-dist --project-name <your-project>
```

Set `VITE_API_BASE` before the build when using a hosted API. Any static host can serve the `dist/` output from `npm run build`.

## Customize

See [BUILD-ON-IT.md](BUILD-ON-IT.md) for the code map, tuning points, recipes, and ideas for making a fork deeper.

## Security

Never put provider keys in `VITE_` variables. If hosting the API, keep the server-side run checks and the commentary and text-to-speech limits in `tools/api/board.py`.

## Using MCP servers

This repo uses all of these tools, but through their APIs and CLIs, not through MCP: Meshy and ElevenLabs from Modal scripts, Rosebud through its CLI and asset API, and Modal as the place those scripts and the game API run. MCP servers are an alternative way to drive the same tools from an agent like Devin during development. MCP servers are optional and are not needed at game runtime.

- Meshy publishes `@meshy-ai/meshy-mcp-server`. Its setup uses the `MESHY_API_KEY` environment variable. One documented install command is `npx add-mcp @meshy-ai/meshy-mcp-server --env MESHY_API_KEY=your-key`. See [Meshy API docs](https://docs.meshy.ai/en/api/ai).
- ElevenLabs offers a hosted MCP endpoint at `https://api.elevenlabs.io/v1/mcp`. It uses OAuth and needs no local install. The hosted server is for managing ElevenLabs agents. The older [local audio MCP server](https://github.com/elevenlabs/elevenlabs-mcp-server) is deprecated. See the [hosted MCP docs](https://elevenlabs.io/docs/eleven-agents/operate/hosted-mcp).
- Modal's official docs show how to deploy a custom MCP server on Modal. They do not document a Modal MCP connector for managing the Modal API. See the [Modal MCP example](https://modal.com/docs/examples/mcp_server_stateless).
- Cloudflare offers a remote API MCP server at `https://mcp.cloudflare.com/mcp`. Add that URL to an MCP client and authorize with Cloudflare OAuth. See the [Cloudflare MCP catalog](https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/) and [remote MCP guide](https://developers.cloudflare.com/agents/model-context-protocol/guides/remote-mcp-server/).
- Rosebud has no documented MCP server as of this writing. See the reviewed [Rosebud developer docs](https://rosebud.ai/developers/agent-publishing/docs) and [asset instructions](https://rosebud.ai/developer-assets/AGENTS.md).

To add a custom server in Devin, an organization admin can open **Customize > MCPs > Add MCP > Add custom MCP**, choose the transport, enter the server details, then save and test it. This requires the **Manage MCP Servers** permission. See [Devin MCP setup](https://docs.devin.ai/work-with-devin/mcp).

## License and assets

The code is licensed under MIT. See [LICENSE](LICENSE).

Generated assets from Meshy, ElevenLabs, and Rosebud are included for use with this game. Check each service's terms before reusing them elsewhere. The Devin name and logo belong to Cognition.
