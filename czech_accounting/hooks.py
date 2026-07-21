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
