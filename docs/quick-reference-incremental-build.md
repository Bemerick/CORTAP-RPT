# Quick Reference - Incremental Build

## 🔧 Setup (Do Once)

**1. Turn OFF Smart Quotes in Word:**
- Mac: Word → Preferences → AutoCorrect → AutoFormat As You Type
- Windows: File → Options → Proofing → AutoCorrect Options → AutoFormat As You Type
- UNCHECK: "Straight quotes" with "smart quotes"
- UNCHECK: Hyphens with dash
- **Restart Word**

**2. Open Clean Template:**
```bash
open app/templates/draft-report-incremental.docx
```

---

## 🎯 Workflow (Repeat for Each Section)

### Step 1: Add Jinja2 in Word
- Find `[PLACEHOLDER]` text
- **Delete it completely**
- **Type** the Jinja2 expression (don't paste!)
- Use regular quotes: `'` and `"` (not curly quotes)

### Step 2: Save & Close Word
- **Save** the document
- **Close Word completely** (don't just close the window)
- Word caches changes - must close to flush

### Step 3: Test
```bash
python scripts/test_section.py app/templates/draft-report-incremental.docx
```

### Step 4: Check Results
- ✅ **PASS** → Open output and verify, then continue to next section
- ❌ **FAIL** → Debug (see troubleshooting below), fix in Word, repeat

---

## 📝 Common Jinja2 Patterns

### Simple Variable
```jinja2
{{ project.recipient_name }}
```

### Function Call
```jinja2
{{ date_format(project.report_date) }}
```

### Conditional Block
```jinja2
{% if metadata.has_deficiencies %}
This shows when there are deficiencies
{% endif %}
```

### If-Elif-Else
```jinja2
{% if area.finding == 'D' %}
Deficiency content
{% elif area.finding == 'ND' %}
No deficiency content
{% else %}
Not applicable content
{% endif %}
```

### Loop
```jinja2
{% for contractor in review_team %}
{{ contractor.name }}
{% endfor %}
```

### Set Variable
```jinja2
{% set area = assessments | selectattr('review_area', '==', 'Legal') | first %}
```

### Grammar Helper (Plurals)
```jinja2
area{{ 's' if metadata.erf_count != 1 else '' }}
```
- 1 area → "area"
- 2+ areas → "areas"

---

## ⚠️ Critical Rules

### ✅ DO
- **Type** Jinja2 fresh in Word
- **Close Word** completely before testing
- **Test after** every 2-3 expressions
- Use `'5' + '307'` for section numbers (not `'5307'`)
- Use `!= 1` instead of `> 1` for comparisons
- Keep expressions **on one line** in Word

### ❌ DON'T
- Don't **copy-paste** Jinja2 from other docs
- Don't use **curly quotes** (' ' " ") - only straight quotes (' ")
- Don't use **en-dash** (–) or **em-dash** (—) - only hyphen (-)
- Don't add 20+ expressions without testing
- Don't forget to **close Word** before testing

---

## 🐛 Troubleshooting

### Error: "unexpected '<'"
**Cause:** Word inserted XML into your Jinja2
**Fix:**
1. Find the expression in Word
2. **Delete the entire expression**
3. **Retype it fresh** (don't paste!)
4. Save, close Word, test again

### Error: "unknown tag 'metadata'"
**Cause:** Missing opening delimiter ({{ or {%)
**Fix:**
1. Check for typos in delimiters
2. Make sure you have `{{` not `{`
3. Verify all blocks are complete

### Error: "got 'integer'"
**Cause:** Year or number adjacent to Jinja2
**Fix:**
- Add extra space: `FY2025 {{` → `FY2025  {{` (two spaces)
- Or use variable: `FY{{ project.fiscal_year }} {{`

### Test passes but output looks wrong
**Check:**
1. Open `output/incremental/draft-report-incremental_test.docx`
2. Verify test data has the fields you're using
3. Check conditional logic (if/elif/endif)
4. Try different test file: `python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json`

### Smart quotes appeared
**Fix:**
1. Check Word settings again (should be OFF)
2. Run: `python scripts/fix_smart_quotes.py app/templates/draft-report-incremental.docx`
3. Close and reopen Word
4. Test again

---

## 📊 Test Commands

### Basic Test (NTD data - 1 deficiency)
```bash
python scripts/test_section.py app/templates/draft-report-incremental.docx
```

### Test with Different Data Files
```bash
# GPTD - 3 deficiencies, has subrecipient
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json

# MEVA - 8 deficiencies, repeat tracking
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/MEVA_FY2023_TR.json

# Nashua - 1 deficiency, clean operational
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/Nashua_FY2023_TR.json

# DRPA - 4 deficiencies, rail system
python scripts/test_section.py app/templates/draft-report-incremental.docx tests/fixtures/mock-data/DRPA_FY2023_TR.json
```

### View Output
```bash
open output/incremental/draft-report-incremental_test.docx
```

---

## 🎓 Section-by-Section Guide

See full guide: `docs/incremental-template-build-guide.md`

**Section order:**
1. Header & Metadata (5 expressions)
2. Executive Summary (4 blocks)
3. Review Type Routing (2 conditionals)
4. Deficiency Sections (~10 blocks)
5. Assessment Areas (23 areas - do 2-3 at a time!)
6. Subrecipient Monitoring (3 conditionals)
7. Exit Conference & Signatures (3 blocks)

**Progress tracker:** `.bmad-ephemeral/incremental-build-progress.md`

---

## 🏁 When Finished

### Final Validation
```bash
# Test all 5 files
for file in tests/fixtures/mock-data/*.json; do
  echo "Testing: $file"
  python scripts/test_section.py app/templates/draft-report-incremental.docx "$file"
done
```

### Post-Processing
```bash
# Clean up any issues
python scripts/fix_smart_quotes.py app/templates/draft-report-incremental.docx
python scripts/merge_split_equals.py app/templates/draft-report-incremental.docx

# Final test
python scripts/test_section.py app/templates/draft-report-incremental.docx
```

### Promote to Production
```bash
# Backup old
mv app/templates/draft-audit-report-poc.docx app/templates/draft-audit-report-poc-old.docx

# Promote new
cp app/templates/draft-report-incremental.docx app/templates/draft-audit-report-poc.docx

# Verify
python scripts/quick_test.py
```

**Done! Move to Story 1.5.6** 🎉
