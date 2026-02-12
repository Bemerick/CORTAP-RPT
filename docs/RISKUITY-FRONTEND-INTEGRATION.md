# Riskuity Frontend Integration Guide

**Version:** 1.0
**Date:** 2026-02-12
**For:** Riskuity Development Team
**API Version:** Synchronous Report Generation

---

## Overview

This guide helps the Riskuity frontend team integrate the CORTAP-RPT synchronous report generation endpoint into the Riskuity web application.

### What Users Will See

1. User clicks **"Generate Report"** button in Riskuity
2. Loading modal appears with progress indicator
3. After 30-60 seconds, document is generated
4. Success modal with **"Download Report"** button
5. Clicking download starts document download

### Integration Points

- **Trigger:** Button in Riskuity project view
- **Authentication:** Pass user's existing Bearer token
- **Loading:** Show progress indicator during generation
- **Success:** Display download link or auto-download
- **Error:** Show user-friendly error messages

---

## Quick Start

### 1. Endpoint Information

**Production URL:** `https://[lambda-function-url]/api/v1/generate-report-sync`
**Method:** `POST`
**Timeout:** 120 seconds (2 minutes)
**Authentication:** Bearer token (user's Riskuity token)

### 2. Minimal Example

```javascript
async function generateReport(projectId) {
  try {
    const response = await fetch(
      'https://[lambda-function-url]/api/v1/generate-report-sync',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getUserToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: projectId,
          report_type: 'draft_audit_report'
        }),
        signal: AbortSignal.timeout(120000) // 2 min
      }
    );

    if (!response.ok) throw new Error('Generation failed');

    const result = await response.json();
    window.location.href = result.download_url; // Auto-download
  } catch (error) {
    console.error('Error:', error);
    alert('Report generation failed');
  }
}
```

---

## Complete Implementation

### Step 1: Add Generate Button

Add a button to the project details page:

```html
<!-- In project view -->
<div class="project-actions">
  <button
    id="generate-report-btn"
    class="btn btn-primary"
    onclick="handleGenerateReport()">
    <i class="icon-document"></i>
    Generate Report
  </button>
</div>
```

### Step 2: Implement Generation Handler

```javascript
/**
 * Main handler for report generation
 */
async function handleGenerateReport() {
  // Get current project ID from page context
  const projectId = getCurrentProjectId();

  // Get report type (could be from dropdown or default)
  const reportType = getSelectedReportType() || 'draft_audit_report';

  // Show loading modal
  const modal = showLoadingModal({
    title: 'Generating Report',
    message: 'Fetching project data and generating document...',
    estimatedTime: '30-60 seconds',
    cancellable: false
  });

  try {
    // Call generation endpoint
    const result = await generateReport(projectId, reportType);

    // Close loading modal
    modal.close();

    // Show success and handle download
    showSuccessModal(result);

  } catch (error) {
    modal.close();
    showErrorModal(error);
  }
}

/**
 * Core generation function
 */
async function generateReport(projectId, reportType) {
  const apiUrl = getApiUrl(); // Get from config
  const token = getUserToken(); // Get from auth context

  console.log(`Generating ${reportType} for project ${projectId}`);

  const response = await fetch(
    `${apiUrl}/api/v1/generate-report-sync`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Request-ID': generateRequestId() // Optional tracking
      },
      body: JSON.stringify({
        project_id: projectId,
        report_type: reportType
      }),
      // Important: Set timeout longer than server timeout
      signal: AbortSignal.timeout(125000) // 125 seconds
    }
  );

  // Handle response
  if (!response.ok) {
    const error = await response.json();
    throw new ReportGenerationError(error);
  }

  return await response.json();
}

/**
 * Get user's authentication token
 */
function getUserToken() {
  // Get from your auth context/store
  return window.auth.getToken(); // Example
}

/**
 * Get current project ID from page
 */
function getCurrentProjectId() {
  // Extract from URL, page data, or context
  return window.currentProject.id; // Example
}

/**
 * Get selected report type
 */
function getSelectedReportType() {
  const select = document.getElementById('report-type-select');
  return select ? select.value : 'draft_audit_report';
}

/**
 * Get API URL from configuration
 */
function getApiUrl() {
  // Return environment-specific URL
  return window.config.cortapApiUrl ||
         'https://[lambda-function-url]';
}

/**
 * Generate unique request ID for tracking
 */
function generateRequestId() {
  return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
```

### Step 3: Loading Modal

```javascript
/**
 * Show loading modal during generation
 */
function showLoadingModal({ title, message, estimatedTime, cancellable = false }) {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-content loading-modal">
      <div class="modal-header">
        <h3>${title}</h3>
      </div>
      <div class="modal-body">
        <div class="spinner"></div>
        <p class="message">${message}</p>
        <p class="estimated-time">Estimated time: ${estimatedTime}</p>
        <div class="progress-container">
          <div class="progress-bar" id="progress-bar"></div>
        </div>
        ${cancellable ? '<button class="btn-cancel">Cancel</button>' : ''}
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Simulate progress (optional)
  let progress = 0;
  const progressBar = document.getElementById('progress-bar');
  const interval = setInterval(() => {
    progress = Math.min(progress + Math.random() * 10, 95);
    progressBar.style.width = `${progress}%`;
  }, 2000);

  return {
    close: () => {
      clearInterval(interval);
      document.body.removeChild(modal);
    },
    updateProgress: (percent) => {
      progressBar.style.width = `${percent}%`;
    }
  };
}
```

### Step 4: Success Modal

```javascript
/**
 * Show success modal with download option
 */
function showSuccessModal(result) {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-content success-modal">
      <div class="modal-header success">
        <i class="icon-check-circle"></i>
        <h3>Report Generated Successfully</h3>
      </div>
      <div class="modal-body">
        <div class="report-info">
          <p><strong>Recipient:</strong> ${result.metadata.recipient_name}</p>
          <p><strong>Report Type:</strong> ${formatReportType(result.report_type)}</p>
          <p><strong>Review Areas:</strong> ${result.metadata.review_areas}</p>
          <p><strong>Deficiencies:</strong> ${result.metadata.deficiency_count}</p>
          <p><strong>File Size:</strong> ${formatFileSize(result.file_size_bytes)}</p>
          <p><strong>Generated:</strong> ${formatTimestamp(result.generated_at)}</p>
        </div>
        <div class="download-info">
          <p class="expiry-warning">
            <i class="icon-clock"></i>
            Download link expires in 24 hours
          </p>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeModal(this)">
          Close
        </button>
        <button class="btn btn-primary" onclick="downloadReport('${result.download_url}')">
          <i class="icon-download"></i>
          Download Report
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Option: Auto-download after 2 seconds
  setTimeout(() => {
    downloadReport(result.download_url);
  }, 2000);
}

/**
 * Trigger document download
 */
function downloadReport(downloadUrl) {
  // Create temporary link and click it
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = ''; // Browser will use filename from Content-Disposition
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

/**
 * Format report type for display
 */
function formatReportType(type) {
  const types = {
    'draft_audit_report': 'Draft Audit Report',
    'recipient_information_request': 'Recipient Information Request'
  };
  return types[type] || type;
}

/**
 * Format ISO timestamp for display
 */
function formatTimestamp(isoString) {
  return new Date(isoString).toLocaleString();
}
```

### Step 5: Error Handling

```javascript
/**
 * Custom error class for report generation
 */
class ReportGenerationError extends Error {
  constructor(errorResponse) {
    const detail = errorResponse.detail || {};
    super(detail.message || 'Report generation failed');
    this.name = 'ReportGenerationError';
    this.code = detail.error;
    this.details = detail.details;
    this.correlationId = detail.correlation_id;
  }
}

/**
 * Show error modal with helpful messages
 */
function showErrorModal(error) {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';

  // Get user-friendly message
  const { title, message, suggestion } = getErrorMessage(error);

  modal.innerHTML = `
    <div class="modal-content error-modal">
      <div class="modal-header error">
        <i class="icon-alert-circle"></i>
        <h3>${title}</h3>
      </div>
      <div class="modal-body">
        <p class="error-message">${message}</p>
        ${suggestion ? `<p class="suggestion">${suggestion}</p>` : ''}
        ${error.correlationId ? `
          <p class="correlation-id">
            <small>Error ID: ${error.correlationId}</small>
          </p>
        ` : ''}
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeModal(this)">
          Close
        </button>
        <button class="btn btn-primary" onclick="handleGenerateReport()">
          <i class="icon-refresh"></i>
          Try Again
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
}

