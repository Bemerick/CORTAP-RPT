#!/usr/bin/env python3
"""Show workaround for Section number XML splitting issue"""

print("="*80)
print("WORKAROUND FOR SECTION NUMBER XML SPLITTING")
print("="*80)

print("""
The core issue: Word breaks "Section 5307" in the XML so Jinja2 sees:
  'Section ' + 5307 + ' Program...'
                ^
                This becomes a bare integer token causing syntax error

SOLUTION: Use string concatenation with the number as a separate piece:

Instead of this string literal:
  'Section 5307 Program Requirements'

Build it dynamically:
  'Section ' + '5307' + ' Program Requirements'

Or even better, use variables that we pre-define.
""")

print("\n" + "="*80)
print("RECOMMENDED FIX")
print("="*80)

print("""
At the TOP of your template (before any Section usage), add these variables:

{% set section_5307_name = 'Section 5307 Program Requirements' %}
{% set section_5310_name = 'Section 5310 Program Requirements' %}
{% set section_5311_name = 'Section 5311 Program Requirements' %}

Then use the VARIABLES in your loops:

BEFORE:
{% for assessment in assessments if assessment.review_area == 'Section 5307 Program Requirements' %}

AFTER:
{% for assessment in assessments if assessment.review_area == section_5307_name %}

This way the string 'Section 5307...' appears in a {% set %} statement where
it's on the right side of the equals, and Word's XML splitting won't break it.
""")

print("\n" + "="*80)
print("SPECIFIC REPLACEMENTS NEEDED")
print("="*80)

print("""
STEP 1: Add these at the top of Section IV (or at the very start of template):
--------
{% set section_5307_name = 'Section 5307 Program Requirements' %}
{% set section_5310_name = 'Section 5310 Program Requirements' %}
{% set section_5311_name = 'Section 5311 Program Requirements' %}


STEP 2: Replace the three for loops:
--------
FIND:
{% for assessment in assessments if assessment.review_area == 'Section 5307 Program Requirements' %}

REPLACE:
{% for assessment in assessments if assessment.review_area == section_5307_name %}

--------
FIND:
{% for assessment in assessments if assessment.review_area == 'Section 5310 Program Requirements' %}

REPLACE:
{% for assessment in assessments if assessment.review_area == section_5310_name %}

--------
FIND:
{% for assessment in assessments if assessment.review_area == 'Section 5311 Program Requirements' %}

REPLACE:
{% for assessment in assessments if assessment.review_area == section_5311_name %}
""")

print("\n✓ This should resolve the XML splitting issue")
