import socket
from dataclasses import dataclass


def _unescape(value: str) -> str:
    return (
        value.replace("\\s", " ")
        .replace("\\p", "|")
        .replace("\\/", "/")
        .replace("\\\\", "\\")
    )


def escape_query_value(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("/", "\\/")
        .replace("|", "\\p")
        .replace(" ", "\\s")
    )


def _parse_values(line: str) -> dict:
    out: dict[str, str] = {}
    for token in line.split():
        if "=" not in token:
            continue
        key, raw = token.split("=", 1)
        out[key] = _unescape(raw)
    return out


@dataclass
class TS3Settings:
    host: str
    port: int
    api_key: str
    timeout: float = 5.0


class ClientQueryError(Exception):
    pass


class ClientQuery:
    def __init__(self, settings: TS3Settings):
        self.settings = settings
        self.sock: socket.socket | None = None
        self._recv_buffer = b""

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def connect(self):
        self.sock = socket.create_connection(
            (self.settings.host, self.settings.port), self.settings.timeout
        )
        self.sock.settimeout(self.settings.timeout)
        self._drain_welcome()
        self.exec(f"auth apikey={escape_query_value(self.settings.api_key)}")
        # Select active TeamSpeak connection context for commands that need it.
        self.exec("use")

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
        self._recv_buffer = b""

    def _readline(self) -> str:
        assert self.sock is not None
        try:
            while b"\n" not in self._recv_buffer:
                chunk = self.sock.recv(4096)
                if not chunk:
                    raise ClientQueryError("ClientQuery connection closed by TeamSpeak.")
                self._recv_buffer += chunk
        except OSError as e:
            raise ClientQueryError("Timed out waiting for TeamSpeak response.") from e

        line, self._recv_buffer = self._recv_buffer.split(b"\n", 1)
        return line.decode("utf-8", errors="replace").strip()

    def _drain_welcome(self):
        if self.sock is None:
            return
        # Read greeting banner lines that are immediately available.
        original_timeout = self.sock.gettimeout()
        self.sock.settimeout(0.2)
        try:
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    return
                self._recv_buffer += chunk
                while b"\n" in self._recv_buffer:
                    line, self._recv_buffer = self._recv_buffer.split(b"\n", 1)
                    decoded = line.decode("utf-8", errors="replace").strip()
                    if decoded.startswith("error "):
                        return
        except OSError:
            return
        finally:
            self.sock.settimeout(original_timeout)

    def exec(self, command: str) -> list[dict]:
        assert self.sock is not None
        self.sock.sendall((command + "\r\n").encode("utf-8"))
        rows: list[dict] = []
        while True:
            line = self._readline()
            if not line:
                continue
            if line.startswith("notify"):
                continue
            if line.startswith("error "):
                error = _parse_values(line)
                if error.get("id", "1") != "0":
                    message = error.get("msg", "Unknown TeamSpeak error")
                    raise ClientQueryError(message)
                return rows

            for row in line.split("|"):
                rows.append(_parse_values(row))

    def get_own_client_id(self) -> str:
        rows = self.exec("whoami")
        if not rows or "clid" not in rows[0]:
            raise ClientQueryError("Could not resolve current TeamSpeak client id.")
        return rows[0]["clid"]
