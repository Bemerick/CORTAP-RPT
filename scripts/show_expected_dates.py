#!/usr/bin/env python3
"""Show what date expressions should be in the template"""

print("="*80)
print("EXPECTED DATE FIELD EXPRESSIONS")
print("="*80)

expected = [
    ("Section I - Report Date", "{{ date_format(project.report_date) }}"),
    ("Section II.2 - Scoping Meeting", "{{ date_format(project.scoping_meeting_date) }}"),
    ("Section II.2 - Site Visit Start", "{{ date_format(project.site_visit_start_date) }}"),
    ("Section II.2 - Site Visit End", "{{ date_format(project.site_visit_end_date) }}"),
    ("Section II.2 - Exit Conference", "{{ date_format(project.exit_conference_date) }}"),
    ("Section IV - Due Date (conditional)", "{{ date_format(area.due_date) if area.due_date else '' }}"),
    ("Section IV - Date Closed (conditional)", "{{ 'Closed ' + date_format(area.date_closed) if area.date_closed else '' }}"),
]

for location, expression in expected:
    print(f"\n{location}:")
    print(f"  {expression}")

print("\n" + "="*80)
print("SEARCH AND REPLACE IN WORD")
print("="*80)

print("""
These date fields were likely removed. You need to add them back:

1. Find where the report date should be (usually Section I, first page)
2. Find the Process dates table (Section II.2)
3. Find the assessment areas with deficiencies (Section IV)

For each location, insert the appropriate expression from above.

IMPORTANT: The syntax MUST be exactly:
  - {{ date_format(field_name) }}
  - NOT {{ field_name | date_format }}
  - NOT {{ date_format field_name }}
  - NOT just {{ field_name }}

The date_format() is a function that needs to be called with parentheses.
""")
