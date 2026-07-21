app_name = "czech_accounting"
app_title = "Czech Accounting"
app_publisher = "Hleb Tkachenko"
app_description = "Czech accounting extension for ERPNext"
app_email = "afframe@hapd.cz"
app_license = "mit"

# ERPNext is a hard dependency: this app extends its accounting engine and must
# never be installed on a site that does not have ERPNext.
required_apps = ["erpnext"]

# Fixtures owned by this app. Export with:
#   bench --site <site> export-fixtures --app czech_accounting
# Stream 1 pre-declares the doctypes all three streams use so Streams 2 and 3 only drop
# fixture JSON files and never edit this list. Module-scoped doctypes filter by module;
# module-less ERPNext doctypes filter by a "CZ-" name prefix (use that prefix for Czech records).
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Czech Accounting"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Czech Accounting"]]},
    {"dt": "Print Format", "filters": [["module", "=", "Czech Accounting"]]},
    {"dt": "Account Category", "filters": [["name", "like", "CZ-%"]]},
    {"dt": "Financial Report Template", "filters": [["name", "like", "CZ-%"]]},
    {"dt": "Asset Category", "filters": [["name", "like", "CZ-%"]]},
    {"dt": "Finance Book", "filters": [["name", "like", "CZ-%"]]},
]

# Stream 2 — boundary validation on the invoice agendas (require DUZP on VAT
# documents; warn on reverse-charge / supply-type mismatch).
doc_events = {
    "Sales Invoice": {"validate": "czech_accounting.doc_events.validate_sales_invoice"},
    "Purchase Invoice": {"validate": "czech_accounting.doc_events.validate_purchase_invoice"},
}

# The CZ-Daňové odpisy Finance Book must carry statutory § 31/§ 32 amounts, not ERPNext's
# straight line. A subclass rewrites the schedule once ERPNext has finished submitting it.
override_doctype_class = {
    "Asset Depreciation Schedule": "czech_accounting.assets.cz_ads.CzechAssetDepreciationSchedule"
}
