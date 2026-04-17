from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from chef.mcp.common import graph_index_path, graph_report_path, read_text


mcp = FastMCP("chef-review-mcp")


@mcp.tool()
def review_sources(project_dir: str = ".") -> str:
    index_path = graph_index_path(project_dir)
    report_path = graph_report_path(project_dir)
    return "\n".join(
        [
            f"Graph index: {index_path}",
            f"Graph report: {report_path}",
            "Review order:",
            "1. Read graph index",
            "2. Read graph report",
            "3. Read graph wiki pages",
            "4. Read raw source only with explicit user override",
        ]
    )


@mcp.tool()
def review_checklist(scope: str = "general") -> str:
    return "\n".join(
        [
            f"Scope: {scope}",
            "- behavior regressions",
            "- architectural drift",
            "- missing tests",
            "- graph-detected blast radius",
            "- security-sensitive changes",
            "- documentation drift",
        ]
    )


@mcp.tool()
def review_context(project_dir: str = ".", focus: str = "") -> str:
    index_text = read_text(graph_index_path(project_dir))
    report_text = read_text(graph_report_path(project_dir))
    return "\n\n".join(
        [
            f"Focus: {focus or 'general review'}",
            "Graph Index",
            index_text,
            "Graph Report",
            report_text,
        ]
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

