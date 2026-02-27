from ts3_plugin.actions.base import TeamSpeakActionBase


class ToggleInputMuteAction(TeamSpeakActionBase):
    def on_key_down(self):
        def _run(cq):
            clid = cq.get_own_client_id()
            row = cq.exec(f"clientvariable clid={clid} client_input_muted")[0]
            current = int(row.get("client_input_muted", "0"))
            target = 0 if current else 1
            cq.exec(f"clientupdate client_input_muted={target}")
            self.set_bottom_label("Mic muted" if target else "Mic unmuted")

        self.with_clientquery(_run)
