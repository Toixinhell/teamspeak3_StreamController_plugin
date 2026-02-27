import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gtk

from ts3_plugin.actions.base import TeamSpeakActionBase
from ts3_plugin.clientquery import ClientQueryError, escape_query_value


class PreviousChannelAction(TeamSpeakActionBase):
    def get_config_rows(self):
        rows = super().get_config_rows()
        settings = self.get_settings() or {}

        password_entry = Gtk.Entry()
        password_entry.set_visibility(False)
        password_entry.set_placeholder_text("Optional channel password")
        password_entry.set_text(settings.get("channel_password", ""))
        password_entry.connect(
            "changed",
            lambda entry: self._store_setting("channel_password", entry.get_text().strip()),
        )
        password_row = Adw.ActionRow(title="Channel Password")
        password_row.add_suffix(password_entry)
        password_row.set_activatable_widget(password_entry)
        rows.append(password_row)

        return rows

    def on_key_down(self):
        settings = self.get_settings() or {}
        password = settings.get("channel_password", "").strip()

        def _run(cq):
            whoami_row = cq.exec("whoami")[0]
            current_cid = str(whoami_row.get("cid", ""))
            if not current_cid:
                raise ClientQueryError("Could not resolve current channel.")

            previous_cid = str(settings.get("previous_cid", "")).strip()
            last_seen_cid = str(settings.get("last_seen_cid", "")).strip()

            if last_seen_cid and last_seen_cid != current_cid:
                previous_cid = last_seen_cid

            if not previous_cid:
                self._store_setting("last_seen_cid", current_cid)
                self.set_bottom_label("No previous channel yet")
                return

            if previous_cid == current_cid:
                self._store_setting("last_seen_cid", current_cid)
                self.set_bottom_label("Already in previous channel")
                return

            clid = cq.get_own_client_id()
            move_cmd = f"clientmove clid={clid} cid={previous_cid}"
            if password:
                move_cmd += f" cpw={escape_query_value(password)}"
            cq.exec(move_cmd)

            self._store_setting("previous_cid", current_cid)
            self._store_setting("last_seen_cid", previous_cid)
            self.set_bottom_label("Moved to previous")

        self.with_clientquery(_run)
