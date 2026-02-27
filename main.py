#!/usr/bin/env python3
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.PluginBase import PluginBase

from ts3_plugin.actions.previous_channel import PreviousChannelAction
from ts3_plugin.actions.raw_command import RawCommandAction
from ts3_plugin.actions.switch_channel import SwitchChannelAction
from ts3_plugin.actions.toggle_input_mute import ToggleInputMuteAction
from ts3_plugin.actions.toggle_output_mute import ToggleOutputMuteAction

PLUGIN_ID = "com_toix_teamspeak3_clientquery"
PLUGIN_VERSION = "0.1.2"
APP_VERSION = "1.5.0-beta.11"


class TeamSpeakClientQueryPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.lm = self.locale_manager
        self.lm.set_to_os_default()
        self.lm.set_fallback_language("en_US")

        self.first_setup = False

        self.register(
            plugin_name="TeamSpeak 3 ClientQuery",
            github_repo="https://github.com/toix/teamspeak3_StreamController_plugin",
            plugin_version=PLUGIN_VERSION,
            app_version=APP_VERSION,
        )

        actions = [
            ("toggle_input_mute", ToggleInputMuteAction),
            ("toggle_output_mute", ToggleOutputMuteAction),
            ("switch_channel", SwitchChannelAction),
            ("previous_channel", PreviousChannelAction),
            ("raw_command", RawCommandAction),
        ]
        for action_key, action_cls in actions:
            self.add_action_holder(
                ActionHolder(
                    plugin_base=self,
                    action_base=action_cls,
                    action_id=f"{PLUGIN_ID}::{action_key}",
                    action_name=self.lm.get(f"actions.{action_key}"),
                )
            )


TeamSpeakClientQueryPlugin()
