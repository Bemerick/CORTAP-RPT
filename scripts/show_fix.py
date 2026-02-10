#!/usr/bin/env python3
"""Show the fix for Section number syntax errors"""

print("="*80)
print("FIX FOR SECTION NUMBER SYNTAX ERROR")
print("="*80)

print("""
The problem is that Word splits the XML in a way that makes Jinja2
see the number (5307, 5310, 5311) as a separate token.

CURRENT (BROKEN):
{% set area = assessments | selectattr('review_area', '==', 'Section 5307 Program Requirements') | first %}

SOLUTION - Use a loop with string comparison instead:
{% set area = namespace(value=none) %}
{% for assessment in assessments %}
  {% if assessment.review_area == 'Section 5307 Program Requirements' %}
    {% set area.value = assessment %}
  {% endif %}
{% endfor %}

Then use: {{ area.value.finding }} instead of {{ area.finding }}

ALTERNATIVE SOLUTION - Use a simpler filter approach:
{% for assessment in assessments if assessment.review_area == 'Section 5307 Program Requirements' %}
  {% set area = assessment %}
  {% break %}
{% endfor %}

This avoids selectattr entirely and uses a simple loop with a condition.

""")

print("="*80)
print("SEARCH AND REPLACE IN WORD")
print("="*80)

replacements = [
    ("5307", """
FIND:
{% set area = assessments | selectattr('review_area', '==', 'Section 5307 Program Requirements') | first %}

REPLACE WITH:
{% for assessment in assessments if assessment.review_area == 'Section 5307 Program Requirements' %}{% set area = assessment %}{% break %}{% endfor %}
"""),
    ("5310", """
FIND:
{% set area = assessments | selectattr('review_area', '==', 'Section 5310 Program Requirements') | first %}

REPLACE WITH:
{% for assessment in assessments if assessment.review_area == 'Section 5310 Program Requirements' %}{% set area = assessment %}{% break %}{% endfor %}
"""),
    ("5311", """
FIND:
{% set area = assessments | selectattr('review_area', '==', 'Section 5311 Program Requirements') | first %}

REPLACE WITH:
{% for assessment in assessments if assessment.review_area == 'Section 5311 Program Requirements' %}{% set area = assessment %}{% break %}{% endfor %}
"""),
]

for section, replacement in replacements:
    print(f"\nSection {section}:")
    print(replacement)
