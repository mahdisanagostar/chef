#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass(frozen=True)
class Check:
    name: str
    weight: int
    patterns: tuple[str, ...]
    advice: str


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    line_index: int


@dataclass(frozen=True)
class FenceSection:
    title: str
    body: str


CHECKS = (
    Check(
        name="audience",
        weight=5,
        patterns=(r"\baudience\b",),
        advice="Name the audience explicitly.",
    ),
    Check(
        name="objective",
        weight=5,
        patterns=(r"\bobjective\b", r"\bgoal\b", r"\blearning goal\b"),
        advice="State the decision, learning outcome, or behavior change.",
    ),
    Check(
        name="promise",
        weight=5,
        patterns=(r"\bpromise\b",),
        advice="Add a one-sentence promise near the start.",
    ),
    Check(
        name="slogan",
        weight=10,
        patterns=(r"\bslogan\b", r"\bbig idea\b", r"\bgoverning idea\b"),
        advice="Reduce the talk to one compact governing line.",
    ),
    Check(
        name="opening",
        weight=10,
        patterns=(r"\bopening\b", r"\bhook\b", r"\bstakes\b", r"\bfirst line\b"),
        advice="Define the opening move, stakes, and promise line.",
    ),
    Check(
        name="time budget",
        weight=5,
        patterns=(r"\btime budget\b", r"\bduration\b", r"\bminutes?\b"),
        advice="Add a duration and rough section timing.",
    ),
    Check(
        name="close",
        weight=10,
        patterns=(r"\bclosing\b", r"\bclose\b", r"\brecap\b", r"\blast line\b"),
        advice="End with a recap and final implication.",
    ),
    Check(
        name="q&a",
        weight=5,
        patterns=(r"\bq&a\b", r"\bquestions\b", r"\blikely question\b"),
        advice="Prepare likely questions before delivery.",
    ),
)

TRANSITION_WORDS = re.compile(
    r"\b(first|second|third|now|next|finally|before moving on|hold that thought)\b",
    re.IGNORECASE,
)
CONCRETE_WORDS = re.compile(
    r"\b(example|story|demo|visual|diagram|board|comparison|number|metric|case study)\b",
    re.IGNORECASE,
)
FENCE_TITLE_RE = re.compile(r"^fence\b", re.IGNORECASE)

