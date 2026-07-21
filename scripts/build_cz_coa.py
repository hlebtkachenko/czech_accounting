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
from collections import Counter

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

MAPPING = "docs/plans/research/coa-statement-mapping.json"
statement_map = json.load(open(MAPPING, encoding="utf-8"))


def leaf_node(num, account_type):
    """A posting account, tagged with its Czech statement-row Account Category."""
    node = {"account_number": num, "account_type": account_type or None}
    entry = statement_map.get(num)
    if entry and entry.get("category_code"):
        node["account_category"] = "CZ-" + entry["category_code"]
    return node


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


def sibling_id(acc):
    """The tree parent an account is placed under, so siblings can be compared for name clashes."""
    n = acc["account_number"]
    if acc["level"] == "analytical":
        return (acc["root_type"], n[:2], acc.get("parent_number") or n[:3])
    return (acc["root_type"], n[:2])


# The source gives a few distinct synthetics the same Czech name (540/548 "Jiné provozní náklady",
# 460/461, 640/648). Those siblings keep the number-prefixed name so they stay two accounts; every
# other account uses the clean bare name.
_sibling_names = {}
for _acc in posting:
    _sibling_names.setdefault(sibling_id(_acc), Counter())[_acc["name_cs"]] += 1


def key_of(acc):
    base = acc["name_cs"]
    if _sibling_names[sibling_id(acc)][base] > 1:
        return f"{acc['account_number']} - {base}"
    return base


placed = 0
for acc in sorted(posting, key=lambda n: n["account_number"]):
    num = acc["account_number"]
    rt = acc["root_type"]
    root = tree[ROOT_LABELS[rt]]  # an unexpected root_type fails loudly here with KeyError

    cls, grp, syn = num[0], num[:2], num[:3]
    # Structural class/group nodes carry no account_number, so the class digit must stay in the
    # name. Accounts that DO carry a number use the bare Czech name — otherwise ERPNext renders
    # "{number} - {name}" and the number, already in the name, shows up twice (e.g. "548 - 548 -").
    cls_node = ensure_group(root, f"{cls} - {name_of(cls, 'Účtová třída ' + cls)}", rt)
    grp_node = ensure_group(cls_node, f"{grp} - {name_of(grp, 'Skupina ' + grp)}", rt)
    key = key_of(acc)

    if acc["level"] == "analytical":
        parent_syn = acc.get("parent_number") or syn
        syn_key = key_of(by_num[parent_syn]) if parent_syn in by_num else name_of(parent_syn, parent_syn)
        syn_node = ensure_group(grp_node, syn_key, rt, parent_syn)
        syn_node[key] = leaf_node(num, acc.get("account_type"))
    elif num in synth_with_children:
        ensure_group(grp_node, key, rt, num)  # synthetic with analytics -> group, not posting
    else:
        grp_node[key] = leaf_node(num, acc.get("account_type"))
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

# --- Account Category fixture from the statement mapping (seam to Stream 3) ---
FIX_OUT = "czech_accounting/fixtures/account_category.json"
cat_root, cat_label = {}, {}
for _num, _entry in statement_map.items():
    _code = _entry.get("category_code")
    if not _code:
        continue
    _rt = by_num[_num]["root_type"]
    cat_root.setdefault(_code, set()).add(_rt)
    cat_label[_code] = _entry.get("category_label") or _code
records = []
for _code in sorted(cat_root):
    _rt = sorted(cat_root[_code])[0]
    _name = "CZ-" + _code
    records.append({
        "doctype": "Account Category", "name": _name, "account_category_name": _name,
        "root_type": _rt, "description": cat_label[_code],
    })
    if len(cat_root[_code]) > 1:
        print(f"  WARN category {_code} spans roots {sorted(cat_root[_code])}; using {_rt}")
with open(FIX_OUT, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=1)
print(f"account categories: {len(records)} -> {FIX_OUT}")