/**
 * Get user-friendly error messages
 */
function getErrorMessage(error) {
  // Timeout errors
  if (error.name === 'TimeoutError') {
    return {
      title: 'Generation Timed Out',
      message: 'The report took too long to generate (> 2 minutes).',
      suggestion: 'This project may have a large amount of data. Please try again or contact support if the issue persists.'
    };
  }

  // Network errors
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return {
      title: 'Connection Error',
      message: 'Unable to connect to the report generation service.',
      suggestion: 'Please check your internet connection and try again.'
    };
  }

  // API errors with error codes
  if (error instanceof ReportGenerationError) {
    switch (error.code) {
      case 'missing_required_data':
        return {
          title: 'Missing Required Information',
          message: 'This project is missing information required for report generation.',
          suggestion: error.details?.missing_fields
            ? `Please add: ${error.details.missing_fields.join(', ')}`
            : 'Please ensure all project information is complete.'
        };

      case 'invalid_data':
        return {
          title: 'Invalid Project Data',
          message: 'The project data could not be validated for report generation.',
          suggestion: 'Please review the project information and ensure all fields are correct.'
        };

      case 'authentication_failed':
        return {
          title: 'Authentication Failed',
          message: 'Your session may have expired.',
          suggestion: 'Please log out and log back in, then try again.'
        };

      case 'insufficient_permissions':
        return {
          title: 'Access Denied',
          message: 'You do not have permission to generate reports for this project.',
          suggestion: 'Please contact your administrator if you believe this is an error.'
        };

      case 'riskuity_api_error':
        return {
          title: 'Unable to Fetch Project Data',
          message: 'There was an error retrieving project data from Riskuity.',
          suggestion: 'Please try again in a few moments. If the issue persists, contact support.'
        };

      case 'generation_failed':
        return {
          title: 'Report Generation Failed',
          message: 'An error occurred while generating the document.',
          suggestion: 'Please try again. If the issue persists, contact support with error ID: ' + error.correlationId
        };

      default:
        return {
          title: 'Generation Error',
          message: error.message || 'An unexpected error occurred.',
          suggestion: 'Please try again or contact support if the issue persists.'
        };
    }
  }

  // Default error
  return {
    title: 'Error',
    message: error.message || 'An unexpected error occurred.',
    suggestion: 'Please try again or contact support.'
  };
}

