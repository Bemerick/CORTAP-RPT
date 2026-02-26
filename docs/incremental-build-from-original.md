# Incremental Template Build - From Original Template

Build the draft report template section by section from the **original Word template**, preserving all formatting and content.

**Strategy:** Work through the document sequentially, converting one section at a time while leaving future sections unchanged.

---

## 🎯 Setup

### 1. Prepare Word Settings (CRITICAL - Do First!)

**Before opening any Word documents:**

1. Open Word → **Preferences** (Mac) or **File → Options** (Windows)
2. Go to **AutoCorrect** → **AutoFormat As You Type**
3. **UNCHECK** these options:
   - ❌ "Straight quotes" with "smart quotes"
   - ❌ Hyphens (--) with dash (—)
   - ❌ Fractions (1/2) with fraction character (½)
   - ❌ Ordinals (1st) with superscript
4. Click **OK**
5. **Restart Word** (important!)

### 2. Copy Original Template

```bash
# Already done:
cp "docs/requirements/State_RO_Recipient# _Recipient Name_FY25_TRSMR_DraftFinalReport.docx" \
   app/templates/draft-report-working.docx
```

**Working template:** `app/templates/draft-report-working.docx`

### 3. Understand the Structure

The template has **7 main sections** with **36 subsections**:

1. **Executive Summary** (header + 2 subsections)
2. **Review Background and Process** (2 subsections)
3. **Recipient Description** (2 subsections)
4. **Results of the Review** (23 assessment areas!)
5. **Attendees** (1 table)
6. **(Empty section)**
7. **Appendices**

**Total:** 606 paragraphs, 4 tables

---

## 📋 Conversion Strategy

### Section-by-Section Workflow

For each section:

