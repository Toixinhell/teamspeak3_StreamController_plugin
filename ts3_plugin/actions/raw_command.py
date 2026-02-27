import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gtk

from ts3_plugin.actions.base import TeamSpeakActionBase


class RawCommandAction(TeamSpeakActionBase):
    def get_config_rows(self):
        rows = super().get_config_rows()
        settings = self.get_settings() or {}

        command_entry = Gtk.Entry()
        command_entry.set_placeholder_text("Example: clientupdate client_input_muted=1")
        command_entry.set_text(settings.get("command", ""))
        command_entry.connect(
            "changed",
            lambda entry: self._store_setting("command", entry.get_text().strip()),
        )
        command_row = Adw.ActionRow(title="Command")
        command_row.add_suffix(command_entry)
        command_row.set_activatable_widget(command_entry)
        rows.append(command_row)

        return rows

    def on_key_down(self):
        settings = self.get_settings() or {}
        command = settings.get("command", "").strip()
        if not command:
            self.show_error()
            self.set_bottom_label("Missing command")
            return

        def _run(cq):
            cq.exec(command)
            self.set_bottom_label("Command sent")

        self.with_clientquery(_run)
