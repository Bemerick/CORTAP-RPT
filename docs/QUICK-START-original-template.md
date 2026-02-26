# Quick Start - Building from Original Template

**Goal:** Convert the original Word template to Jinja2 section by section while preserving all formatting.

---

## ✅ Ready to Start!

Everything is set up:
- ✅ Original template copied to: `app/templates/draft-report-working.docx`
- ✅ Test script ready: `scripts/test_section.py`
- ✅ Template analyzed (7 sections, 36 subsections)
- ✅ Baseline test passes

---

## 🎯 Before You Begin

### 1. Configure Word (CRITICAL!)

**Do this FIRST, before opening any Word documents:**

```
Mac: Word → Preferences → AutoCorrect → AutoFormat As You Type
Windows: File → Options → Proofing → AutoCorrect Options → AutoFormat As You Type

UNCHECK:
  ❌ "Straight quotes" with "smart quotes"
  ❌ Hyphens with dash
  ❌ Fractions
  ❌ Ordinals

Click OK → RESTART Word
```

### 2. Open the Template

```bash
open app/templates/draft-report-working.docx
```

---

## 🔄 Workflow (Repeat for Each Section)

### Step 1: Find & Replace
- Find placeholder text (see patterns below)
- **Delete it completely**
- **Type** the Jinja2 replacement (don't paste!)

### Step 2: Save & Close
- **Save** the document
- **Close Word completely** (not just the window)

### Step 3: Test
```bash
python scripts/test_section.py app/templates/draft-report-working.docx
```

### Step 4: Verify
```bash
# Check the output
open output/incremental/draft-report-working_test.docx
```

### Step 5: Continue
- ✅ PASS → Move to next section
- ❌ FAIL → Fix error, go back to Step 2

---

## 📝 Section 1: Cover Letter (Start Here!)

**Placeholders to Replace:**

### Easy Find & Replace (use Word's Find & Replace)

| Find This | Replace With |
|-----------|--------------|
| `Month Day, Year` | `{{ date_format(project.report_date) }}` |
| `FY2025` | `FY{{ project.fiscal_year }}` |
| `[Recipient Acronym]` | `{{ project.recipient_acronym }}` |
| `[Recipient name]` | `{{ project.recipient_name }}` |
| `[City, State]` | `{{ project.recipient_city }}, {{ project.recipient_state }}` |

### Manual Replacements (type these)

```
Current: INSERT Regional Header
Replace: {{ project.regional_office_header }}

Current: Name (recipient contact)
Replace: {{ project.recipient_contact_name }}

Current: Title
Replace: {{ project.recipient_contact_title }}

Current: Recipient Organization Name
Replace: {{ project.recipient_name }}

Current: Street Address
Replace: {{ project.recipient_address }}

Current: City, State, Zip
Replace: {{ project.recipient_city }}, {{ project.recipient_state }}, {{ project.recipient_zip }}
```

### Conditional Text (choose ONE option)

```
Current: [Triennial Review]/[State Management Review]/[Combined...]
Replace: {{ project.review_type }}

Current: [Draft/Final]
Replace: {{ project.report_status }}

Current: [draft/final] (lowercase)
Replace: {{ project.report_status | lower }}

Current: Mr./Ms. [Last Name]
Replace: {{ project.recipient_salutation }} {{ project.recipient_last_name }}
```

### Test Section 1
```bash
python scripts/test_section.py app/templates/draft-report-working.docx
```

**Expected:** ✅ Cover letter has real data (recipient name, date, etc.)

---

## 📊 Section 2: Executive Summary (Next)

See full guide: `docs/incremental-build-from-original.md`

**Key replacements:**

```
Metric table:
- [Recipient Acronym] → {{ project.recipient_acronym }}
- April 11, 2024 → {{ date_format(project.review_start_date) }}
- May 13, 2024 → {{ date_format(project.review_end_date) }}

Conditional findings:
{% if not metadata.has_deficiencies %}
[no deficiency text]
{% endif %}

{% if metadata.has_deficiencies %}
The review identified {{ metadata.deficiency_count }} {{ 'deficiency' if metadata.deficiency_count == 1 else 'deficiencies' }}.
{% endif %}
```

### Test Section 2
```bash
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json
```

---

## 🗺️ Remaining Sections

See detailed instructions in: `docs/incremental-build-from-original.md`

**Sections:**
3. Review Background and Process
4. Recipient Description
5. **Results of the Review (23 assessment areas - do 2-3 at a time!)**
6. Attendees
7. Appendices

**Test after EVERY 2-3 expressions!**

---

## 💡 Quick Tips

### ✅ DO
- **Type** Jinja2 fresh - never paste
- **Close Word** completely before testing
- **Test often** (every 2-3 changes)
- Use **Find & Replace** for repeated placeholders

### ❌ DON'T
- Don't paste Jinja2 from other documents
- Don't use curly quotes (' ') - only straight quotes (' ")
- Don't add 20+ expressions without testing
- Don't forget to close Word before testing

### 🔍 Watch For
- Smart quotes (`'` instead of `'`) - check Word settings
- Years next to Jinja2: `FY2025 {{` should be `FY2025  {{` (two spaces)
- Section numbers: use `'5' + '307'` not `'5307'`

---

## 🐛 Troubleshooting

### Test fails with "unexpected '<'"
Word added XML into your Jinja2
→ Delete the entire expression, retype fresh

### Test passes but output looks wrong
Check the test data has the fields you're using
→ Try different test file: `tests/fixtures/mock-data/GPTD_FY2023_TR.json`

### Smart quotes appeared
Word settings didn't stick
→ Recheck settings, restart Word, run `python scripts/fix_smart_quotes.py app/templates/draft-report-working.docx`

---

## 📚 Full Documentation

- **Detailed guide:** `docs/incremental-build-from-original.md`
- **Template analysis:** `output/original_template_analysis.txt`
- **Progress tracker:** `.bmad-ephemeral/incremental-build-progress.md`

---

## ✅ When Section is Done

```bash
# Test passes?
python scripts/test_section.py app/templates/draft-report-working.docx

# Output looks good?
open output/incremental/draft-report-working_test.docx

# ✓ Move to next section!
```

---

## 🎉 Final Steps (When All Sections Complete)

```bash
# Test all 5 mock files
for file in tests/fixtures/mock-data/*.json; do
  python scripts/test_section.py app/templates/draft-report-working.docx "$file"
done

# Clean up any issues
python scripts/fix_smart_quotes.py app/templates/draft-report-working.docx
python scripts/merge_split_equals.py app/templates/draft-report-working.docx

# Promote to production
mv app/templates/draft-audit-report-poc.docx app/templates/draft-audit-report-poc-old.docx
cp app/templates/draft-report-working.docx app/templates/draft-audit-report-poc.docx

# Done! ✨
```
