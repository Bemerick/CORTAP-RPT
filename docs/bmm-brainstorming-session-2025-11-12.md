# Brainstorming Session Results

**Session Date:** 2025-11-12
**Facilitator:** Business Analyst Mary
**Participant:** Bob

## Executive Summary

**Topic:** CORTAP-RPT Reporting Module - Document generation system for FTA CORTAP audits

**Session Goals:** Comprehensive exploration of architecture, features, technical approaches, user workflows, data transformation strategies, and integration design for a reporting module that generates Word documents from Riskuity API data.

**Techniques Used:**
1. Mind Mapping (15-20 min)
2. SCAMPER Method (20 min)
3. Six Thinking Hats (20 min)
4. What If Scenarios (15 min)

**Total Ideas Generated:** 40+ architectural decisions, feature concepts, and technical considerations

### Key Themes Identified:

1. **Risk Mitigation Through Early Validation** - Front-loading technical risks (Word formatting, API structure) rather than discovering issues late in development

2. **Simplicity for POC** - Resisting feature creep; focusing on core workflow: select project → select template → generate → download

3. **Auditor-Centric Design** - Removing formatting burden from auditors to enable focus on core audit work

4. **Build vs Buy** - Decided to build with Python stack rather than integrate external tools (cost-effective, full control)

5. **Python-First Architecture** - Leveraging team expertise with Python for both data processing and document generation

## Technique Sessions

### Session 1: Mind Mapping - System Architecture

**Central Concept:** CORTAP-RPT Reporting Module

**Major Branches Explored:**

**1. DATA SOURCES**
- Single source: Riskuity API only (Excel files removed for simplification)
- Endpoints: Assessments, Risks, Surveys
- Authentication: API keys
- Data readiness indicator/flag system
- Data freshness: Not a concern (static snapshots)
- 36 CORTAP reviews for FY26

**2. DATA PROCESSING / WORKFLOW**

Setup Phase (one-time):
- Create Survey Templates in Riskuity (for each document type)
- Define CORTAP FY26 framework with controls

Per-Project Workflow (×36 CORTAP reviews):
- Create new Riskuity project
- Apply CORTAP FY26 framework + controls
- Perform Assessments for each control with "Deficient" or "Non-Deficient" comments
- Create surveys from templates
- Complete survey responses
- Export all data (Assessments, Surveys, Risks) via API
- Generate Word documents from exported data + templates

**3. BUSINESS RULES / LOGIC**

