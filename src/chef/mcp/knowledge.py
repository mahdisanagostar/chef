from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from chef.mcp.common import (
    graph_dir,
    graph_index_path,
    graph_report_path,
    manifest_warning,
    read_text,
    vault_dir,
)

mcp = FastMCP("chef-knowledge-mcp")


@mcp.tool()
def vault_summary(project_dir: str = ".") -> str:
    vault = vault_dir(project_dir)
    lines: list[str] = []
    warning = manifest_warning(project_dir)
    if warning:
        lines.append(warning)
    lines.extend(
        [
            f"Vault: {vault}",
            f"Home: {(vault / 'Home' / 'Home.md').exists()}",
            f"Memory: {(vault / 'Memory' / 'Memory.md').exists()}",
            f"Graphify: {(vault / 'Graphify' / 'index.md').exists()}",
        ]
    )
    return "\n".join(lines)


@mcp.tool()
def read_graph_index(project_dir: str = ".") -> str:
    return read_text(graph_index_path(project_dir))


@mcp.tool()
def read_graph_report(project_dir: str = ".") -> str:
    return read_text(graph_report_path(project_dir))


@mcp.tool()
def list_graph_pages(project_dir: str = ".") -> list[str]:
    wiki_dir = graph_dir(project_dir) / "wiki"
    if not wiki_dir.exists():
        return []
    return sorted(str(path.relative_to(wiki_dir)) for path in wiki_dir.rglob("*.md"))


@mcp.tool()
def read_graph_page(project_dir: str = ".", page: str = "index.md") -> str:
    wiki_dir = graph_dir(project_dir) / "wiki"
    target = (wiki_dir / page).resolve()
    if wiki_dir not in target.parents and target != wiki_dir:
        return "Page path escapes graph wiki root."
    return read_text(target)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
