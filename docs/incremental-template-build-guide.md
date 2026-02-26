# Incremental Template Build Guide

Build the draft report template section by section, testing after each addition.

## Setup

### 1. Prepare Word Settings

**CRITICAL:** Before opening Word, configure these settings:

1. Open Word → Preferences (Mac) or File → Options (Windows)
2. Go to **AutoCorrect** → **AutoFormat As You Type**
3. **UNCHECK** these options:
   - ✅ "Straight quotes" with "smart quotes"
   - ✅ Hyphens (--) with dash (—)
   - ✅ Fractions (1/2) with fraction character (½)
4. Click OK and **restart Word**

### 2. Create Clean Template

```bash
# Extract clean template (no Jinja2) from original
python scripts/create_clean_template.py app/templates/draft-audit-report-poc_backup.docx app/templates/draft-report-incremental.docx
```

This creates `draft-report-incremental.docx` with all Jinja2 removed (replaced with [PLACEHOLDER]).

### 3. Open Template

```bash
open app/templates/draft-report-incremental.docx
```

---

## Section-by-Section Build

### Section 1: Header & Metadata

**Location:** Top of document (before main content)

**Jinja2 to add:**

1. Find: `[PLACEHOLDER]` for fiscal year
   - Replace with: `{{ project.fiscal_year }}`

2. Find: `[PLACEHOLDER]` for recipient name
   - Replace with: `{{ project.recipient_name }}`

3. Find: `[PLACEHOLDER]` for recipient acronym
   - Replace with: `{{ project.recipient_acronym }}`

4. Find: `[PLACEHOLDER]` for review type
   - Replace with: `{{ project.review_type }}`

5. Find: `[PLACEHOLDER]` for report date
   - Replace with: `{{ date_format(project.report_date) }}`

**Test:**
```bash
# Save and close Word
python scripts/test_section.py app/templates/draft-report-incremental.docx
```

**Expected:** ✅ All tests pass, output shows correct header data

---

### Section 2: Executive Summary

**Location:** After header, before detailed sections

**Jinja2 to add:**

1. Find: `[PLACEHOLDER]` for deficiency count
   - Replace with: `{{ metadata.deficiency_count }}`

2. Find: `[PLACEHOLDER]` for deficiency areas
   - Replace with: `{{ metadata.deficiency_areas }}`

3. Find: Conditional for "no deficiencies" message
   - Add: `{% if not metadata.has_deficiencies %}`
   - (around the "no deficiencies found" paragraph)
   - Add: `{% endif %}`

4. Find: Conditional for "has deficiencies" message
   - Add: `{% if metadata.has_deficiencies %}`
   - (around the deficiency summary paragraph)
   - Add: `{% endif %}`

**Test:**
```bash
python scripts/test_section.py app/templates/draft-report-incremental.docx
```

**Expected:** ✅ All tests pass, executive summary shows/hides correctly

---

### Section 3: Review Type Routing

**Location:** Main body - routes to TR vs CR content

**Jinja2 to add:**

1. Find: Start of Triennial Review section
   - Add BEFORE: `{% if project.review_type == 'Triennial Review' %}`

2. Find: End of Triennial Review section
   - Add AFTER: `{% endif %}`

3. Find: Start of Compliance Review section
   - Add BEFORE: `{% if project.review_type == 'Compliance Review' %}`

4. Find: End of Compliance Review section
   - Add AFTER: `{% endif %}`

**Test:**
```bash
# Test with TR data
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/NTD_FY2023_TR.json

# Test with CR data (when available)
# python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/CR_test.json
```

**Expected:** ✅ Only TR section appears (CR section hidden)

---

### Section 4: Deficiency Sections

**Location:** Within TR/CR sections

**Jinja2 to add (for each deficiency block):**

1. **ERF Section Loop**
   - Find: Start of ERF deficiency table
   - Add BEFORE: `{% if metadata.erf_count %}`
   - Add AFTER table: `{% endif %}`

2. **ERF Count Expressions**
   - Find: `[PLACEHOLDER]` for ERF count
   - Replace with: `{{ metadata.erf_count }}`

3. **ERF Area Names**
   - Find: `[PLACEHOLDER]` for ERF areas
   - Replace with: `{{ metadata.erf_areas }}`

4. **Grammar Helpers** (plural/singular)
   - "area" vs "areas": `{{ 's' if metadata.erf_count != 1 else '' }}`
   - "is" vs "are": `{{ 'are' if metadata.erf_count != 1 else 'is' }}`

5. **Repeat Deficiencies Section**
   - Find: Repeat deficiencies paragraph
   - Wrap with: `{% if not metadata.no_repeat_deficiencies %}` ... `{% endif %}`

**Test:**
```bash
# Test with deficiency data (GPTD has 3 deficiencies)
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json

# Test without deficiencies (NTD has 1)
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
```

**Expected:** ✅ Deficiency sections show/hide based on data

---

### Section 5: Assessment Areas (All 23)

**Location:** Detailed findings section

**This is the most complex section - add ONE area at a time!**

#### 5.1: First Area (e.g., "Legal")

1. Find the **Legal** assessment area section

2. **Add set variable** (BEFORE the section):
   ```jinja2
   {% set area = assessments | selectattr('review_area', '==', 'Legal') | first %}
   ```

3. **Wrap section in conditional**:
   - Add BEFORE section: `{% if area %}`
   - Add AFTER section: `{% endif %}`