/**
 * Close modal helper
 */
function closeModal(button) {
  const modal = button.closest('.modal-overlay');
  if (modal) {
    document.body.removeChild(modal);
  }
}
```

---

## API Reference

### Request

**Endpoint:** `POST /api/v1/generate-report-sync`

**Headers:**
```javascript
{
  'Authorization': 'Bearer <user-token>',
  'Content-Type': 'application/json'
}
```

**Body:**
```javascript
{
  "project_id": 33,                    // Required: Riskuity project ID
  "report_type": "draft_audit_report"  // Required: Template type
}
```

**Report Types:**
- `draft_audit_report` - Draft Triennial Review / SMR Report
- `recipient_information_request` - RIR Cover Letter

### Response (Success - 200 OK)

```javascript
{
  "status": "completed",
  "report_id": "rpt-20260212-141530-x7y8z9",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "download_url": "https://s3-govcloud.amazonaws.com/cortap-docs/...",
  "expires_at": "2026-02-13T14:15:00Z",
  "generated_at": "2026-02-12T14:15:30Z",
  "file_size_bytes": 524288,
  "metadata": {
    "recipient_name": "Greater Portland Transit District",
    "review_type": "Triennial Review",
    "review_areas": 21,
    "deficiency_count": 2,
    "generation_time_ms": 48523
  },
  "correlation_id": "gen-sync-41899cd919af"
}
```

**Key Fields:**
- `download_url` - Presigned S3 URL (expires in 24 hours)
- `expires_at` - ISO 8601 timestamp when URL expires
- `file_size_bytes` - Document size for display
- `metadata` - Project info for confirmation modal

### Response (Error)

**400 Bad Request** - Invalid data or missing required fields
```javascript
{
  "detail": {
    "error": "missing_required_data",
    "message": "Cannot generate report: missing critical fields",
    "details": {
      "missing_fields": ["recipient_contact_email"],
      "quality_score": 95
    },
    "timestamp": "2026-02-12T14:15:30Z",
    "correlation_id": "gen-sync-x7y8z9"
  }
}
```

**401 Unauthorized** - Invalid or expired token
```javascript
{
  "detail": {
    "error": "authentication_failed",
    "message": "Invalid or expired token",
    "timestamp": "2026-02-12T14:15:30Z",
    "correlation_id": "gen-sync-x7y8z9"
  }
}
```

**403 Forbidden** - User lacks permission for project
```javascript
{
  "detail": {
    "error": "insufficient_permissions",
    "message": "User lacks access to project 33",
    "timestamp": "2026-02-12T14:15:30Z",
    "correlation_id": "gen-sync-x7y8z9"
  }
}
```

**502 Bad Gateway** - Riskuity API error
```javascript
{
  "detail": {
    "error": "riskuity_api_error",
    "message": "Failed to fetch data from Riskuity: API unavailable",
    "details": {
      "error_code": "API_UNAVAILABLE"
    },
    "timestamp": "2026-02-12T14:15:30Z",
    "correlation_id": "gen-sync-x7y8z9"
  }
}
```

**504 Gateway Timeout** - Generation exceeded 2 minutes
```javascript
{
  "detail": {
    "error": "timeout",
    "message": "Generation exceeded timeout (2 minutes)",
    "timestamp": "2026-02-12T14:15:30Z",
    "correlation_id": "gen-sync-x7y8z9"
  }
}
```

---

## Configuration

### Environment-Specific URLs

```javascript
// config.js
const config = {
  development: {
    cortapApiUrl: 'http://localhost:8000'
  },
  staging: {
    cortapApiUrl: 'https://staging-xyz.lambda-url.us-gov-west-1.on.aws'
  },
  production: {
    cortapApiUrl: 'https://prod-xyz.lambda-url.us-gov-west-1.on.aws'
  }
};