Template Field Handling Strategy:
- Pre-generation validation: Check for critical required fields
- Warn user if critical data missing (list what's missing)
- User choice: proceed, cancel, or review data
- Conditional sections: Hide/show template blocks based on data presence
- Smart defaults for optional fields ("N/A", "Not Applicable")

Requirements:
- Template metadata: Which fields are required vs optional
- Field mapping: Data source → template field relationships
- Validation engine: Pre-flight checks before generation
- Section logic: Rules for when to show/hide sections

**4. INTEGRATION LAYER**

Primary: Embedded in Riskuity UI
- "Generate Document" button in Riskuity project view
- Calls CORTAP-RPT API/service
- Passes project context (project ID, recipient info)

Secondary: Standalone capability (TBD)
- Direct API access for manual/batch processing
- Useful for: bulk regeneration, testing, emergency fixes

Async Document Generation Pattern:
- User selects project + templates → Submit request
- CORTAP-RPT creates job (returns job ID immediately)
- User sees: "Document generation in progress..."
- Processing happens in background
- When complete:
  - Document saved to S3
  - User notification
  - Download link available

Components Needed:
- Job queue system
- Job status tracking (pending → processing → complete → failed)
- Job history/audit trail
- Retry logic for failures
- Notification mechanism (in-app polling, WebSocket, or email)

**5. USER WORKFLOW**

Document Generation Flow:
1. User selects specific CORTAP project/review (1 of 36)
2. User selects which template(s) to generate:
   - Draft Audit Report ⭐ (POC starting point)
   - Cover Letter
   - Recipient Request for Information
   - Others...
3. System generates selected documents
4. Documents stored in S3 automatically
5. User can download immediately

**6. TECHNOLOGY STACK**

Primary Decision: **Python**
- Team expertise in Python
- Open source libraries
- Cost-effective
- Good for data processing

Document Generation Libraries (TO TEST IN POC):
- python-docxtpl (Jinja2 templating, good for conditional sections)
- docx-mailmerge (simple merge fields, better formatting preservation)
- python-docx (creating from scratch, limited for templates)

**7. ERROR HANDLING & RESILIENCE**

Potential Risks Identified:
- Riskuity API changes/breaks
- API downtime during critical audit deadlines
- Word formatting preservation (BIGGEST CONCERN)
- Document generation failures
- S3 upload failures
- Job queue failures
- Data quality issues (missing fields)

### Session 2: SCAMPER Method - Technology Decisions

**S - SUBSTITUTE:**
- Python vs .NET evaluation → **Decision: Python** (team expertise, cost)
- Editable Word docs required (cannot substitute with PDFs)
- Team is more experienced with Python

**C - COMBINE:**
- Python for both data processing AND Word generation
- Unified data pipeline: Merge Riskuity API data into consistent model
- Combine notification methods: Email + in-app + S3 event trigger (future)

**A - ADAPT:**
- Adapt from mail merge concept but enhance beyond its limitations
- **Learned from experience:** Mailchimp used before, but prefer own stack to reduce external tool costs
- Mail Merge in Word too limited for needs

**M - MODIFY/MAGNIFY:**
Enhanced capabilities beyond basic mail merge:
- Conditional sections (show/hide based on data)
- Dynamic tables (variable rows)
- Rich formatting (bold/highlight deficiencies)
- Nested data structures
- Business rules for smart field handling

**P - PUT TO OTHER USES:**
- Future extensibility for other fiscal years (FY27, FY28...)
- Potential for other audit types or frameworks
- (Deferred consideration - focus on CORTAP FY26 for POC)

**E - ELIMINATE:**
- ✅ Excel files eliminated (use Riskuity API only)
- Cannot eliminate template selection (user needs choice)
- Cannot eliminate S3 storage (requirement)
- Manual trigger needed (not automatic)

**R - REVERSE/REARRANGE:**
- No preview/review step needed before generation
- Straight through: request → validate → generate → store
- Data in Riskuity is authoritative

### Session 3: Six Thinking Hats - Balanced Analysis

**🤍 WHITE HAT - Facts:**
- 36 CORTAP reviews for FY26
- Data source: Riskuity API only (Assessments, Risks, Surveys)
- Output: Editable Word documents
- Multiple template types
- Team expertise: Python
- Integration: React/Node app calls reporting module
- Pattern: Async job processing
- Storage: S3 + download capability
- Timeline: **Proof of concept in a few weeks**
- Development: **Using Claude Code**
- Infrastructure: **AWS**
- Users: **~20 auditors**
- Security: **No special compliance requirements**

**💛 YELLOW HAT - Benefits:**
- **Time savings:** 36 reviews × multiple documents = hundreds of hours saved
- **Consistency:** All documents follow same formatting, no human error
- **Scalability:** Handle FY27, FY28... with same system; more auditors, more reviews
- **Auditor happiness:** Click button, get polished document
- **Professional output:** Clean, properly formatted audit deliverables
- **Reusability:** Templates reused year after year
- **Flexibility:** Python stack means easy updates/enhancements
- **Force multiplier for audit program**

**🖤 BLACK HAT - Risks:**

**#1 CRITICAL RISK: Word Formatting Preservation**
- Python libraries may not preserve complex Word formatting
- Government/professional formatting must remain perfect
- python-docx: Limited for templates
- docx-mailmerge: Better but simple substitution only
- python-docxtpl: Best for complex logic, uses Jinja2

Mitigation: **Test python-docxtpl and docx-mailmerge with actual Draft Audit Report template in Week 1**

Other Technical Risks:
- Riskuity API changes/rate limits
- API downtime during deadlines
- Document corruption
- S3 upload failures
- Job queue failures

Process Risks:
- Templates change frequently (maintenance burden) - **LOW: few changes expected**
- Data quality issues
- Missing critical fields
- Users generate too early
- Version control confusion

**❤️ RED HAT - Feelings:**
- Project seems **straightforward**
- **Biggest excitement:** Taking pressure off auditors to focus on audit work, not document formatting
- Confident about async approach
- Timeline feels realistic
- Word formatting risk is manageable with early testing

**💚 GREEN HAT - Creative Alternatives (Deferred to V2):**
- Template Studio (visual field mapping UI)
- Smart suggestions from past audits
- Batch mode (queue multiple generations)
- Version history in S3
- Template tester with sample data
- PDF export option

**💙 BLUE HAT - Process & Organization:**

POC Phases (3 weeks):

**Phase 1: Template + Library Testing (Week 1)** ⚡ CRITICAL
- Test python-docxtpl vs docx-mailmerge with Draft Audit Report
- Validate formatting preservation
- Choose library
- **Decision point:** Python works OR need .NET fallback

**Phase 2: Riskuity API Integration (Week 1-2)**
- Connect to Riskuity API
- Pull sample Assessment/Survey/Risk data
- Map data structure to template fields

**Phase 3: Document Generation Engine (Week 2)**
- Build core generation logic
- Implement validation rules
- Handle missing fields (conditional sections + warnings)

**Phase 4: Job Queue + Storage (Week 2-3)** - **START WITH SYNCHRONOUS** (simpler for POC)
- Synchronous generation first (user waits with progress indicator)
- S3 upload
- Download link generation
- **Defer async job queue to v2** after POC validation

**Phase 5: React/Node Integration (Week 3)**
- API endpoint for generation request
- Job status endpoint
- Download link generation

### Session 4: What If Scenarios - Edge Cases

**Scenario 1: Scale**
- What if FY27 has 100 audits? → Architecture handles it (async jobs scale)
- What if 10 auditors generate simultaneously? → Job queue handles concurrency

**Scenario 2: Failures**
- What if Riskuity API is down at deadline? → (Manageable - accept risk for POC)
- What if generation fails halfway? → Retry logic, error notification

**Scenario 3: Data Quality**
- What if Assessment missing "Deficient/Non-Deficient" comment? → Validation catches it, user decides to proceed or cancel

**Scenario 4: Template Evolution**
- What if FY27 template has 20 new fields? → Extend Riskuity data model

**Scenario 5: Audit Changes**
- What if auditor needs to fix data and regenerate? → Overwrite or version history (v2)

**Assessment:** All scenarios manageable

## Template Data Requirements

**Draft Audit Report Template Fields Identified:**

### Document Metadata
- `[REGION #]` - FTA Region number
- `[XX-2020-000-00]` - Review/audit ID
- `[DRAFT/FINAL]` - Document status
- `[draft/final]` - Document status (lowercase variant)
- `[Draft/Final]` - Document status (title case variant)

### Review Type
- `[Triennial Review]` - Review type option 1
- `[State Management Review]` - Review type option 2 (uses `/[` separator pattern)
- Review types appear to be mutually exclusive options

### Recipient Information
- `[Recipient name]` - Full organization name
- `[Recipient Acronym]` - Organization abbreviation
- `[City, State]` - Location
- `[subrecipient name]` - Sub-organization name
- `[subrecipient City/County]` - Sub-organization location
- `[Subrecipients]` - Multiple subrecipients reference
- `[Contractors/Lessees]` - Contractor information

### Dates
- `[Month]` - Month name
- `[Day]` - Day number
- Multiple date contexts: Scoping Meeting, Site Visit Entrance, Site Visit Exit, Draft Report, Final Report

### Personnel
- `[Last Name]` - Recipient contact
- `[Appropriate Regional Officer Titles]` - FTA officer designation
- `[FTA Title]` - FTA staff title
- `[reviewer name]` - Assigned reviewer
- `[contractor name]` - Contractor representative
- `[contractor firm]` - Contractor company

### Contact Information
- `[phone number]` - Contact phone
- `[email]` - Contact email address

### Findings Data
- `[#]` - Count of deficiencies
- `[no]` - Boolean indicator ("no repeat deficiencies")
- `[LIST]` - Dynamic list of deficiency areas
- `[is/are]` - Grammar helper
- `[is/is not]` - Boolean grammar helper
- `[an]` - Grammar helper (a/an)

### Conditional Sections
- `[IF APPLICABLE]` - Conditional content marker
- `[ADD AS APPLICABLE]` - Optional content marker
- `[OR]` - Alternative option marker

**Key Observations:**
1. **Conditional logic needed:** Many fields like `[Triennial Review]/[State Management Review]` indicate mutually exclusive options
2. **Dynamic lists:** `[LIST]` fields need to support variable-length content
3. **Grammar helpers:** Fields like `[is/are]`, `[an]` suggest smart pluralization logic needed
4. **Repeating patterns:** Date fields, personnel fields repeat across different contexts
5. **Deficiency tracking:** Core data model around deficiencies, repeat deficiencies, ERF (Enhanced Review Focus)

## Idea Categorization

### Immediate Opportunities (POC - Weeks 1-3)

**Priority 1: Python Library Validation** ⚡
- Test python-docxtpl and docx-mailmerge with Draft Audit Report template
- Validate formatting preservation with varying data
- **MUST COMPLETE WEEK 1** - This is the critical go/no-go decision

**Priority 2: Riskuity API Data Structure**
- Understand API response structure (flat? nested? paginated?)
- Map API fields to template merge fields
- Test with real project data
- **Need API access credentials first**

**Priority 3: Process Consistency & Reliability**
- Define validation rules
- Build validation engine
- Implement conditional section logic
- Error handling with clear messages
- **Weeks 2-3**

**Core POC Features:**
- Single document generation (synchronous, user waits)
- Riskuity API integration
- Template field validation
- Conditional sections handling
- S3 storage + download
- Basic error handling

### Future Innovations (Post-POC, Version 2+)

**Async Job Queue System:**
- Background processing
- Job status tracking
- Notification system (email, WebSocket, in-app)
- Job history and audit trail

**Enhanced Features:**
- Batch document generation (multiple projects at once)
- Template Studio (visual field mapping interface)
- Version history for generated documents
- Template tester with sample data
- Smart suggestions from past audits
- PDF export option alongside Word
- Advanced notification mechanisms

**Scalability Enhancements:**
- Support for 100+ audits per fiscal year
- Concurrent generation optimization
- Retry and recovery logic
- Performance monitoring

### Moonshots (Long-term Vision)

**AI-Powered Audit Assistance:**
- Auto-suggest findings based on historical patterns
- Anomaly detection in assessment data
- Natural language query of audit data

**Multi-Format Publishing:**
- Generate executive summaries automatically
- Create presentation decks from audit data
- Interactive dashboard views

**Cross-Year Analytics:**
- Trend analysis across fiscal years
- Recipient performance tracking
- Framework evolution impact analysis

### Insights and Learnings

**Critical Insights:**

1. **Simplification was key:** Removing Excel files as a data source dramatically simplified the architecture and eliminated file parsing complexity

2. **Word formatting is THE technical risk:** All other architectural decisions are validated patterns, but Python's ability to preserve complex Word formatting is uncertain until tested

3. **Synchronous-first approach de-risks faster:** Starting with synchronous generation allows validating the core document generation challenge before adding async complexity

4. **Auditor workflow drives design:** Every decision traced back to "does this make auditors' lives easier?" - no feature creep, just reliable document generation

5. **Template analysis reveals data model:** The merge fields show a rich data model with conditional logic, dynamic lists, and grammar helpers that inform API mapping requirements

**Technical Learnings:**

- python-docxtpl likely best choice for conditional sections and loops
- Conditional sections more important than initially recognized (half the template fields are conditional)
- Grammar helpers (`[is/are]`, `[an]`) suggest need for smart template logic beyond simple substitution
- Dynamic `[LIST]` fields require iteration support in template engine

**Process Learnings:**

- Build vs buy decision = build (cost, control, team expertise)
- POC phasing must front-load the highest risk (Word formatting)
- Template metadata (required vs optional fields) is critical for validation engine
- User choice on proceeding with missing data balances flexibility with data quality

## Action Planning

### Top 3 Priority Ideas

#### #1 Priority: Python Library Validation with Actual Template

**Rationale:** This is the single highest technical risk. If Python cannot preserve the complex formatting of the Draft Audit Report while supporting conditional sections and dynamic lists, the entire Python-based approach fails. Must validate Week 1.

**Next steps:**
1. Request Riskuity API access and credentials
2. Extract sample assessment data structure from API (or use mock data)
3. Set up test environment with python-docxtpl and docx-mailmerge
4. Create test scenarios:
   - Full data population (all fields present)
   - Partial data (optional fields missing)
   - Conditional variations (Triennial vs State Management Review)
   - Dynamic lists (variable number of deficiencies)
5. Generate test documents and compare formatting against original template
6. **Decision:** Proceed with Python OR pivot to .NET/alternative

**Resources needed:**
- Draft Audit Report template (✅ have it)
- Riskuity API access (⏳ pending request)
- Sample assessment/survey data
- Python development environment
- AWS/local S3 testing bucket

**Timeline:** Week 1 (CRITICAL PATH)

#### #2 Priority: Riskuity API Data Structure Mapping

**Rationale:** Understanding how data comes from the API (structure, pagination, completeness) is essential for building the data transformation layer and mapping to template fields.

**Next steps:**
1. Review Riskuity API documentation (https://api.riskuity.com/docs)
2. Test API calls:
   - GET Assessments for a project
   - GET Surveys for a project
   - GET Risks for a project
3. Document response schemas
4. Identify if data comes in one call or requires multiple endpoints
5. Create data mapping document: API field → Template merge field
6. Identify which fields are always present vs optional
7. Design data transformation logic (API response → template data model)

**Resources needed:**
- API credentials and access
- API documentation
- Test CORTAP project in Riskuity with sample data
- Data modeling tool/documentation

**Timeline:** Week 1-2

#### #3 Priority: Validation Engine & Business Rules

**Rationale:** Ensuring data completeness and providing clear feedback to users is critical for trust and adoption. Auditors need confidence that generated documents are accurate and complete.

**Next steps:**
1. Define required vs optional template fields
2. Create validation rule set:
   - Critical fields that must be present
   - Conditional field dependencies (if [Triennial Review] then need X fields)
   - Data format validation (dates, phone numbers, emails)
3. Build validation engine:
   - Pre-generation validation check
   - Return list of missing/invalid fields
   - Severity levels (error vs warning)
4. Implement conditional section logic:
   - Rules for show/hide sections
   - Grammar helpers logic ([is/are], [an])
5. Design user feedback:
   - Clear error messages
   - "Proceed anyway" vs "Cancel and fix" options
6. Test with various data completeness scenarios

**Resources needed:**
- Complete template field inventory (✅ extracted)
- Business rules documentation from audit team
- Validation library (Python: Pydantic, Cerberus)
- Test data scenarios

**Timeline:** Week 2-3

## Reflection and Follow-up

### What Worked Well

**Mind Mapping** was excellent for:
- Visualizing the full system architecture
- Revealing the complete CORTAP workflow (not just the reporting module)
- Uncovering the per-project workflow details
- Identifying all major system components and their relationships

**SCAMPER** drove critical decisions:
- Build vs Buy (build with Python)
- Python vs .NET (Python based on team expertise)
- Simplification (remove Excel files)
- Understanding what to eliminate vs keep

**Six Thinking Hats** surfaced the critical risk early:
- Black Hat identified Word formatting as #1 concern
- Red Hat confirmed auditor-centric motivation
- Yellow Hat quantified time savings benefits
- White Hat established concrete facts (timeline, resources)

**What If Scenarios** validated the architecture robustness:
- Confirmed async design handles scale
- Identified manageable edge cases
- Built confidence in architectural choices

**Template Analysis** revealed data model complexity:
- Conditional logic requirements
- Dynamic list support needs
- Grammar helper logic
- Field categorization (required vs optional)

### Areas for Further Exploration

**When API Access Granted:**
- Riskuity API response structure in detail
- Pagination strategy for large data sets
- API rate limits and throttling
- Error response patterns
- Authentication token refresh strategy

**During POC Development:**
- Optimal template engine (python-docxtpl vs docx-mailmerge)
- Conditional section implementation patterns
- Grammar helper logic implementation
- Dynamic table generation approaches
- S3 integration best practices

**Post-POC:**
- Async job queue architecture (Celery, Redis, AWS SQS)
- Notification mechanism selection
- Version control for generated documents
- Analytics and monitoring strategy
- Batch processing optimization

### Recommended Follow-up Techniques

**For Next Research Session (when API access available):**
- **Deep Dive Analysis** - Examine API documentation and responses
- **Data Flow Mapping** - Trace data from API to template fields
- **Error Scenario Planning** - What-if analysis of API failures

**For Architecture Refinement:**
- **Decision Matrix** - Evaluate python-docxtpl vs docx-mailmerge vs python-docx
- **Assumption Testing** - Validate technical assumptions with spike testing

**For Implementation Planning:**
- **Story Mapping** - Break POC into user stories for development
- **Risk Register** - Catalog and track all identified risks

### Questions That Emerged

**Technical Questions (need answers before/during POC):**

1. Does the Riskuity API return all assessment data in one call, or requires pagination/multiple endpoints?
2. Are there API rate limits that would affect document generation performance?
3. Can python-docxtpl preserve Word styles, headers, footers, and complex formatting?
4. How do we handle merge field [LIST] - comma-separated, bulleted, numbered, or custom format?
5. What triggers the "data ready" flag in Riskuity - manual or automatic?

**Business Rules Questions (need audit team input):**

6. Which template fields are absolutely required (block generation) vs nice-to-have?
7. For conditional fields like [Triennial Review]/[State Management Review] - how is this determined? User selection or data-driven?
8. What grammar rules apply for [is/are] helpers - based on count of items?
9. Should generated documents include metadata (generation timestamp, data source version)?
10. What's the retention policy for generated documents in S3?

**Process Questions (need stakeholder input):**

11. Who has authority to trigger document generation - any auditor or specific roles?
12. Should there be an approval workflow before documents are finalized?
13. How do auditors want to be notified when async generation completes?
14. What happens if an auditor regenerates a document - version history or overwrite?

### Next Session Planning

**Suggested topics:**
1. **API Integration Deep-Dive** (after API access granted) - Map complete data flow from Riskuity to templates
2. **Error Handling & Resilience Design** - Plan for failure scenarios and recovery strategies
3. **User Experience Flow** - Detail the auditor's interaction with document generation feature

**Recommended timeframe:**
- API Deep-Dive: 1-2 weeks from now (when API access granted)
- Error Handling Design: Week 2 of POC (during implementation)
- UX Flow Refinement: Week 3 of POC (during React/Node integration)

**Preparation needed:**
- ✅ Request Riskuity API access immediately
- ✅ Set up Python development environment
- ✅ Install candidate libraries (python-docxtpl, docx-mailmerge, python-docx)
- ✅ Review Draft Audit Report template in detail
- ✅ Identify test CORTAP project in Riskuity for sample data
- Move to PRD workflow next to document requirements formally

---

**✅ Brainstorming session complete! Ready to proceed to PRD creation.**

_Session facilitated using the BMAD BMM brainstorming framework with CIS techniques_