4. **Add finding conditional** (within the area):
   ```jinja2
   {% if area.finding == 'D' %}
   [Deficiency content]
   {% elif area.finding == 'ND' %}
   [No deficiency content]
   {% elif area.finding == 'NA' %}
   [Not applicable content]
   {% endif %}`
   ```

5. **Add deficiency details** (within D section):
   - `{{ area.deficiency_code }}`
   - `{{ area.corrective_action }}`
   - `{{ date_format(area.date_closed) }}`  (if closed)
   - `{{ date_format(area.due_date) }}`  (if open)

**Test after EACH area:**
```bash
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json
```

#### 5.2-5.23: Remaining Areas

Repeat the pattern for each of the 23 areas:
- Financial Management and Capacity
- Organizational Management
- Technical Capacity
- … (all 23)

**Critical:** Test after adding each 2-3 areas. Don't add all 23 at once!

---

### Section 6: Subrecipient Monitoring

**Location:** After assessment areas (if applicable)

**Jinja2 to add:**

1. **Section 5307 block**:
   ```jinja2
   {% if subrecipient.reviewed and subrecipient.program_section == '5' + '307' %}
   Section 5307 content
   {% endif %}
   ```

2. **Section 5310 block**:
   ```jinja2
   {% elif subrecipient.reviewed and subrecipient.program_section == '5' + '310' %}
   Section 5310 content
   ```

3. **Section 5311 block**:
   ```jinja2
   {% elif subrecipient.reviewed and subrecipient.program_section == '5' + '311' %}
   Section 5311 content
   {% endif %}
   ```

**Note:** Use `'5' + '307'` instead of `'5307'` to avoid Word fragmentation issues.

**Test:**
```bash
# Test with subrecipient data
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json
```

---

### Section 7: Exit Conference & Signatures

**Location:** End of document

**Jinja2 to add:**

1. **Exit conference format routing**:
   ```jinja2
   {% if project.exit_conference_format == 'virtual' %}
   Virtual exit conference content
   {% elif project.exit_conference_format == 'in-person' %}
   In-person exit conference content
   {% endif %}
   ```

2. **Exit date**:
   - Replace with: `{{ date_format(assessment.date_closed) }}`

3. **Team member loop**:
   ```jinja2
   {% for contractor in review_team %}
   {{ contractor.name }}
   {% endfor %}
   ```

**Test:**
```bash
python scripts/test_section.py app/templates/draft-report-incremental.docx
```

---

## Final Validation

### Test All 5 Mock Files

```bash
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/MEVA_FY2023_TR.json
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/Nashua_FY2023_TR.json
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/DRPA_FY2023_TR.json
```

**Expected:** ✅ All 5 tests pass

### Apply Post-Processing

Once all sections work, run cleanup scripts:

```bash
# Fix any smart quotes that crept in
python scripts/fix_smart_quotes.py app/templates/draft-report-incremental.docx

# Fix any split == operators
python scripts/merge_split_equals.py app/templates/draft-report-incremental.docx

# Final test
python scripts/test_section.py app/templates/draft-report-incremental.docx
```

### Promote to Production

```bash
# Backup current template
mv app/templates/draft-audit-report-poc.docx app/templates/draft-audit-report-poc-old.docx

# Promote incremental template
cp app/templates/draft-report-incremental.docx app/templates/draft-audit-report-poc.docx
```

---

## Tips for Success

### 1. Type, Don't Paste
- **ALWAYS** type Jinja2 fresh in Word
- **NEVER** copy-paste Jinja2 from other documents
- Pasting can introduce hidden formatting/XML

### 2. Test Frequently
- Test after adding 1-2 expressions
- Don't add 20 expressions then test
- Easier to find problems when you test often

### 3. Save & Close Word Before Testing
- Word caches changes
- Close Word completely before running test script
- Reopen to add more

### 4. Watch for Smart Quotes
- If you see `'` or `"` (curly quotes) instead of `'` or `"`
- Check Word settings again
- Run `fix_smart_quotes.py` to clean up

### 5. Use Simple Comparisons
- Prefer: `!= 1` over `> 1`
- Prefer: `== 'value'` over `!= 'other'`
- Avoid `<` and `>` (can become HTML entities)

### 6. Keep Expressions Simple
- Split complex logic into multiple `{% set %}` statements
- Use descriptive variable names
- Comment with Word comments if needed

### 7. Track Progress
Update `.bmad-ephemeral/story-1.5.5-incremental-progress.md` after each section:
```markdown
- [x] Section 1: Header
- [x] Section 2: Executive Summary
- [ ] Section 3: Review Type Routing (in progress)
...
```

---

## Troubleshooting

### Test fails with "unexpected '<'"
- Word inserted XML into your Jinja2
- Find the expression in Word
- **Delete it completely**
- **Retype it fresh** (don't paste!)

### Test fails with "unknown tag"
- Missing opening delimiter ({{ or {%)
- Check for typos in delimiters
- Verify all blocks are complete

### Rendering looks wrong
- Check the generated output in `output/incremental/`
- Verify your test data has the fields you're using
- Check conditional logic (if/elif/endif)

### "Got 'integer'" error
- Usually a year or number adjacent to Jinja2
- Add extra space: `FY2025 {{` → `FY2025  {{`
- Or use variable: `FY{{ project.fiscal_year }} {{`

---

## Next Steps After Completion

1. ✅ All 5 test files render successfully
2. Move to **Story 1.5.6**: Full POC generation script
3. Generate all 5 reports in batch
4. Systematic validation of all 9 conditional patterns
