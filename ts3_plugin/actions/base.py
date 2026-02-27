import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from src.backend.PluginManager.ActionBase import ActionBase
from ts3_plugin.clientquery import ClientQuery, ClientQueryError, TS3Settings


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 25639


class TeamSpeakActionBase(ActionBase):
    def get_ts_settings(self) -> TS3Settings:
        settings = self.get_settings() or {}
        host = settings.get("host", DEFAULT_HOST).strip() or DEFAULT_HOST
        port = int(settings.get("port", DEFAULT_PORT))
        api_key = settings.get("api_key", "").strip()
        if not api_key:
            raise ValueError("Missing TeamSpeak ClientQuery API key in action settings.")
        return TS3Settings(host=host, port=port, api_key=api_key)

    def _store_setting(self, key: str, value):
        settings = self.get_settings() or {}
        settings[key] = value
        self.set_settings(settings)

    def get_config_rows(self):
        settings = self.get_settings() or {}
        rows = []

        host_entry = Gtk.Entry()
        host_entry.set_text(settings.get("host", DEFAULT_HOST))
        host_entry.connect(
            "changed", lambda entry: self._store_setting("host", entry.get_text().strip())
        )
        host_row = Adw.ActionRow(title="Host")
        host_row.add_suffix(host_entry)
        host_row.set_activatable_widget(host_entry)
        rows.append(host_row)

        port_input = Gtk.SpinButton.new_with_range(1, 65535, 1)
        port_input.set_value(float(settings.get("port", DEFAULT_PORT)))
        port_input.connect(
            "value-changed", lambda spin: self._store_setting("port", spin.get_value_as_int())
        )
        port_row = Adw.ActionRow(title="Port")
        port_row.add_suffix(port_input)
        port_row.set_activatable_widget(port_input)
        rows.append(port_row)

        key_entry = Gtk.Entry()
        key_entry.set_visibility(False)
        key_entry.set_placeholder_text("ClientQuery API key")
        key_entry.set_text(settings.get("api_key", ""))
        key_entry.connect(
            "changed",
            lambda entry: self._store_setting("api_key", entry.get_text().strip()),
        )
        key_row = Adw.ActionRow(title="API Key")
        key_row.add_suffix(key_entry)
        key_row.set_activatable_widget(key_entry)
        rows.append(key_row)

        return rows

    def with_clientquery(self, fn):
        try:
            ts_settings = self.get_ts_settings()
            with ClientQuery(ts_settings) as cq:
                return fn(cq)
        except ValueError:
            self.show_error()
            self.set_bottom_label("Config needed")
        except (OSError, ClientQueryError) as e:
            self.show_error()
            self.set_bottom_label(f"TS3 error: {e}")