export const getApiUrl = () => {
  const env = process.env.NODE_ENV || 'development';
  return config[env].cortapApiUrl;
};
```

### Feature Flags

Consider adding feature flags for gradual rollout:

```javascript
const FEATURES = {
  reportGeneration: {
    enabled: true,
    rollout: 100, // Percentage of users
    reportTypes: ['draft_audit_report'] // Initially limit types
  }
};

function isFeatureEnabled(feature) {
  const config = FEATURES[feature];
  if (!config.enabled) return false;

  // Gradual rollout
  const userHash = hashUserId(getCurrentUser().id);
  return (userHash % 100) < config.rollout;
}

// Usage
if (isFeatureEnabled('reportGeneration')) {
  showGenerateButton();
}
```

---

## Testing

### Manual Testing Checklist

- [ ] **Happy Path**
  - [ ] Click "Generate Report" button
  - [ ] Loading modal appears
  - [ ] Success modal appears after 30-60s
  - [ ] Document downloads successfully
  - [ ] Document opens in Word

- [ ] **Error Handling**
  - [ ] Test with invalid project ID → Show error
  - [ ] Test with expired token → Prompt re-login
  - [ ] Test with slow network → Show timeout message
  - [ ] Cancel during generation → Handle gracefully

- [ ] **Edge Cases**
  - [ ] Test with project missing required fields
  - [ ] Test with very large project (> 500 controls)
  - [ ] Test concurrent generation requests
  - [ ] Test download link after 24 hours (should expire)

### Automated Testing

```javascript
// Example Jest test
describe('Report Generation', () => {
  it('should generate report successfully', async () => {
    // Mock fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          status: 'completed',
          download_url: 'https://s3.aws.com/test',
          metadata: { recipient_name: 'Test' }
        })
      })
    );

    // Call function
    const result = await generateReport(33, 'draft_audit_report');

    // Assert
    expect(result.status).toBe('completed');
    expect(result.download_url).toBeDefined();
  });

  it('should handle errors gracefully', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({
          detail: { error: 'missing_required_data' }
        })
      })
    );

    // Assert error thrown
    await expect(
      generateReport(33, 'draft_audit_report')
    ).rejects.toThrow(ReportGenerationError);
  });
});
```

---

## Performance Considerations

### 1. Show Progress Feedback

Since generation takes 30-60 seconds, provide clear feedback:

```javascript
function showProgressStages() {
  const stages = [
    { time: 0, message: 'Connecting to report service...' },
    { time: 5000, message: 'Fetching project data from Riskuity...' },
    { time: 20000, message: 'Transforming data...' },
    { time: 30000, message: 'Generating Word document...' },
    { time: 45000, message: 'Uploading to secure storage...' },
    { time: 55000, message: 'Almost done...' }
  ];

  let currentStage = 0;
  const interval = setInterval(() => {
    if (currentStage < stages.length) {
      updateModalMessage(stages[currentStage].message);
      currentStage++;
    }
  }, 10000); // Update every 10 seconds

  return () => clearInterval(interval);
}
```

### 2. Prevent Duplicate Requests

```javascript
let isGenerating = false;

