# TeamSpeak 3 ClientQuery Plugin For StreamController (Linux)

This plugin controls a local TeamSpeak 3 client from StreamController using the TeamSpeak ClientQuery plugin.

## Actions

- `Toggle Microphone Mute`
- `Toggle Sound Mute`
- `Switch To Channel`
- `Move To Previous Channel`
- `Send Raw ClientQuery Command`

### Action Notes

- `Switch To Channel`
  - Target accepts channel ID or channel name.
  - If you are already in the target channel, the action exits cleanly.
  - Optional channel password can be configured per action.
- `Move To Previous Channel`
  - First press initializes history for this action key.
  - Next press moves back to the previous channel.
  - Repeated presses toggle between last two channels.
  - Optional channel password can be configured per action.
- `Send Raw ClientQuery Command`
  - Sends exactly the configured command string.

## Requirements

- Linux
- StreamController (`>= 1.5.0-beta`)
- TeamSpeak 3 client with ClientQuery plugin enabled
- A ClientQuery API key from TeamSpeak

## Manual Install Tutorial (Testing)

Use this when you want to test the plugin without packaging it.

1. Close StreamController completely.
2. Find your local StreamController plugins directory.
   - Typical Flatpak path on Linux: `~/.var/app/com.core447.StreamController/data/plugins/`
   - If your installation differs, open StreamController once and check its settings/data path, then close it again.
3. Copy this project folder into the plugins directory.
   - The final folder should look like:
     - `<plugins-dir>/com_toix_teamspeak3_clientquery/manifest.json`
     - `<plugins-dir>/com_toix_teamspeak3_clientquery/main.py`
4. Confirm TeamSpeak 3 ClientQuery is enabled and you have an API key.
5. Start StreamController.
6. Add one of these actions to a key:
   - `Toggle Microphone Mute`
   - `Toggle Sound Mute`
   - `Switch To Channel`
   - `Move To Previous Channel`
   - `Send Raw ClientQuery Command`
7. Configure action settings:
   - `Host`: `127.0.0.1`
   - `Port`: `25639`
   - `API Key`: your TeamSpeak ClientQuery API key
8. Press the key and verify TeamSpeak reacts.

### Manual Install With Script (Recommended)

From this repository, run:

```sh
chmod +x scripts/install_local.sh
./scripts/install_local.sh
```

Then fully restart StreamController.

### Verify Installed Files

Run:

```sh
find ~/.var/app/com.core447.StreamController/data/plugins/com_toix_teamspeak3_clientquery -maxdepth 2 -type f | sort
```

You must see at least:

- `manifest.json`
- `main.py`
- `ts3_plugin/locales/en_US.json`

### Quick Troubleshooting

- Plugin does not appear:
  - Re-check folder layout (must contain `manifest.json` directly in the plugin root).
  - Restart StreamController after copying files.
- Key press shows connection error:
  - Verify TeamSpeak is running.
  - Verify ClientQuery plugin is enabled.
  - Verify `Host`, `Port`, and API key are correct.
- After code changes:
  - Restart StreamController to reload plugin files.

## Notes

- The plugin opens a connection to TeamSpeak only when an action is pressed.
- `Raw ClientQuery Command` sends exactly the command you configure.
- Plugin entrypoint and registration now follow the official `StreamController/PluginTemplate` pattern (`main.py` owns plugin class and action registration).

## Publish Checklist

Reference: https://streamcontroller.github.io/docs/latest/plugin_dev/getting_started/

1. Verify metadata in `manifest.json` (`id`, `version`, `minimum-app-version`, `github`, `thumbnail`).
2. Verify plugin registration metadata in `main.py` (`plugin_name`, `github_repo`, `plugin_version`, `app_version`).
3. Verify locale exists at `ts3_plugin/locales/en_US.json`.
4. Verify assets and attribution files exist (`assets/thumbnail.svg`, `attribution.json`).
5. Run local install and smoke test:
   - `./scripts/install_local.sh`
   - restart StreamController
   - test each action at least once
