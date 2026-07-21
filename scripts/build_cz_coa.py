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
OUT = "czech_accounting/chart_of_accounts/cz_coa.json"

ROOT_LABELS = {
    "Asset": "Aktiva",
    "Liability": "Cizí zdroje",
    "Equity": "Vlastní kapitál",
    "Income": "Výnosy",
    "Expense": "Náklady",
}
CHART_NAME = "Czech Republic - Účtová osnova (podnikatelé)"

# Standard accounts the client's exported chart omits but a build-to-sell developer needs,
# plus DPH direction analytics. 61x change-in-state and 62x aktivace are Income (výnosové).
NAME_OVERRIDES = {"61": "Změna stavu zásob vlastní činnosti", "62": "Aktivace"}
AUGMENT = [
    # number, name_cs, root_type, account_type, level, parent_number
    ("611", "Změna stavu nedokončené výroby", "Income", None, "synthetic", None),
    ("612", "Změna stavu polotovarů vlastní výroby", "Income", None, "synthetic", None),
    ("613", "Změna stavu výrobků", "Income", None, "synthetic", None),
    ("614", "Změna stavu zvířat", "Income", None, "synthetic", None),
    ("621", "Aktivace materiálu a zboží", "Income", None, "synthetic", None),
    ("622", "Aktivace vnitropodnikových služeb", "Income", None, "synthetic", None),
    ("623", "Aktivace dlouhodobého nehmotného majetku", "Income", None, "synthetic", None),
    ("624", "Aktivace dlouhodobého hmotného majetku", "Income", None, "synthetic", None),
    ("343.100", "DPH na vstupu", "Liability", "Tax", "analytical", "343"),
    ("343.200", "DPH na výstupu", "Liability", "Tax", "analytical", "343"),
]

nodes = json.load(open(SRC))
for _num, _name, _rt, _at, _lvl, _parent in AUGMENT:
    nodes.append({
        "account_number": _num, "name_cs": _name, "root_type": _rt,
        "account_type": _at, "level": _lvl, "parent_number": _parent, "is_group": False,
    })
by_num = {n["account_number"]: n for n in nodes if n.get("account_number")}


def name_of(num, fallback):
    if num in NAME_OVERRIDES:
        return NAME_OVERRIDES[num]
    n = by_num.get(num)
    return n["name_cs"] if n and n.get("name_cs") else fallback


def ensure_group(parent, key, root_type, number=None):
    """Insert (or fetch) a group node under parent and return it.

    Intermediate class/group nodes carry NO account_number: a Czech class/group can span two
    ERPNext root_types (classes 2, 3, 4), and ERPNext requires account_number to be unique per
    company. Only real accounts (synthetic parents and leaves) keep their number; ERPNext
    auto-suffixes any duplicate group names.
    """
    if key not in parent:
        node = {"is_group": 1, "root_type": root_type}
        if number:
            node["account_number"] = number
        parent[key] = node
    return parent[key]


tree = {label: {"root_type": rt, "is_group": 1} for rt, label in ROOT_LABELS.items()}

posting = [n for n in nodes if n["level"] in ("synthetic", "analytical")]
# A synthetic that carries analytical children is a group, not a posting account.
synth_with_children = {a.get("parent_number") for a in posting if a["level"] == "analytical"}
placed = 0
for acc in sorted(posting, key=lambda n: n["account_number"]):
    num = acc["account_number"]
    rt = acc["root_type"]
    if rt not in ROOT_LABELS:
        rt = "Equity"  # class 7 closing/off-balance fallback; flagged for accountant review
    root = tree[ROOT_LABELS[rt]]

    cls, grp, syn = num[0], num[:2], num[:3]
    cls_node = ensure_group(root, f"{cls} - {name_of(cls, 'Účtová třída ' + cls)}", rt)
    grp_node = ensure_group(cls_node, f"{grp} - {name_of(grp, 'Skupina ' + grp)}", rt)
    key = f"{num} - {acc['name_cs']}"

    if acc["level"] == "analytical":
        parent_syn = acc.get("parent_number") or syn
        syn_node = ensure_group(
            grp_node, f"{parent_syn} - {name_of(parent_syn, parent_syn)}", rt, parent_syn
        )
        syn_node[key] = {"account_number": num, "account_type": acc.get("account_type") or None}
    elif num in synth_with_children:
        ensure_group(grp_node, key, rt, num)  # synthetic with analytics -> group, not posting
    else:
        grp_node[key] = {"account_number": num, "account_type": acc.get("account_type") or None}
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
