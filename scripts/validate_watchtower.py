#!/usr/bin/env python3
"""Dependency-free integrity checks for the static Watchtower app."""
from __future__ import annotations

import json
import sys
import re
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    with (ROOT / path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class WatchtowerHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.citation_data_link = False
        self.targets_data_link = False
        self.parties_data_link = False
        self.local_ids: set[str] = set()
        self.duplicate_ids: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            if element_id in self.local_ids:
                self.duplicate_ids.append(element_id)
            self.local_ids.add(element_id)
        if values.get("href") == "data/case-citations.json":
            self.citation_data_link = True
        if values.get("href") == "data/targets.json":
            self.targets_data_link = True
        if values.get("href") == "data/parties.json":
            self.parties_data_link = True


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    citations = load_json("public/data/case-citations.json")
    targets = load_json("public/data/targets.json")
    changes = load_json("public/data/changes.json")
    parties_data = load_json("public/data/parties.json")
    absence = load_json("public/data/watch-status.json")
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

    allowed = set(citations.get("method", {}).get("treatment_classifications", []))
    for item in judgments:
        classes = item.get("treatment_class")
        require(isinstance(classes, list) and classes and set(classes) <= allowed,
                f"Treatment class missing or not in the method list: {item.get('id')}")

    exclusions = citations.get("verification_exclusions", [])
    judged = {item.get("neutral_citation") for item in judgments}
    for item in exclusions:
        require(item.get("neutral_citation") not in judged,
                f"A case cannot be both cited and excluded: {item.get('neutral_citation')}")
        # An exclusion must rest on the full official text searched for every
        # citation variant (case name alone under-recalls: see Brown v Ridley).
        require(str(item.get("primary_text_checked", "")).startswith("https://"),
                f"Exclusion lacks the official full-text URL that was searched: {item.get('neutral_citation')}")
        require(set(item.get("variants_searched", [])) >= set(citations.get("method", {}).get("query_variants", [])),
                f"Exclusion did not search every query variant: {item.get('neutral_citation')}")

    # Regression: Brown v Ridley [2024] UKUT 14 (LC) cites Buckler in its table of
    # authorities and at paras 154-155, where it distinguishes and limits it.
    brown = [item for item in judgments if item.get("neutral_citation") == "[2024] UKUT 14 (LC)"]
    require(len(brown) == 1, "Brown v Ridley [2024] UKUT 14 (LC) must be in the register.")
    require({"distinguishes", "limits"} <= set(brown[0].get("treatment_class", [])),
            "Brown v Ridley must be classified distinguishes / limits.")
    require("154" in brown[0].get("pinpoint", "") and "155" in brown[0].get("pinpoint", ""),
            "Brown v Ridley pinpoint must give paragraphs 154-155.")
    variants = citations.get("method", {}).get("query_variants", [])
    require("55 P. & C.R." in variants,
            "Query variants must include the page-less report form '55 P. & C.R.'.")

    page = WatchtowerHTML()
    page.feed(html)
    # The visitor-facing page is intentionally compact: the scatter graph and
    # summary lead directly to the footer. Detailed registers remain in their
    # machine-readable feeds and are validated above.
    require(page.citation_data_link,
            "The page must expose data/case-citations.json.")
    require(page.targets_data_link,
            "The page must expose data/targets.json.")
    require(page.parties_data_link,
            "The page must expose data/parties.json.")
    tail = re.search(r'<p class="lh">.*?</p>\s*(.*?)<footer\b', html, re.S)
    require(tail is not None,
            "The page must place its footer after the summary.")
    require(not tail.group(1).strip(),
            "Only the footer may appear after the point/institution/date summary.")
    require(not page.duplicate_ids,
            f"Duplicate HTML IDs found: {page.duplicate_ids}")

    require(bool(changes.get("changes")), "Existing page-change data must remain present.")
    require("name variants" in targets.get("about", "").lower()
            or "property-name" in targets.get("about", "").lower(),
            "Target feed scope should describe the property-name discovery set.")

    # Party/institution coverage is a separate, evidence-linked layer. References must
    # resolve to existing Watchtower checks or exact URLs already in the archive feed.
    parties = parties_data.get("parties", [])
    require(bool(parties), "Party coverage register must contain entries.")
    party_ids = [item.get("id") for item in parties]
    require(None not in party_ids and len(party_ids) == len(set(party_ids)),
            "Party coverage IDs must be present and unique.")
    allowed_party_status = set(parties_data.get("status_values", []))
    require(allowed_party_status == {"partial", "research needed", "no verified target", "role not established"},
            "Party coverage status vocabulary is missing or has changed unexpectedly.")
    absence_ids = {item.get("id") for item in absence.get("targets", [])}
    archive_urls = {item.get("u") for item in target_items}
    require(bool(absence_ids), "Absence-watch data must remain available for party coverage.")
    for item in parties:
        require(item.get("name") and item.get("role_class") and item.get("role"),
                f"Party entry lacks a name or role: {item.get('id')}")
        require(item.get("coverage_status") in allowed_party_status,
                f"Party entry has an invalid coverage status: {item.get('id')}")
        require(item.get("qualification") and item.get("next_action"),
                f"Party entry lacks a qualification or next action: {item.get('id')}")
        for ref in item.get("watch_checks", []):
            require(ref in absence_ids,
                    f"Party entry refers to an unknown absence-watch check: {item.get('id')} / {ref}")
        for url in item.get("wayback_urls", []):
            require(url in archive_urls,
                    f"Party entry refers to a URL not in the Wayback target feed: {item.get('id')} / {url}")
        evidence_ids = [ref.get("id") for ref in item.get("evidence", [])]
        require(len(evidence_ids) == len(set(evidence_ids)),
                f"Duplicate evidence anchor in party entry: {item.get('id')}")
        for ref in item.get("evidence", []):
            require(ref.get("id") and ref.get("title") and str(ref.get("url", "")).startswith("https://"),
                    f"Party entry has an incomplete public evidence anchor: {item.get('id')}")
    # The party register and its supporting renderer remain in the repository,
    # but are intentionally not rendered on the compact scatter-graph page.

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
