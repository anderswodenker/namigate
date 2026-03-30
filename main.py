import asyncio
import json
import subprocess
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, DataTable, Input
from textual.containers import Container

CONNECTIONS_FILE = Path.home() / ".config" / "namigate" / "connections.json"


def _is_git_repo() -> bool:
    path = CONNECTIONS_FILE.parent
    while path != path.parent:
        if (path / ".git").exists():
            return True
        path = path.parent
    return False


class SSHConnectionTable(DataTable):
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_column("Alias", key="alias")
        self.add_column("Hostname", key="hostname")
        self.add_column("User", key="user")
        self.add_column("Port", key="port")
        self.add_column("Location", key="location")
        self.add_column("Description", key="description")


class ListSSH(App):
    """An App to List my SSH Connection Options"""

    # Kanagawa color palette
    # Backgrounds: sumiInk0=#16161D, sumiInk3=#1F1F28, sumiInk4=#2A2A37, sumiInk5=#363646, sumiInk6=#54546D
    # Accents: crystalBlue=#7E9CD8, oniViolet=#957FB8, carpYellow=#E6C384, springGreen=#98BB6C
    # Wave: waveBlue1=#223249, waveBlue2=#2D4F67
    # Text: fujiWhite=#DCD7BA, fujiGray=#727169

    CSS = """
    Screen {
        background: #1F1F28;
        color: #DCD7BA;
    }

    Header {
        background: #16161D;
        color: #DCD7BA;
    }

    Header .header--highlight {
        background: #16161D;
        color: #7E9CD8;
    }

    Footer {
        background: #16161D;
        color: #727169;
    }

    Footer .footer--highlight {
        background: #223249;
        color: #DCD7BA;
    }

    Input {
        background: #2A2A37;
        color: #DCD7BA;
        border: tall #54546D;
        margin: 0 1;
        height: 3;
    }

    Input:focus {
        border: tall #7E9CD8;
    }

    DataTable {
        background: #1F1F28;
        color: #DCD7BA;
    }

    DataTable > .datatable--header {
        background: #16161D;
        color: #E6C384;
        text-style: bold;
    }

    DataTable > .datatable--even-row {
        background: #1F1F28;
    }

    DataTable > .datatable--odd-row {
        background: #2A2A37;
    }

    DataTable > .datatable--cursor {
        background: #2D4F67;
        color: #DCD7BA;
    }

    DataTable:focus > .datatable--cursor {
        background: #7E9CD8;
        color: #16161D;
        text-style: bold;
    }

    DataTable > .datatable--hover {
        background: #223249;
        color: #DCD7BA;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("slash", "focus_search", "Search"),
        Binding("c", "copy_command", "Copy cmd"),
        Binding("ctrl+r", "sync", "Sync"),
        Binding("escape", "action_escape", "Clear / Quit", show=False),
        Binding("h", "helping", "Help"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._connections: list[dict] = []
        self._highlighted_row_key = None

    async def on_mount(self) -> None:
        await self._sync_and_reload(notify_up_to_date=False)
        self.query_one(SSHConnectionTable).focus()

    async def _git_pull(self) -> str | None:
        """Run git pull --rebase. Returns stdout on success, None on failure."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "pull", "--rebase",
                cwd=CONNECTIONS_FILE.parent,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                return stdout.decode().strip()
            self.notify(
                f"Git sync failed: {stderr.decode().strip()}",
                severity="warning",
                timeout=6,
            )
            return None
        except FileNotFoundError:
            self.notify("git not found in PATH", severity="error")
            return None

    async def _sync_and_reload(self, notify_up_to_date: bool = True) -> None:
        if not _is_git_repo():
            self.load_connections()
            return

        output = await self._git_pull()
        if output is None:
            # Pull failed — still load whatever is on disk
            self.load_connections()
            return

        if "Already up to date" in output:
            if notify_up_to_date:
                self.notify("Already up to date.")
        else:
            self.notify(f"Synced: {output}", timeout=4)

        self.load_connections()

    def load_connections(self) -> None:
        if not CONNECTIONS_FILE.exists():
            self.notify(
                "connections.json not found. Copy connections.sample.json to get started.",
                severity="error",
                timeout=10,
            )
            return

        try:
            with open(CONNECTIONS_FILE) as f:
                self._connections = json.load(f)
        except json.JSONDecodeError as e:
            self.notify(f"Invalid JSON in connections.json: {e}", severity="error", timeout=10)
            return

        self._apply_filter(self.query_one("#search", Input).value)

    def _apply_filter(self, query: str) -> None:
        table = self.query_one(SSHConnectionTable)
        table.clear()

        q = query.lower()
        filtered = (
            [c for c in self._connections if any(q in str(v).lower() for v in c.values())]
            if q else self._connections
        )

        for conn in filtered:
            table.add_row(
                conn["alias"],
                conn["hostname"],
                conn["user"],
                str(conn.get("port", 22)),
                conn.get("location", "N/A"),
                conn.get("description", "N/A"),
            )

        total = len(self._connections)
        n = len(filtered)
        self.sub_title = f"{n} of {total} connections" if q else f"{total} connections"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Filter connections… (press / to focus)", id="search")
        with Container(id="table-container"):
            yield SSHConnectionTable()
        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            self._apply_filter(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search":
            self.query_one(SSHConnectionTable).focus()

    def action_focus_search(self) -> None:
        self.query_one("#search", Input).focus()

    def action_escape(self) -> None:
        search = self.query_one("#search", Input)
        if search.value:
            search.value = ""
            self.query_one(SSHConnectionTable).focus()
        else:
            self.exit()

    async def action_sync(self) -> None:
        await self._sync_and_reload(notify_up_to_date=True)

    def action_helping(self) -> None:
        self.notify("↑/↓ navigate · Enter connect · / search · c copy · ctrl+r sync · q quit")

    def _build_ssh_command(self, row) -> list[str]:
        user, hostname, port = row[2], row[1], row[3]
        cmd = ["ssh", f"{user}@{hostname}"]
        if port != "22":
            cmd += ["-p", port]
        return cmd

    def action_copy_command(self) -> None:
        if self._highlighted_row_key is None:
            return
        table = self.query_one(SSHConnectionTable)
        try:
            row = table.get_row(self._highlighted_row_key)
        except Exception:
            return

        cmd_str = " ".join(self._build_ssh_command(row))

        copied = False
        for args in [
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
            ["pbcopy"],
        ]:
            try:
                subprocess.run(args, input=cmd_str.encode(), check=True, capture_output=True)
                copied = True
                break
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue

        if copied:
            self.notify(f"Copied: {cmd_str}")
        else:
            self.notify(f"[bold]{cmd_str}[/bold]", title="SSH command", timeout=8)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Called when user presses Enter on a row."""
        row = event.data_table.get_row(event.row_key)
        self.exit(tuple(self._build_ssh_command(row)))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Called when user navigates to a row with arrow keys."""
        if event.row_key is not None:
            self._highlighted_row_key = event.row_key
            row = event.data_table.get_row(event.row_key)
            self.sub_title = f"{row[0]} — {row[2]}@{row[1]}"


if __name__ == "__main__":
    app = ListSSH()
    result = app.run()

    if result:
        subprocess.run(result)
