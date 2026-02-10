#!/usr/bin/env python3
"""Show string concatenation fix for Section numbers"""

print("="*80)
print("STRING CONCATENATION FIX")
print("="*80)

print("""
The issue persists even in {% set %} statements because Word breaks the XML.

SOLUTION: Build the strings using concatenation with quoted numbers:

Instead of:
{% set section_5307_name = 'Section 5307 Program Requirements' %}

Use string concatenation:
{% set section_5307_name = 'Section ' + '5307' + ' Program Requirements' %}

The key is that '5307' is explicitly in quotes, so it's a string, not an integer.
""")

print("\n" + "="*80)
print("REPLACE YOUR {% set %} STATEMENTS")
print("="*80)

print("""
FIND:
{% set section_5307_name = 'Section 5307 Program Requirements' %}

REPLACE:
{% set section_5307_name = 'Section ' + '5307' + ' Program Requirements' %}

--------

FIND:
{% set section_5310_name = 'Section 5310 Program Requirements' %}

REPLACE:
{% set section_5310_name = 'Section ' + '5310' + ' Program Requirements' %}

--------

FIND:
{% set section_5311_name = 'Section 5311 Program Requirements' %}

REPLACE:
{% set section_5311_name = 'Section ' + '5311' + ' Program Requirements' %}
""")

print("\n" + "="*80)
print("ALTERNATIVE: Skip the variables entirely")
print("="*80)

print("""
If concatenation still doesn't work, use it directly in the comparison:

INSTEAD OF:
{% for assessment in assessments if assessment.review_area == 'Section 5307 Program Requirements' %}

USE:
{% for assessment in assessments if assessment.review_area == 'Section ' + '5307' + ' Program Requirements' %}

This explicitly tells Jinja2 that '5307' is a string that needs to be
concatenated, not an integer token.
""")