FENCE_FIELDS = (
    ("question_answered", "Question answered", re.compile(r"\bquestion answered\b", re.IGNORECASE)),
    ("memory_target", "Memory target", re.compile(r"\bmemory target\b", re.IGNORECASE)),
    ("evidence", "Evidence", re.compile(r"\bevidence\b", re.IGNORECASE)),
    (
        "board_demo_move",
        "Board/demo move",
        re.compile(r"\b(board/demo move|board move|demo move|visual move)\b", re.IGNORECASE),
    ),
    ("transition_out", "Transition out", re.compile(r"\btransition out\b", re.IGNORECASE)),
    ("time", "Time", re.compile(r"^\s*-\s*time\s*:", re.IGNORECASE | re.MULTILINE)),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_headings(lines: list[str]) -> list[Heading]:
    headings: list[Heading] = []
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match:
            continue
        headings.append(
            Heading(
                level=len(match.group(1)),
                title=match.group(2).strip(),
                line_index=index,
            )
        )
    return headings


def section_body(lines: list[str], headings: list[Heading], index: int) -> str:
    start = headings[index].line_index + 1
    end = len(lines)
    current_level = headings[index].level
    for next_heading in headings[index + 1 :]:
        if next_heading.level <= current_level:
            end = next_heading.line_index
            break
    return "\n".join(lines[start:end]).strip()


def extract_fence_sections(text: str) -> list[FenceSection]:
    lines = text.splitlines()
    headings = parse_headings(lines)
    if not headings:
        return []

    fences_parent_index: int | None = None
    for idx, heading in enumerate(headings):
        if heading.title.strip().lower() == "fences":
            fences_parent_index = idx
            break

    sections: list[FenceSection] = []
    if fences_parent_index is not None:
        parent = headings[fences_parent_index]
        for idx in range(fences_parent_index + 1, len(headings)):
            heading = headings[idx]
            if heading.level <= parent.level:
                break
            if heading.level == parent.level + 1:
                sections.append(
                    FenceSection(
                        title=heading.title,
                        body=section_body(lines, headings, idx),
                    )
                )
        if sections:
            return sections

    for idx, heading in enumerate(headings):
        if FENCE_TITLE_RE.search(heading.title):
            sections.append(
                FenceSection(
                    title=heading.title,
                    body=section_body(lines, headings, idx),
                )
            )
    return sections


def score_checks(text: str) -> tuple[int, list[dict[str, object]]]:
    lowered = text.lower()
    score = 0
    results: list[dict[str, object]] = []
    for check in CHECKS:
        hit = any(re.search(pattern, lowered) for pattern in check.patterns)
        earned = check.weight if hit else 0
        score += earned
        results.append(
            {
                "name": check.name,
                "earned": earned,
                "weight": check.weight,
                "passed": hit,
                "advice": "" if hit else check.advice,
            }
        )
    return score, results


def score_fences(
    fences: list[FenceSection],
) -> tuple[int, bool, list[dict[str, object]], list[str]]:
    details: list[dict[str, object]] = []
    recommendations: list[str] = []
    count = len(fences)
    count_ok = 3 <= count <= 5
    total = 0

    if count_ok:
        total += 8
    else:
        recommendations.append("Use 3-5 named fences or section headings.")

    complete_fences = 0
    evidence_ready = 0
    transitions_ready = 0

    for fence in fences:
        missing: list[str] = []
        found: dict[str, bool] = {}
        for field_name, label, pattern in FENCE_FIELDS:
            present = bool(pattern.search(fence.body))
            found[field_name] = present
            if not present:
                missing.append(label)
        if not missing:
            complete_fences += 1
        if found["evidence"] and found["board_demo_move"]:
            evidence_ready += 1
        if found["transition_out"]:
            transitions_ready += 1
        details.append(
            {
                "title": fence.title,
                "missing": missing,
                "complete": not missing,
            }
        )

    if fences and complete_fences == len(fences):
        total += 6
    elif fences:
        recommendations.append(
            "Complete each fence with time, evidence, board/demo move, and transition."
        )

    if fences and evidence_ready == len(fences):
        total += 3
    elif fences:
        recommendations.append("Give every fence both evidence and a board/demo/visual move.")

    if fences and transitions_ready == len(fences):
        total += 3
    elif fences:
        recommendations.append("Write an explicit transition out for each fence.")

    return total, count_ok, details, recommendations


def detect_transitions(text: str) -> bool:
    return bool(TRANSITION_WORDS.search(text))


def detect_concreteness(text: str) -> bool:
    return bool(CONCRETE_WORDS.search(text))


def build_report(path: Path, text: str) -> dict[str, object]:
    base_score, checks = score_checks(text)
    fences = extract_fence_sections(text)
    fence_score, fence_pass, fence_details, fence_recommendations = score_fences(fences)
    transition_pass = detect_transitions(text)
    concrete_pass = detect_concreteness(text)

    total = base_score + fence_score
    if transition_pass:
        total += 10
    if concrete_pass:
        total += 15

    missing = [item["advice"] for item in checks if not item["passed"]]
    missing.extend(fence_recommendations)
    if not transition_pass:
        missing.append("Add verbal punctuation and explicit transitions.")
    if not concrete_pass:
        missing.append("Add examples, demos, visuals, numbers, or comparisons.")

    report = {
        "path": str(path),
        "score": total,
        "max_score": 100,
        "fence_count": len(fences),
        "fence_structure_pass": fence_pass,
        "fence_details": fence_details,
        "transitions": transition_pass,
        "concreteness": concrete_pass,
        "checks": checks,
        "recommendations": missing,
    }
    return report


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        f"# Outline Audit: {report['path']}",
        "",
        f"- Score: {report['score']}/{report['max_score']}",
        f"- Fence count: {report['fence_count']}",
        f"- Fence structure pass: {'yes' if report['fence_structure_pass'] else 'no'}",
        f"- Explicit transitions: {'yes' if report['transitions'] else 'no'}",
        f"- Concrete evidence signals: {'yes' if report['concreteness'] else 'no'}",
        "",
        "## Checks",
        "",
    ]
    for item in report["checks"]:
        status = "pass" if item["passed"] else "fail"
        lines.append(f"- {item['name']}: {status} ({item['earned']}/{item['weight']})")
        if item["advice"]:
            lines.append(f"  Advice: {item['advice']}")
    if report["fence_details"]:
        lines.extend(["", "## Fence Details", ""])
        for fence in report["fence_details"]:
            if fence["complete"]:
                lines.append(f"- {fence['title']}: complete")
            else:
                missing = ", ".join(fence["missing"])
                lines.append(f"- {fence['title']}: missing {missing}")
    lines.extend(["", "## Recommendations", ""])
    if report["recommendations"]:
        for recommendation in report["recommendations"]:
            lines.append(f"- {recommendation}")
    else:
        lines.append("- Outline meets the rubric with no missing core signals.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit a presentation outline against the TalkCraft rubric.",
    )
    parser.add_argument("outline", help="Path to a markdown or text outline")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of markdown",
    )
    args = parser.parse_args()

    path = Path(args.outline).expanduser().resolve()
    report = build_report(path, read_text(path))
    if args.json:
        print(json.dumps(report, indent=2))
        return
    print(render_markdown(report), end="")


if __name__ == "__main__":
    main()
