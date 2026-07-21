app_name = "czech_accounting"
app_title = "Czech Accounting"
app_publisher = "Hleb Tkachenko"
app_description = "Czech accounting extension for ERPNext"
app_email = "afframe@hapd.cz"
app_license = "mit"

# ERPNext is a hard dependency: this app extends its accounting engine and must
# never be installed on a site that does not have ERPNext.
required_apps = ["erpnext"]

# Fixtures (Custom Fields, Property Setters) owned by this app's module are
# exported to source with: bench --site <site> export-fixtures --app czech_accounting
# Uncomment and extend once the first custom fields exist.
# fixtures = [
#     {"dt": "Custom Field", "filters": [["module", "=", "Czech Accounting"]]},
#     {"dt": "Property Setter", "filters": [["module", "=", "Czech Accounting"]]},
# ]