1. **Open template** in Word: `open app/templates/draft-report-working.docx`
2. **Find placeholders** (see patterns below)
3. **Replace with Jinja2** (type fresh, don't paste!)
4. **Save & close Word** completely
5. **Test:** `python scripts/test_section.py app/templates/draft-report-working.docx`
6. **Verify output** looks correct
7. **Move to next section**

### Placeholder Patterns to Look For

The original template uses these patterns:

1. **Square brackets:** `[Triennial Review]`, `[Recipient Name]`, `[City, State]`
2. **Descriptive text:** `Month Day, Year`, `Recipient Organization Name`
3. **Fiscal years:** `FY2025`, `FY2022`
4. **Boilerplate choices:** `[Draft/Final]`, `[Mr./Ms.]`

---

## 🔨 Section 1: Cover Letter & Header

**Location:** First page (before "Executive Summary" heading)

**What to Convert:**

### Header (Regional Office info - top of page)
```
Current: INSERT Regional Header
Replace with: {{ project.regional_office_header }}
```

### Date
```
Current: Month Day, Year
Replace with: {{ date_format(project.report_date) }}
```

### Recipient Address Block
```
Current: Name
Replace with: {{ project.recipient_contact_name }}

Current: Title
Replace with: {{ project.recipient_contact_title }}

Current: Recipient Organization Name
Replace with: {{ project.recipient_name }}

Current: Street Address
Replace with: {{ project.recipient_address }}

Current: City, State, Zip
Replace with: {{ project.recipient_city }}, {{ project.recipient_state }}, {{ project.recipient_zip }}
```

### Subject Line
```
Current: Fiscal Year FY2025
Replace with: Fiscal Year FY{{ project.fiscal_year }}

Current: [Triennial Review]/[State Management Review]/[Combined...]
Replace with: {{ project.review_type }}

Current: [Draft/Final]
Replace with: {{ project.report_status }}
```

### Letter Salutation
```
Current: Mr./Ms. [Last Name]
Replace with: {{ project.recipient_salutation }} {{ project.recipient_last_name }}
```

### Letter Body - Multiple Occurrences

Throughout the letter, replace ALL instances of:

```
[Triennial Review]/[State Management Review]/[Combined...]
→ {{ project.review_type }}

[Recipient name]
→ {{ project.recipient_name }}

[Recipient Acronym]
→ {{ project.recipient_acronym }}

[City, State]
→ {{ project.recipient_city }}, {{ project.recipient_state }}

[draft/final]
→ {{ project.report_status | lower }}
```

**💡 Tip:** Use Find & Replace in Word:
- Find: `[Recipient Acronym]`
- Replace with: `{{ project.recipient_acronym }}`
- Click **Replace All**

### Test Section 1

```bash
# Save and close Word first!
python scripts/test_section.py app/templates/draft-report-working.docx
```

**Expected:** ✅ Cover letter renders with correct recipient info

**Verify output:**
```bash
open output/incremental/draft-report-working_test.docx
```

Check that:
- Header has regional office info
- Date is formatted correctly
- Recipient address is complete
- Review type appears (not choices like "[TR]/[SMR]")
- Letter flows naturally

---

## 📊 Section 2: Executive Summary

**Location:** After cover letter, starts with "Executive Summary" heading

### 2.1: Metric Section

**Find the table** under "Metric" heading.

**Replace:**

```
Current: [Recipient Acronym] (in multiple cells)
Replace with: {{ project.recipient_acronym }}

Current: FY2025
Replace with: FY{{ project.fiscal_year }}

Current: April 11, 2024 (review start date)
Replace with: {{ date_format(project.review_start_date) }}

Current: May 13, 2024 (review end date)
Replace with: {{ date_format(project.review_end_date) }}
```

### 2.2: Summary of Findings

**Conditional rendering** - this section changes based on whether there are deficiencies.

#### If NO deficiencies:

**Find:** The paragraph that says "The review resulted in no findings..."

**Wrap with:**
```jinja2
{% if not metadata.has_deficiencies %}
[existing paragraph text]
{% endif %}
```

#### If HAS deficiencies:

**Find:** The paragraph that starts "The review identified..."

**Wrap with:**
```jinja2
{% if metadata.has_deficiencies %}
[existing paragraph text]
{% endif %}
```

**Replace within this paragraph:**
```
Current: [#] deficiencies
Replace with: {{ metadata.deficiency_count }} {{ 'deficiency' if metadata.deficiency_count == 1 else 'deficiencies' }}

Current: [list of areas]
Replace with: {{ metadata.deficiency_areas }}
```

**Find:** The list of ERF areas (if exists)

**Wrap with:**
```jinja2
{% if metadata.erf_count %}
The {{ metadata.erf_count }} {{ 'area' if metadata.erf_count == 1 else 'areas' }} requiring ERFs {{ 'is' if metadata.erf_count == 1 else 'are' }}: {{ metadata.erf_areas }}.
{% endif %}
```

### Test Section 2

```bash
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json
```

**Expected:** ✅ Summary shows deficiencies (GPTD has 3)

**Also test with no deficiencies:**
```bash
# NTD has only 1 minor deficiency, might show different text
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
```

---

## 🔍 Section 3: Review Background and Process

**Location:** After Executive Summary

### 3.1: Review Background

**Replace throughout:**
```
[Recipient Acronym]
→ {{ project.recipient_acronym }}

FY2025 / FY 2025
→ FY{{ project.fiscal_year }}

[Triennial Review]
→ {{ project.review_type }}
```

### 3.2: Process

**Find:** Exit conference format paragraph

**Conditional - Virtual:**
```jinja2
{% if project.exit_conference_format == 'virtual' %}
The exit conference was held virtually on {{ date_format(project.exit_conference_date) }}.
{% endif %}
```

**Conditional - In-Person:**
```jinja2
{% if project.exit_conference_format == 'in-person' %}
The in-person exit conference was held on {{ date_format(project.exit_conference_date) }} at [location].
{% endif %}
```

### Test Section 3

```bash
python scripts/test_section.py app/templates/draft-report-working.docx
```

---

## 🏢 Section 4: Recipient Description

**Location:** After Review Background

### Replace throughout:
```
[Recipient Name]
→ {{ project.recipient_name }}

[Recipient Acronym]
→ {{ project.recipient_acronym }}

[City, State]
→ {{ project.recipient_city }}, {{ project.recipient_state }}

FY2025
→ FY{{ project.fiscal_year }}
```

**Award information** (if dynamic):
```
Current: Section 5307 formula funds
Replace with: {% if project.has_5307 %}Section 5307 formula funds{% endif %}

(Similar for 5310, 5311, etc.)
```

### Test Section 4

```bash
python scripts/test_section.py app/templates/draft-report-working.docx
```

---

## 🎯 Section 5: Results of the Review (THE BIG ONE!)

**Location:** After Recipient Description - this contains all 23 assessment areas

**Strategy:** Convert 2-3 areas at a time, test after each batch.

### Pattern for Each Assessment Area

Each area follows this structure:

```
Heading: [Area Name] (e.g., "Legal", "Financial Management and Capacity")

Paragraph 1: Intro text

Conditional section based on finding:
  - If finding == "D" (Deficiency): Show deficiency details
  - If finding == "ND" (No Deficiency): Show standard text
  - If finding == "NA" (Not Applicable): Show N/A text
```

### Template Pattern for ONE Area

**Example: Legal**

#### Step 1: Add set variable (BEFORE the "Legal" heading)

```jinja2
{% set area = assessments | selectattr('review_area', '==', 'Legal') | first %}
```

#### Step 2: Conditional wrapper (wrap entire area section)

```jinja2
{% if area %}
[entire Legal section content]
{% endif %}
```

#### Step 3: Finding conditional (within the area)

```jinja2
{% if area.finding == 'D' %}
[Deficiency content - KEEP existing text]

Deficiency: {{ area.deficiency_code }}

Corrective Action: {{ area.corrective_action }}

{% if area.date_closed %}
Date Closed: {{ date_format(area.date_closed) }}
{% else %}
Due Date: {{ date_format(area.due_date) }}
{% endif %}

{% elif area.finding == 'ND' %}
[No deficiency content - KEEP existing text]

{% elif area.finding == 'NA' %}
[Not applicable content - KEEP existing text]

{% endif %}
```

### Batch 1: First 3 Areas (Start Here!)

Convert these areas:
1. **Legal**
2. **Financial Management and Capacity**
3. **Organizational Management** (if it exists, or pick the first 3 you see)

**After converting each area**, test:
```bash
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json
```

### Batch 2-8: Remaining 20 Areas

Continue in batches of 2-3 areas:
- Technical Capacity – Award Management
- Technical Capacity – Program Management & Subrecipient Oversight
- Technical Capacity – Project Management
- Transit Asset Management
- Satisfactory Continuing Control
- Maintenance
- Procurement
- Disadvantaged Business Enterprise (DBE)
- Title VI
- Americans with Disabilities Act (ADA) – General
- ADA – Complementary Paratransit
- Equal Employment Opportunity (EEO)
- School Bus
- Charter Bus
- Drug Free Workplace Act
- Drug and Alcohol Program
- Section 5307 Program Requirements
- Section 5310 Program Requirements
- Section 5311 Program Requirements
- Public Transportation Agency Safety Plan (PTASP)
- Cybersecurity

**Test after EVERY 2-3 areas!**

### Special: Section 5307/5310/5311 Areas

These have special string concatenation to avoid Word fragmentation:

```jinja2
{% set section_5307_name = 'Section ' + '5307' + ' Program Requirements' %}
{% set section_5310_name = 'Section ' + '5310' + ' Program Requirements' %}
{% set section_5311_name = 'Section ' + '5311' + ' Program Requirements' %}

{% set area = assessments | selectattr('review_area', '==', section_5307_name) | first %}
```

---

## 👥 Section 6: Attendees

**Location:** After Results section

**Simple replacements:**

```
[Recipient Acronym]
→ {{ project.recipient_acronym }}
```

**Team member loop** (in the table):

```jinja2
{% for contractor in review_team %}
{{ contractor.name }}
{{ contractor.role }}
{% endfor %}
```

### Test Section 6

```bash
python scripts/test_section.py app/templates/draft-report-working.docx
```

---

## 📎 Section 7: Appendices

**Leave as-is** (typically static content)

Or replace any dynamic references:
```
[Recipient Acronym]
→ {{ project.recipient_acronym }}
```

---

## ✅ Final Validation

### Test All 5 Mock Files

```bash
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/MEVA_FY2023_TR.json
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/Nashua_FY2023_TR.json
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/DRPA_FY2023_TR.json
```

**All 5 should pass!**

### Post-Processing

```bash
# Fix any smart quotes that crept in
python scripts/fix_smart_quotes.py app/templates/draft-report-working.docx

# Fix any split == operators
python scripts/merge_split_equals.py app/templates/draft-report-working.docx

# Final test
python scripts/test_section.py app/templates/draft-report-working.docx
```

### Promote to Production

```bash
# Backup current
mv app/templates/draft-audit-report-poc.docx app/templates/draft-audit-report-poc-old.docx

# Promote working template
cp app/templates/draft-report-working.docx app/templates/draft-audit-report-poc.docx

# Verify
python scripts/quick_test.py
```

---

## 💡 Tips for Success

### 1. Work Slowly & Test Often
- Convert 1-2 expressions
- Save, close Word
- Test
- Check output
- Continue

### 2. Type, Never Paste
- Always type Jinja2 fresh
- Pasting can introduce hidden XML

### 3. Watch for Smart Quotes
- If you see `'` or `"` instead of `'` or `"`
- Word settings aren't saved
- Recheck settings, restart Word

### 4. Use Find & Replace
- Word's Find & Replace works well for simple replacements
- Find: `[Recipient Acronym]`
- Replace: `{{ project.recipient_acronym }}`

### 5. Keep Original Content
- Don't delete existing text unless it's a placeholder
- The original formatting is preserved by keeping structure

### 6. Test with Different Data
- GPTD has deficiencies
- NTD has minimal deficiencies
- MEVA has many deficiencies
- Use different test files to verify conditionals work

---

## 📝 Progress Tracking

Update: `.bmad-ephemeral/incremental-build-progress.md`

Check off each section as you complete it:
- [ ] Section 1: Cover Letter & Header
- [ ] Section 2: Executive Summary
- [ ] Section 3: Review Background
- [ ] Section 4: Recipient Description
- [ ] Section 5.1: Assessment Areas (first 3)
- [ ] Section 5.2: Assessment Areas (next 3)
- [ ] ... (continue)
- [ ] Section 6: Attendees
- [ ] Section 7: Appendices
- [ ] Final validation (all 5 test files)

---

## 🐛 Troubleshooting

See: `docs/quick-reference-incremental-build.md`

**Common issues:**
- Smart quotes appeared → Check Word settings
- XML fragmentation → Delete & retype expression
- Test fails → Check previous section still works
- Output wrong → Verify test data has required fields

---

## 🎉 Completion

When all tests pass:
1. ✅ All 7 sections converted
2. ✅ All 5 test files render successfully
3. ✅ Formatting preserved
4. ✅ Ready for Story 1.5.6!
