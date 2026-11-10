#!/usr/bin/env python3
"""Dependency-free integrity checks for the static Watchtower app."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    with (ROOT / path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class WatchtowerHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.case_section_count = 0
        self.citation_data_link = False
        self.local_ids: set[str] = set()
        self.duplicate_ids: list[str] = []
        self.wayback_heading = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            if element_id in self.local_ids:
                self.duplicate_ids.append(element_id)
            self.local_ids.add(element_id)
        if element_id == "case-citations":
            self.case_section_count += 1
        if values.get("href") == "data/case-citations.json":
            self.citation_data_link = True
        if element_id == "wayback":
            self.wayback_heading = True


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    citations = load_json("public/data/case-citations.json")
    targets = load_json("public/data/targets.json")
    changes = load_json("public/data/changes.json")
    html = (ROOT / "public/index.html").read_text(encoding="utf-8")

    judgments = citations.get("judicial_citations", [])
    target_items = targets.get("targets", [])
    target_urls = [item.get("u") for item in target_items]
    order = targets.get("order", [])
    primary_case = citations.get("primary_case", {})

    require(primary_case.get("neutral_citation") == "[1987] EWCA Civ 2",
            "Primary case neutral citation is missing or incorrect.")
    require(len(judgments) >= 4, "Expected at least four verified later judgments.")
    require(
        [item.get("judgment_date") for item in judgments]
        == sorted(item.get("judgment_date") for item in judgments),
        "Judicial citations must be ordered chronologically."
    )

    ids = [item.get("id") for item in judgments]
    require(None not in ids and len(ids) == len(set(ids)),
            "Judicial citation IDs must be present and unique.")

    for item in judgments:
        require(item.get("neutral_citation"), f"Missing neutral citation: {item.get('id')}")
        require(item.get("pinpoint"), f"Missing pinpoint: {item.get('id')}")
        require(item.get("primary_url", "").startswith("https://"),
                f"Missing HTTPS primary URL: {item.get('id')}")
        require(item["primary_url"] in target_urls,
                f"Primary URL is absent from weekly archive targets: {item['id']}")
        require(item["primary_url"] in order,
                f"Primary URL is absent from target processing order: {item['id']}")

    require(len(target_urls) == len(set(target_urls)),
            "Duplicate URLs in targets.json.")
    require(len(order) == len(set(order)), "Duplicate URLs in targets.json order.")
    require(targets.get("counts", {}).get("targets") == len(target_items),
            "targets.json target count does not match the target array.")
    require(set(target_urls).issubset(set(order)),
            "One or more target URLs are missing from processing order.")

    exclusions = citations.get("verification_exclusions", [])
    require(
        not any(item.get("neutral_citation") == "[2024] UKUT 14 (LC)"
                for item in judgments),
        "Brown v Ridley is an exclusion, not a verified Buckler citation."
    )
    require(
        any(item.get("neutral_citation") == "[2024] UKUT 14 (LC)"
            for item in exclusions),
        "The Brown v Ridley exclusion note is missing."
    )

    page = WatchtowerHTML()
    page.feed(html)
    require(page.case_section_count == 1,
            "The page must contain exactly one judicial citation section.")
    require(page.citation_data_link,
            "The page must link to data/case-citations.json.")
    require(page.wayback_heading,
            "The page must retain the Wayback target section.")
    require(not page.duplicate_ids,
            f"Duplicate HTML IDs found: {page.duplicate_ids}")

    require(bool(changes.get("changes")), "Existing page-change data must remain present.")
    require("name variants" in targets.get("about", "").lower()
            or "property-name" in targets.get("about", "").lower(),
            "Target feed scope should describe the property-name discovery set.")

    print(
        "Watchtower validation passed: "
        f"{len(judgments)} judicial citations, "
        f"{len(target_items)} archived targets, "
        f"{len(changes.get('changes', []))} existing page-change records."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Watchtower validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