async function handleGenerateReport() {
  if (isGenerating) {
    alert('A report is already being generated. Please wait.');
    return;
  }

  isGenerating = true;
  try {
    await generateReport(...);
  } finally {
    isGenerating = false;
  }
}
```

### 3. Cache Recent Reports

Consider caching recent report metadata:

```javascript
const reportCache = new Map();

function getCachedReport(projectId) {
  const cached = reportCache.get(projectId);
  if (cached && Date.now() - cached.timestamp < 3600000) { // 1 hour
    return cached.data;
  }
  return null;
}

function cacheReport(projectId, data) {
  reportCache.set(projectId, {
    data,
    timestamp: Date.now()
  });
}
```

---

## Security Considerations

### 1. Token Handling

**DO:**
- ✅ Pass user's existing Bearer token
- ✅ Let token expire naturally (don't extend)
- ✅ Use HTTPS only

**DON'T:**
- ❌ Store token in localStorage
- ❌ Log token in console
- ❌ Send token in query parameters

### 2. Download Link Handling

- Download URLs expire in 24 hours
- URLs are presigned (no additional auth needed)
- Treat URLs as sensitive (don't log or share)

### 3. CORS

The Lambda Function URL is configured to allow:
- **Origins:** `https://app.riskuity.com` (production)
- **Methods:** `POST`
- **Headers:** `Authorization`, `Content-Type`

Contact CORTAP team to add additional origins for staging/dev.

---

## Support & Troubleshooting

### Common Issues

#### 1. CORS Errors

**Symptom:** Browser blocks request with CORS error

**Solution:**
- Verify your domain is in `AllowedOrigins` (contact CORTAP team)
- Check that you're using HTTPS (not HTTP)
- Ensure headers are correct (`Authorization`, `Content-Type`)

