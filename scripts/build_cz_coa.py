#!/usr/bin/env python3
"""Build the ERPNext chart tree (cz_coa.json) from the normalized CoA research file.

ERPNext's create_charts() reads a nested dict whose top-level keys are the five root_type
groups; every descendant inherits its root's root_type. The Czech classes 2/3/4 are mixed
(Asset+Liability / Equity+Liability), so we cannot use the class digit as the root. Instead
we place each posting account under the root matching its own root_type, rebuilding the
class -> group -> synthetic -> analytical hierarchy inside each root. A class/group that
spans two roots appears under both, carrying only its matching children.

Run from the repo root:  python3 scripts/build_cz_coa.py
"""
import json
import os

SRC = "docs/plans/research/coa-normalized.json"
OUT = "czech_accounting/czech_accounting/chart_of_accounts/cz_coa.json"

ROOT_LABELS = {
    "Asset": "Aktiva",
    "Liability": "Cizí zdroje",
    "Equity": "Vlastní kapitál",
    "Income": "Výnosy",
    "Expense": "Náklady",
}
CHART_NAME = "Czech Republic - Účtová osnova (podnikatelé)"

nodes = json.load(open(SRC))
by_num = {n["account_number"]: n for n in nodes if n.get("account_number")}


def name_of(num, fallback):
    n = by_num.get(num)
    return n["name_cs"] if n and n.get("name_cs") else fallback


def ensure_group(parent, key, number, root_type):
    """Insert (or fetch) a group node under parent and return it."""
    if key not in parent:
        parent[key] = {"account_number": number, "is_group": 1, "root_type": root_type}
    return parent[key]


tree = {label: {"root_type": rt, "is_group": 1} for rt, label in ROOT_LABELS.items()}

posting = [n for n in nodes if n["level"] in ("synthetic", "analytical")]
placed = 0
for acc in sorted(posting, key=lambda n: n["account_number"]):
    num = acc["account_number"]
    rt = acc["root_type"]
    if rt not in ROOT_LABELS:
        rt = "Equity"  # class 7 closing/off-balance fallback; flagged for accountant review
    root = tree[ROOT_LABELS[rt]]

    cls, grp, syn = num[0], num[:2], num[:3]
    cls_node = ensure_group(root, f"{cls} - {name_of(cls, 'Účtová třída ' + cls)}", cls, rt)
    grp_node = ensure_group(cls_node, f"{grp} - {name_of(grp, 'Skupina ' + grp)}", grp, rt)

    leaf = {
        "account_number": num,
        "account_type": acc.get("account_type") or None,
    }
    key = f"{num} - {acc['name_cs']}"
    if acc["level"] == "analytical":
        parent_syn = acc.get("parent_number") or syn
        syn_node = ensure_group(
            grp_node, f"{parent_syn} - {name_of(parent_syn, parent_syn)}", parent_syn, rt
        )
        syn_node[key] = leaf
    else:
        grp_node[key] = leaf
    placed += 1

chart = {"name": CHART_NAME, "country_code": "cz", "tree": tree}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(chart, f, ensure_ascii=False, indent=1)


def count(d):
    groups = leaves = 0
    for k, v in d.items():
        if k in ("root_type", "account_number", "account_type", "is_group"):
            continue
        if isinstance(v, dict) and v.get("is_group"):
            groups += 1
            g, l = count(v)
            groups += g
            leaves += l
        elif isinstance(v, dict):
            leaves += 1
    return groups, leaves


g, l = count(tree)
print(f"posting accounts placed: {placed}")
print(f"tree: {len(tree)} roots, {g} group nodes, {l} leaf (posting) accounts")
print(f"written: {OUT}")
