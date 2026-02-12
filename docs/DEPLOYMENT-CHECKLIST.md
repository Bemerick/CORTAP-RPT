# CORTAP-RPT Deployment Checklist

Quick reference for deploying to AWS.

## ☐ Pre-Deployment

- [ ] AWS CLI installed (`aws --version`)
- [ ] SAM CLI installed (`sam --version`)
- [ ] AWS credentials configured (`aws configure --profile govcloud`)
- [ ] Python 3.11 available (`python3.11 --version`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)

## ☐ Configuration

- [ ] Update `config/project-setup.json` with project data
- [ ] Validate configuration (`python scripts/manage_project_config.py validate`)
- [ ] Review `samconfig.toml` parameters
- [ ] Verify `template.yaml` environment variables

## ☐ Files Check

- [ ] `app/templates/draft_audit_report.docx` exists
- [ ] `config/project-setup.json` exists
- [ ] `requirements.txt` complete
- [ ] `.samignore` configured

## ☐ Build

```bash
sam build --use-container
```

- [ ] Build succeeds without errors
- [ ] Check `.aws-sam/build/GenerateReportSyncFunction/config/` exists
- [ ] Check `.aws-sam/build/GenerateReportSyncFunction/app/templates/` exists

## ☐ Deploy

**First time:**
```bash
sam deploy --guided --profile govcloud
```

**Updates:**
```bash
sam build && sam deploy --profile govcloud
```

- [ ] Deployment completes successfully
- [ ] Stack status = `CREATE_COMPLETE` or `UPDATE_COMPLETE`

## ☐ Post-Deployment

- [ ] Get Function URL:
  ```bash
  aws cloudformation describe-stacks --stack-name cortap-rpt-dev --profile govcloud \
    --query 'Stacks[0].Outputs[?OutputKey==`GenerateReportSyncFunctionUrl`].OutputValue' --output text
  ```

- [ ] Get S3 Bucket:
  ```bash
  aws cloudformation describe-stacks --stack-name cortap-rpt-dev --profile govcloud \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucket`].OutputValue' --output text
  ```

- [ ] Test endpoint with sample request
- [ ] Verify logs in CloudWatch
- [ ] Verify S3 bucket accessible

## ☐ Testing

```bash
# Test command
curl -X POST https://[function-url]/api/v1/generate-report-sync \
  -H "Authorization: Bearer $RISKUITY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id": 33, "report_type": "draft_audit_report"}'
```

- [ ] Response status = 200
- [ ] Report generated successfully
- [ ] Document uploaded to S3
- [ ] Download URL works

## ☐ Monitoring

- [ ] CloudWatch logs visible
- [ ] Alarms configured (errors, duration)
- [ ] Metrics dashboard created (optional)

## ☐ Documentation

- [ ] Function URL documented
- [ ] S3 bucket name documented
- [ ] Integration instructions shared with team
- [ ] Riskuity team notified

---

## Quick Commands

```bash
# Full deployment workflow
sam build --use-container
sam deploy --profile govcloud

# View logs
sam logs --stack-name cortap-rpt-dev --tail --profile govcloud

# Delete stack
sam delete --stack-name cortap-rpt-dev --profile govcloud
```

---

## Rollback Plan

If deployment fails:

1. **Check logs:**
   ```bash
   sam logs --stack-name cortap-rpt-dev --profile govcloud
   ```

2. **Rollback to previous version:**
   ```bash
   aws cloudformation cancel-update-stack --stack-name cortap-rpt-dev --profile govcloud
   ```

3. **Delete failed stack:**
   ```bash
   sam delete --stack-name cortap-rpt-dev --profile govcloud
   ```

4. **Redeploy from last known good state**

---

**Status:** Ready for deployment
**Last Updated:** February 12, 2026
