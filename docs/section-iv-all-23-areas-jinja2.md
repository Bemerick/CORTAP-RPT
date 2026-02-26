# Section IV - All 23 Review Areas (Jinja2 Format)

Copy this entire section into your Word template for Section IV.

---

```jinja2
IV.    Results of the Review

1.    Legal

Basic Requirement: The recipient must promptly notify the FTA of legal matters and additionally notify the USDOT Office of Inspector General (OIG) of any instances relating to false claims under the False Claims Act or fraud. Recipients must comply with restrictions on lobbying requirements.

{% set area = assessments | selectattr('review_area', 'equalto', 'Legal') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Legal.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Legal.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

2.    Financial Management and Capacity

Basic Requirement: The recipient must have financial policies and procedures; an organizational structure that defines, assigns, and delegates fiduciary authority; and financial management systems in place to manage, match, and charge only allowable costs to the award. The recipient must conduct required Single Audits, as required by 2 CFR part 200, and provide financial oversight of subrecipients.

{% set area = assessments | selectattr('review_area', 'equalto', 'Financial Management and Capacity') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Financial Management and Capacity.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Financial Management and Capacity.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

3.    Technical Capacity – Award Management

Basic Requirement: The recipient must demonstrate the capability to manage and administer FTA awards in accordance with federal requirements, including proper closeout procedures, timely drawdown of funds, and maintenance of accurate records.

{% set area = assessments | selectattr('review_area', 'equalto', 'Technical Capacity – Award Management') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Technical Capacity – Award Management.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Technical Capacity – Award Management.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

4.    Technical Capacity – Program Management & Subrecipient Oversight

Basic Requirement: The recipient must demonstrate the capability to manage FTA programs and oversee subrecipients in accordance with federal requirements, including proper monitoring, reporting, and technical assistance.

{% set area = assessments | selectattr('review_area', 'equalto', 'Technical Capacity – Program Management & Subrecipient Oversight') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Technical Capacity – Program Management & Subrecipient Oversight.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Technical Capacity – Program Management & Subrecipient Oversight.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

5.    Technical Capacity – Project Management

Basic Requirement: The recipient must demonstrate the capability to manage capital and planning projects in accordance with federal requirements, including proper project oversight, change management, and adherence to project schedules and budgets.

{% set area = assessments | selectattr('review_area', 'equalto', 'Technical Capacity – Project Management') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Technical Capacity – Project Management.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Technical Capacity – Project Management.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

6.    Transit Asset Management

Basic Requirement: The recipient must develop and implement a Transit Asset Management (TAM) plan that includes an inventory of capital assets, condition assessments, decision support tools, and investment prioritization.

{% set area = assessments | selectattr('review_area', 'equalto', 'Transit Asset Management') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Transit Asset Management.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Transit Asset Management.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

7.    Satisfactory Continuing Control

Basic Requirement: The recipient must maintain satisfactory continuing control over FTA-funded equipment and facilities, including proper inventory management, disposition procedures, and maintenance of use records.

{% set area = assessments | selectattr('review_area', 'equalto', 'Satisfactory Continuing Control') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Satisfactory Continuing Control.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Satisfactory Continuing Control.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

8.    Maintenance

Basic Requirement: The recipient must maintain FTA-funded equipment and facilities in good operating condition in accordance with the recipient's maintenance plan and industry standards.

{% set area = assessments | selectattr('review_area', 'equalto', 'Maintenance') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Maintenance.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Maintenance.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

9.    Procurement

Basic Requirement: The recipient must conduct procurements in accordance with 2 CFR part 200 and FTA requirements, including competition, proper solicitation procedures, cost and price analysis, and inclusion of required clauses.

{% set area = assessments | selectattr('review_area', 'equalto', 'Procurement') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Procurement.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Procurement.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

10.    Disadvantaged Business Enterprise (DBE)

Basic Requirement: The recipient must implement a DBE program in accordance with 49 CFR Part 26, including setting goals, maintaining a DBE directory, monitoring and reporting DBE participation, and ensuring prompt payment to DBE contractors.

{% set area = assessments | selectattr('review_area', 'equalto', 'Disadvantaged Business Enterprise (DBE)') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Disadvantaged Business Enterprise.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Disadvantaged Business Enterprise.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

11.    Title VI

Basic Requirement: The recipient must ensure that no person is excluded from participation in, denied benefits of, or subjected to discrimination under any FTA-funded program on the basis of race, color, or national origin, in accordance with Title VI of the Civil Rights Act of 1964.

{% set area = assessments | selectattr('review_area', 'equalto', 'Title VI') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Title VI.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Title VI.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

12.    Americans with Disabilities Act (ADA) – General

Basic Requirement: The recipient must comply with the Americans with Disabilities Act of 1990 and 49 CFR Part 37, ensuring that facilities and services are accessible to individuals with disabilities.

{% set area = assessments | selectattr('review_area', 'equalto', 'Americans with Disabilities Act (ADA) – General') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Americans with Disabilities Act (ADA) – General.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Americans with Disabilities Act (ADA) – General.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

13.    ADA – Complementary Paratransit

Basic Requirement: The recipient must provide complementary paratransit service that is comparable to fixed-route service for individuals with disabilities who are unable to use the fixed-route system, in accordance with 49 CFR Part 37.

{% set area = assessments | selectattr('review_area', 'equalto', 'ADA – Complementary Paratransit') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for ADA – Complementary Paratransit.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for ADA – Complementary Paratransit.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

14.    Equal Employment Opportunity

Basic Requirement: The recipient must have an Equal Employment Opportunity (EEO) program that complies with applicable federal requirements, including non-discrimination in hiring and employment practices.

{% set area = assessments | selectattr('review_area', 'equalto', 'Equal Employment Opportunity') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Equal Employment Opportunity.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Equal Employment Opportunity.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

15.    School Bus

Basic Requirement: The recipient must comply with 49 USC 5323(f) and FTA regulations regarding the prohibition on providing school bus service, except under specific allowable circumstances.

{% set area = assessments | selectattr('review_area', 'equalto', 'School Bus') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for School Bus.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for School Bus.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

16.    Charter Bus

Basic Requirement: The recipient must comply with 49 USC 5323(d) and FTA regulations regarding the prohibition on providing charter bus service, except under specific allowable circumstances.

{% set area = assessments | selectattr('review_area', 'equalto', 'Charter Bus') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Charter Bus.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Charter Bus.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

17.    Drug Free Workplace Act

Basic Requirement: The recipient must comply with the Drug-Free Workplace Act of 1988, maintaining a drug-free workplace and implementing appropriate policies and procedures.

{% set area = assessments | selectattr('review_area', 'equalto', 'Drug Free Workplace Act') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Drug Free Workplace Act.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Drug Free Workplace Act.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

18.    Drug and Alcohol Program

Basic Requirement: The recipient must implement a drug and alcohol testing program in accordance with 49 CFR Part 655, including pre-employment, random, reasonable suspicion, post-accident, return-to-duty, and follow-up testing.

{% set area = assessments | selectattr('review_area', 'equalto', 'Drug and Alcohol Program') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Drug and Alcohol Program.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Drug and Alcohol Program.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

19.    Section 5307 Program Requirements

Basic Requirement: The recipient must comply with specific requirements for the Section 5307 Urbanized Area Formula Program, including planning, coordination, and reporting requirements.

{% set area = assessments | selectattr('review_area', 'equalto', 'Section 5307 Program Requirements') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Section 5307 Program Requirements.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Section 5307 Program Requirements.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

20.    Section 5310 Program Requirements

Basic Requirement: The recipient must comply with specific requirements for the Section 5310 Enhanced Mobility of Seniors and Individuals with Disabilities Program, including coordination with other transportation providers and appropriate project selection.

{% set area = assessments | selectattr('review_area', 'equalto', 'Section 5310 Program Requirements') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Section 5310 Program Requirements.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Section 5310 Program Requirements.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

21.    Section 5311 Program Requirements

Basic Requirement: The recipient must comply with specific requirements for the Section 5311 Formula Grants for Rural Areas Program, including planning, coordination with rural stakeholders, and appropriate fund distribution.

{% set area = assessments | selectattr('review_area', 'equalto', 'Section 5311 Program Requirements') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Section 5311 Program Requirements.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Section 5311 Program Requirements.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

22.    Public Transportation Agency Safety Plan (PTASP)

Basic Requirement: The recipient must develop, implement, and maintain a Public Transportation Agency Safety Plan in accordance with 49 CFR Part 673, including safety performance targets, safety management policies, and safety risk management processes.

{% set area = assessments | selectattr('review_area', 'equalto', 'Public Transportation Agency Safety Plan (PTASP)') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Public Transportation Agency Safety Plan.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Public Transportation Agency Safety Plan.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}

23.    Cybersecurity

Basic Requirement: The recipient must implement appropriate cybersecurity measures to protect FTA-funded systems and data from cyber threats, in accordance with FTA guidance and industry best practices.

{% set area = assessments | selectattr('review_area', 'equalto', 'Cybersecurity') | first %}
{%p if area.finding == "D" %}
Finding: {{ (area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1 }} deficienc{{ 'y was' if ((area.deficiency_code.split(',') | length) if area.deficiency_code and ',' in area.deficiency_code else 1) == 1 else 'ies were' }} found with the FTA requirements for Cybersecurity.

Deficiency Code(s): {{ area.deficiency_code }}

Deficiency Description: {{ area.description }}

Corrective Action(s) and Schedule: {{ area.corrective_action }}{% if area.due_date %} Due date: {{ area.due_date | date_format }}.{% endif %}{% if area.date_closed %} Date closed: {{ area.date_closed | date_format }}.{% endif %}
{%p elif area.finding == "ND" %}
Finding: During this {{ project.review_type }} of {{ project.recipient_acronym }}, no deficiencies were found with the FTA requirements for Cybersecurity.
{%p elif area.finding == "NA" %}
Finding: Not applicable.
{%p endif %}
```

---

## Notes

1. **Copy the entire section above** into your Word template starting at "IV. Results of the Review"

2. **Area names match exactly** what's in your JSON files (including special characters like "–" and "(DBE)")

3. **Basic requirements are generic but appropriate** - you can edit them in the Word template if you have the actual text from FTA guidelines

4. **All 23 areas follow the same pattern** for consistency

5. **Handles multiple deficiency codes** by counting commas and adjusting grammar

6. **Test with validation script** after pasting into Word:
   ```bash
   python scripts/validate_draft_template.py --render
   ```
