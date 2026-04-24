from __future__ import annotations

import httpx
from rich.markdown import Markdown
from rich.table import Table
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Static

from studyagent.tui.screens.chat import API_BASE


class DashboardScreen(Screen):
    CSS = """
    DashboardScreen {
        layout: vertical;
    }
    #dashboard-area {
        height: 1fr;
        padding: 1 2;
        scrollbar-size: 1 1;
    }
    #dashboard-status {
        dock: bottom;
        height: 1;
        background: $primary-background-darken-1;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="dashboard-area")
        yield Static("Loading dashboard...", id="dashboard-status")

    async def on_mount(self) -> None:
        await self._load_data()

    async def _load_data(self) -> None:
        area = self.query_one("#dashboard-area", VerticalScroll)
        status = self.query_one("#dashboard-status", Static)

        overview = {}
        weak_areas = []
        recommendations = []
        domains = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(f"{API_BASE}/analytics/default/overview")
                if resp.status_code == 200:
                    overview = resp.json()
            except Exception:
                pass

            try:
                resp = await client.get(f"{API_BASE}/analytics/default/weak-areas", params={"limit": 8})
                if resp.status_code == 200:
                    weak_areas = resp.json()
            except Exception:
                pass

            try:
                resp = await client.get(f"{API_BASE}/analytics/default/recommendations")
                if resp.status_code == 200:
                    recommendations = resp.json()
            except Exception:
                pass

            try:
                resp = await client.get(f"{API_BASE}/analytics/default/domains")
                if resp.status_code == 200:
                    domains = resp.json()
            except Exception:
                pass

        # Build dashboard
        for child in list(area.children):
            child.remove()

        # Overview section
        if overview:
            mastered = overview.get("mastered", 0)
            learning = overview.get("learning", 0)
            new = overview.get("new", 0)
            avg = overview.get("avg_mastery", 0)
            due = overview.get("due_reviews", 0)
            total = overview.get("total_concepts", 0)

            bar_len = 30
            m_bar = "#" * int(bar_len * mastered / max(total, 1))
            l_bar = "=" * int(bar_len * learning / max(total, 1))
            n_bar = "-" * int(bar_len * new / max(total, 1))

            area.mount(Static(Markdown(f"""# StudyAgent Dashboard

## Overview
- **Total Concepts:** {total}
- **Avg Mastery:** {avg:.0%}
- **Due Reviews:** {due}
- Progress: `[{m_bar}{l_bar}{n_bar}]` {mastered} mastered / {learning} learning / {new} new
""")))

        # Domain breakdown
        if domains:
            table = Table(title="Domain Mastery", show_lines=False)
            table.add_column("Domain", style="cyan")
            table.add_column("Concepts", justify="right")
            table.add_column("Avg Mastery", justify="right", style="green")
            for d in domains:
                bar = "#" * int(20 * d["avg_mastery"])
                table.add_row(d["domain"], str(d["concepts"]), f"{d['avg_mastery']:.0%} [{bar}]")
            area.mount(Static(table))

        # Weak areas
        if weak_areas:
            weak_md = "## Weak Areas\n"
            for w in weak_areas:
                bar = "#" * int(20 * w["mastery"])
                weak_md += f"- **{w['concept_name']}** ({w['domain']}): {w['mastery']:.0%} `[{bar}]`\n"
            area.mount(Static(Markdown(weak_md)))

        # Recommendations
        if recommendations:
            rec_md = "## Recommended Next Topics\n"
            for r in recommendations:
                prereq = ", ".join(r.get("prerequisites", []))
                rec_md += f"- **{r['name']}** ({r['domain']}, difficulty {r['difficulty']:.1f})"
                if prereq:
                    rec_md += f" — prereqs: {prereq}"
                rec_md += "\n"
            area.mount(Static(Markdown(rec_md)))

        if not overview:
            area.mount(Static(Markdown("## Welcome!\n\nStart chatting to build your knowledge profile.")))

        status.update(f"StudyAgent v0.1 | Dashboard | {overview.get('total_concepts', 0)} concepts tracked")

    async def refresh(self) -> None:
        await self._load_data()
