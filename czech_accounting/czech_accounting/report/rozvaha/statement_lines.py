# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Statutory statement structure and the Account Category seam (Stream 1, READ-ONLY).

Stream 1 owns the Account Category taxonomy (Decree 500/2002 Sb., Příloha 1 = Rozvaha,
Příloha 2 = VZZ druhové) and assigns one category to every posting Account. The category
names are the join key. Stream 1's taxonomy is namespaced:

  CZ-rozvaha-aktiva-<...>   Rozvaha, Aktiva rows       (root_type Asset / Liability)
  CZ-rozvaha-pasiva-<...>   Rozvaha, Pasiva rows       (root_type Equity / Liability / Asset)
  CZ-vzz-<...>              VZZ druhové rows           (root_type Income / Expense)

The name segments after the prefix encode the statutory hierarchy, e.g.
``CZ-rozvaha-aktiva-b-ii-2`` = B.II.2 Hmotné movité věci a jejich soubory. The Rozvaha
report builds its tree from the live categories (so it stays in sync with Stream 1); the
VZZ report uses the explicit statutory ordering below.

Stream 3 renders rows from these categories; it never creates or assigns them. If a needed
row has no category, request it from Stream 1 (do not add it here).

This module is intentionally free of any Frappe import so it can be reused by the report
controllers, the tests, and run stand-alone. Draft-for-accountant-signoff (repo invariant).
"""

LAYOUT_LAW = "Decree 500/2002 Sb."
LAYOUT_EFFECTIVE_FROM = "2024-01-01"

ROZVAHA_PREFIX = "CZ-rozvaha-"
VZZ_PREFIX = "CZ-vzz-"

# Rozvaha row A.V — the provisional / booked result of the period is added here so that
# Aktiva = Pasiva while class 5/6 accounts are still open.
RESULT_CATEGORY = "CZ-rozvaha-pasiva-a-v"

# Tax authority (accounts 341/342/343/345/346/347) is a receivable in a nadměrný-odpočet
# period and a payable otherwise. Stream 1 assigns the pasiva category; this report routes
# an account to its Aktiva counterpart when the period balance is a net debit.
DUAL_SIDE_ROUTING = {
    "CZ-rozvaha-pasiva-c-ii-8-5": "CZ-rozvaha-aktiva-c-ii-2-4-3",
}

# Synthetic buckets that keep the statement reconciling when an account is unmapped; they
# are never assigned by Stream 1 and surface anything that would otherwise be lost.
UNMAPPED_ASSET = "__unmapped_debit__"
UNMAPPED_LIABILITY = "__unmapped_credit__"
UNMAPPED_ASSET_LABEL = "Nezařazené účty (aktivní zůstatek)"
UNMAPPED_LIABILITY_LABEL = "Nezařazené účty (pasivní zůstatek)"
UNMAPPED_PL_LABEL = "Nezařazené náklady a výnosy"

# Account-number prefixes that make an account a *correction* (Korekce column, Aktiva side):
# 07x/08x = oprávky (accumulated depreciation), 09x/19x/29x/39x = opravné položky.
CORRECTION_PREFIXES = ("07", "08", "09", "19", "29", "39")

# Accounts inside those groups that are NOT contra-asset (they belong in Brutto, not Korekce):
# 097 Oceňovací rozdíl k nabytému majetku (a valuation account; its own contra is 098),
# 395 Vnitřní zúčtování, 396/398 Spojovací účty (clearing/consolidation, not opravné položky).
NON_CORRECTION_NUMBERS = ("097", "395", "396", "398")

# Roman numerals used in the statutory row codes, mapped to their ordinal for sorting.
_ROMAN = {r: i for i, r in enumerate(
    ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"], start=1)}


def is_correction_account(account_number) -> bool:
    """True when the account is oprávky / opravná položka (contributes to Korekce)."""
    if not account_number:
        return False
    number = str(account_number)
    if number[:3] in NON_CORRECTION_NUMBERS:
        return False
    return number[:2] in CORRECTION_PREFIXES


def category_side(name: str) -> str:
    """'A' for an Aktiva category, 'P' for a Pasiva category."""
    return "A" if "aktiva" in name else "P"


def _seg_key(seg: str):
    if seg in _ROMAN:
        return (1, _ROMAN[seg])
    if seg.isdigit():
        return (2, int(seg))
    return (0, seg)  # 'aktiva'/'pasiva' and letter segments a/b/c/d


def category_sort_key(name: str):
    """Statutory ordering key derived from the category-name segments."""
    segs = name[len(ROZVAHA_PREFIX):].split("-") if name.startswith(ROZVAHA_PREFIX) else name.split("-")
    return tuple(_seg_key(s) for s in segs)


# ---------------------------------------------------------------------------
# VZZ druhové (Příloha 2) — explicit statutory ordering.
# Each entry: code, label, indent, kind, category, nature, members
#   kind "L" leaf(category), "S" subtotal(members), "R" result(members), "T" grand total
#   nature "revenue" -> presented as (credit-debit); "cost" -> as (debit-credit)
# The grand total *** is computed straight from the GL (-sum(debit-credit) over all class
# 5/6 accounts) so it always reconciles to Rozvaha A.V.
# ---------------------------------------------------------------------------
def _V(code, label, indent, kind, category=None, nature=None, members=None):
    return {"code": code, "label": label, "indent": indent, "kind": kind,
            "category": category, "nature": nature, "members": members or []}


VZZ_LAYOUT = [
    _V("I", "I. Tržby z prodeje výrobků a služeb", 0, "L", "CZ-vzz-i", "revenue"),
    _V("II", "II. Tržby za prodej zboží", 0, "L", "CZ-vzz-ii", "revenue"),
    _V("A", "A. Výkonová spotřeba", 0, "S", members=["A.1", "A.2", "A.3"]),
    _V("A.1", "A.1 Náklady vynaložené na prodané zboží", 1, "L", "CZ-vzz-a-1", "cost"),
    _V("A.2", "A.2 Spotřeba materiálu a energie", 1, "L", "CZ-vzz-a-2", "cost"),
    _V("A.3", "A.3 Služby", 1, "L", "CZ-vzz-a-3", "cost"),
    _V("B", "B. Změna stavu zásob vlastní činnosti (+/−)", 0, "L", "CZ-vzz-b", "cost"),
    _V("C", "C. Aktivace (−)", 0, "L", "CZ-vzz-c", "cost"),
    _V("D", "D. Osobní náklady", 0, "S", members=["D.1", "D.2.1", "D.2.2"]),
    _V("D.1", "D.1 Mzdové náklady", 1, "L", "CZ-vzz-d-1", "cost"),
    _V("D.2.1", "D.2.1 Náklady na sociální zabezpečení a zdravotní pojištění", 1, "L", "CZ-vzz-d-2-1", "cost"),
    _V("D.2.2", "D.2.2 Ostatní náklady (osobní)", 1, "L", "CZ-vzz-d-2-2", "cost"),
    _V("E", "E. Úpravy hodnot v provozní oblasti", 0, "S", members=["E.1.1", "E.3"]),
    _V("E.1.1", "E.1.1 Úpravy hodnot DNM a DHM – trvalé", 1, "L", "CZ-vzz-e-1-1", "cost"),
    _V("E.3", "E.3 Úpravy hodnot pohledávek", 1, "L", "CZ-vzz-e-3", "cost"),
    _V("III", "III. Ostatní provozní výnosy", 0, "S", members=["III.1", "III.2", "III.3"]),
    _V("III.1", "III.1 Tržby z prodaného dlouhodobého majetku", 1, "L", "CZ-vzz-iii-1", "revenue"),
    _V("III.2", "III.2 Tržby z prodaného materiálu", 1, "L", "CZ-vzz-iii-2", "revenue"),
    _V("III.3", "III.3 Jiné provozní výnosy", 1, "L", "CZ-vzz-iii-3", "revenue"),
    _V("F", "F. Ostatní provozní náklady", 0, "S", members=["F.1", "F.2", "F.3", "F.4", "F.5"]),
    _V("F.1", "F.1 Zůstatková cena prodaného dlouhodobého majetku", 1, "L", "CZ-vzz-f-1", "cost"),
    _V("F.2", "F.2 Prodaný materiál", 1, "L", "CZ-vzz-f-2", "cost"),
    _V("F.3", "F.3 Daně a poplatky (v provozní oblasti)", 1, "L", "CZ-vzz-f-3", "cost"),
    _V("F.4", "F.4 Rezervy v provozní oblasti a komplexní náklady příštích období", 1, "L", "CZ-vzz-f-4", "cost"),
    _V("F.5", "F.5 Jiné provozní náklady", 1, "L", "CZ-vzz-f-5", "cost"),
    _V("STAR", "* Provozní výsledek hospodaření", 0, "R",
       members=["I", "II", "A", "B", "C", "D", "E", "III", "F"]),
    _V("IV.2", "IV.2 Ostatní výnosy z podílů", 0, "L", "CZ-vzz-iv-2", "revenue"),
    _V("VI.2", "VI.2 Ostatní výnosové úroky a podobné výnosy", 0, "L", "CZ-vzz-vi-2", "revenue"),
    _V("VII", "VII. Ostatní finanční výnosy", 0, "L", "CZ-vzz-vii", "revenue"),
    _V("I.fin", "I.fin Úpravy hodnot a rezervy ve finanční oblasti", 0, "L", "CZ-vzz-i-fin", "cost"),
    _V("J.2", "J.2 Ostatní nákladové úroky a podobné náklady", 0, "L", "CZ-vzz-j-2", "cost"),
    _V("K", "K. Ostatní finanční náklady", 0, "L", "CZ-vzz-k", "cost"),
    _V("DSTAR", "** Finanční výsledek hospodaření", 0, "R",
       members=["IV.2", "VI.2", "VII", "I.fin", "J.2", "K"]),
    _V("L", "L. Daň z příjmů", 0, "S", members=["L.1", "L.2"]),
    _V("L.1", "L.1 Daň z příjmů splatná", 1, "L", "CZ-vzz-l-1", "cost"),
    _V("L.2", "L.2 Daň z příjmů odložená (+/−)", 1, "L", "CZ-vzz-l-2", "cost"),
    _V("M", "M. Převod podílu na výsledku hospodaření společníkům (+/−)", 0, "L", "CZ-vzz-m", "cost"),
    _V("TSTAR", "*** Výsledek hospodaření za účetní období (+/−)", 0, "T"),
]
