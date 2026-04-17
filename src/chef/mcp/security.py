from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from chef.mcp.common import (
    graph_index_path,
    graph_report_path,
    manifest_warning,
    read_text,
)

mcp = FastMCP("chef-security-mcp")


@mcp.tool()
def security_review_order(project_dir: str = ".") -> str:
    lines: list[str] = []
    warning = manifest_warning(project_dir)
    if warning:
        lines.append(warning)
    lines.extend(
        [
            "Security review order:",
            f"1. {graph_index_path(project_dir)}",
            f"2. {graph_report_path(project_dir)}",
            "3. related graph wiki pages",
            "4. raw source only on explicit user request",
        ]
    )
    return "\n".join(lines)


@mcp.tool()
def owasp_prompt(language: str = "general") -> str:
    return "\n".join(
        [
            f"Language: {language}",
            "- validate inputs",
            "- constrain outputs",
            "- review auth and session boundaries",
            "- review secret handling",
            "- review injection surfaces",
            "- review unsafe deserialization and code execution paths",
        ]
    )


@mcp.tool()
def security_context(project_dir: str = ".", focus: str = "sensitive paths") -> str:
    index_text = read_text(graph_index_path(project_dir))
    report_text = read_text(graph_report_path(project_dir))
    sections: list[str] = []
    warning = manifest_warning(project_dir)
    if warning:
        sections.append(warning)
    sections.extend(
        [
            f"Focus: {focus}",
            "Graph Index",
            index_text,
            "Graph Report",
            report_text,
        ]
    )
    return "\n\n".join(sections)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