#### 2. 401 Unauthorized

**Symptom:** "Authentication failed" error

**Solution:**
- Verify token is valid (not expired)
- Ensure `Authorization` header starts with `Bearer `
- Check token has proper Riskuity format

#### 3. Timeout Errors

**Symptom:** Request times out after 2 minutes

**Solution:**
- This is rare (typical: 30-50s)
- Check project size (> 500 controls may be slow)
- Retry once - may be transient Riskuity API issue
- If persistent, contact CORTAP support with correlation_id

#### 4. Missing Required Data

**Symptom:** "Cannot generate report: missing critical fields"

**Solution:**
- Review missing_fields in error response
- Ensure project has required information in Riskuity
- Add missing data and retry

### Getting Help

**CORTAP Support:**
- Email: support@cortap.example.com
- Include: correlation_id from error response
- Include: project_id and timestamp

**Debug Information:**
```javascript
// Include this info when reporting issues:
{
  correlationId: error.correlationId,
  projectId: projectId,
  timestamp: new Date().toISOString(),
  userAgent: navigator.userAgent,
  errorMessage: error.message
}
```

---

## Styling Examples (CSS)

```css
/* Loading Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.modal-header.success {
  color: #10b981;
}

.modal-header.error {
  color: #ef4444;
}

/* Spinner */
.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Progress Bar */
.progress-container {
  width: 100%;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
  margin: 16px 0;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  border-radius: 4px;
  transition: width 0.3s ease;
  width: 0%;
}

/* Report Info */
.report-info {
  background: #f9fafb;
  border-radius: 4px;
  padding: 16px;
  margin: 16px 0;
}

.report-info p {
  margin: 8px 0;
  font-size: 14px;
}

.report-info strong {
  font-weight: 600;
  color: #374151;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

/* Expiry Warning */
.expiry-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f59e0b;
  font-size: 14px;
  margin: 12px 0;
}
```

---

## Next Steps

1. **Review Integration Guide** with your team
2. **Set Up Development Environment** with test endpoint
3. **Implement Basic Integration** (button + loading + download)
4. **Add Error Handling** for all error cases
5. **Test Thoroughly** with various projects
6. **Deploy to Staging** for QA testing
7. **Deploy to Production** with feature flag

---

## Appendix

### A. TypeScript Interfaces

```typescript
// Request
interface GenerateReportRequest {
  project_id: number;
  report_type: 'draft_audit_report' | 'recipient_information_request';
}

// Response
interface GenerateReportResponse {
  status: 'completed';
  report_id: string;
  project_id: number;
  report_type: string;
  download_url: string;
  expires_at: string; // ISO 8601
  generated_at: string; // ISO 8601
  file_size_bytes: number;
  metadata: ReportMetadata;
  correlation_id: string;
}

interface ReportMetadata {
  recipient_name: string;
  review_type: string;
  review_areas: number;
  deficiency_count: number;
  generation_time_ms: number;
}

// Error
interface ErrorResponse {
  detail: {
    error: string;
    message: string;
    details?: any;
    timestamp: string;
    correlation_id: string;
  };
}
```

### B. React Component Example

```typescript
import React, { useState } from 'react';

export const GenerateReportButton: React.FC<{ projectId: number }> = ({ projectId }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const result = await generateReport(projectId, 'draft_audit_report');
      // Show success modal
      showSuccessModal(result);
    } catch (err) {
      setError(err.message);
      showErrorModal(err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <button
      onClick={handleGenerate}
      disabled={isGenerating}
      className="btn btn-primary"
    >
      {isGenerating ? (
        <>
          <Spinner size="sm" />
          Generating...
        </>
      ) : (
        <>
          <DocumentIcon />
          Generate Report
        </>
      )}
    </button>
  );
};
```

---

**Last Updated:** 2026-02-12
**Version:** 1.0
**Maintained By:** CORTAP-RPT Team
**Questions:** support@cortap.example.com
