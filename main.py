import json
import os
import subprocess
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable
from textual.containers import Container

CONNECTIONS_FILE = Path(__file__).parent / "connections.json"


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

    BINDINGS = [("h", "helping", "Help")]

    def on_mount(self) -> None:
        self.load_connections()

    def load_connections(self) -> None:
        table = self.query_one(SSHConnectionTable)
        table.clear()

        if not CONNECTIONS_FILE.exists():
            self.notify(
                f"connections.json not found. Copy connections.sample.json to get started.",
                severity="error",
                timeout=10,
            )
            return

        try:
            with open(CONNECTIONS_FILE) as f:
                connections = json.load(f)
        except json.JSONDecodeError as e:
            self.notify(f"Invalid JSON in connections.json: {e}", severity="error", timeout=10)
            return

        for conn in connections:
            table.add_row(
                conn["alias"],
                conn["hostname"],
                conn["user"],
                str(conn.get("port", 22)),
                conn.get("location", "N/A"),
                conn.get("description", "N/A"),
            )

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="table-container"):
            yield SSHConnectionTable()
        yield Footer()

    def action_helping(self) -> None:
        self.notify("Navigate with ↑/↓, press Enter to connect, q to quit.")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Called when user presses Enter on a row."""
        row = event.data_table.get_row(event.row_key)
        hostname = row[1]
        user = row[2]
        self.exit(("ssh", f"{user}@{hostname}"))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Called when user navigates to a row with arrow keys."""
        if event.row_key is not None:
            row = event.data_table.get_row(event.row_key)
            self.sub_title = f"Highlighted: {row[0]}"


if __name__ == "__main__":
    app = ListSSH()
    result = app.run()

    if result:
        subprocess.run(result)
