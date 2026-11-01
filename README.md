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

## How it was built

- Devin sessions drove all code for this project.
- Meshy generated 3D assets from images and text. Rigging jobs run through `tools/assets/modal_app.py` on Modal.
- ElevenLabs generated sound effects, music, and voice.
- Rosebud created the sky.
- `tools/api` runs the leaderboard and otter commentary API on Modal.
- Cloudflare Pages hosts the game.

## Backend keys

The game API reads a Modal secret named `downhill-api`. Set `GEMINI_API_KEY` for text commentary. Set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` for commentary audio. If the voice ID or ElevenLabs key is missing, commentary text still works without audio.

The asset generation tools use a Modal secret named `downhill-assets` with `MESHY_API_KEY` and `ELEVENLABS_API_KEY`. Setup notes are in `tools/assets/README.md`.

Do not put provider keys in client-side Vite variables. Keep them in Modal secrets.

## Using MCP servers

MCP servers are optional tools for development. The game does not need them at runtime.

- Meshy publishes `@meshy-ai/meshy-mcp-server`. Its setup uses the `MESHY_API_KEY` environment variable. One documented install command is `npx add-mcp @meshy-ai/meshy-mcp-server --env MESHY_API_KEY=your-key`.
- ElevenLabs offers a hosted MCP endpoint at `https://api.elevenlabs.io/v1/mcp`. It uses OAuth and needs no local install. The hosted server is for managing ElevenLabs agents. The older local audio MCP server is deprecated.
- Modal's official docs show how to deploy a custom MCP server on Modal. They do not document a Modal MCP connector for managing the Modal API.
- Cloudflare offers a remote API MCP server at `https://mcp.cloudflare.com/mcp`. Add that URL to an MCP client and authorize with Cloudflare OAuth.
- I did not find official Rosebud MCP setup instructions in the reviewed documentation.

To add a custom server in Devin, an organization admin can open **Customize > MCPs > Add MCP > Add custom MCP**, choose the transport, enter the server details, then save and test it. This requires the **Manage MCP Servers** permission.

## License and assets

The code is licensed under MIT. See [LICENSE](LICENSE).

Generated assets from Meshy, ElevenLabs, and Rosebud are included for use with this game. Check each service's terms before reusing them elsewhere. The Devin name and logo belong to Cognition.
