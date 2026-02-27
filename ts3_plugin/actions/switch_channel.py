import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gtk

from ts3_plugin.actions.base import TeamSpeakActionBase
from ts3_plugin.clientquery import ClientQueryError, escape_query_value


class SwitchChannelAction(TeamSpeakActionBase):
    def get_config_rows(self):
        rows = super().get_config_rows()
        settings = self.get_settings() or {}

        target_entry = Gtk.Entry()
        target_entry.set_placeholder_text("Channel ID or exact channel name")
        target_entry.set_text(settings.get("target_channel", ""))
        target_entry.connect(
            "changed",
            lambda entry: self._store_setting("target_channel", entry.get_text().strip()),
        )
        target_row = Adw.ActionRow(title="Target Channel")
        target_row.add_suffix(target_entry)
        target_row.set_activatable_widget(target_entry)
        rows.append(target_row)

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

    def _extract_cid(self, row: dict) -> str:
        for key in ("cid", "channel_id"):
            value = row.get(key, "")
            if value:
                return str(value)
        # Fallback for unexpected response shapes: first numeric value wins.
        for value in row.values():
            text = str(value)
            if text.isdigit():
                return text
        return ""

    def _resolve_channel_id(self, cq, target: str) -> str:
        if target.isdigit():
            return target

        rows = cq.exec("channellist")
        if not rows:
            raise ClientQueryError(f"Channel not found: {target}")

        target_cf = target.casefold()
        for row in rows:
            channel_name = row.get("channel_name", "")
            if channel_name.casefold() == target_cf:
                cid = self._extract_cid(row)
                if cid:
                    return cid

        for row in rows:
            channel_name = row.get("channel_name", "")
            if target_cf in channel_name.casefold():
                cid = self._extract_cid(row)
                if cid:
                    return cid

        raise ClientQueryError(f"Channel not found: {target}")

    def on_key_down(self):
        settings = self.get_settings() or {}
        target = settings.get("target_channel", "").strip()
        channel_password = settings.get("channel_password", "").strip()
        if not target:
            self.show_error()
            self.set_bottom_label("Missing target")
            return

        def _run(cq):
            cid = self._resolve_channel_id(cq, target)
            whoami_row = cq.exec("whoami")[0]
            current_cid = str(whoami_row.get("cid", ""))
            if current_cid == str(cid):
                self.set_bottom_label("Already in channel")
                return

            clid = str(whoami_row.get("clid", "")) or cq.get_own_client_id()
            move_cmd = f"clientmove clid={clid} cid={cid}"
            if channel_password:
                move_cmd += f" cpw={escape_query_value(channel_password)}"
            cq.exec(move_cmd)
            self.set_bottom_label(f"Moved to {target}")

        self.with_clientquery(_run)
