#!/bin/ksh
# AWS MFA Login Script (KSH compatible)
# Gets temporary session credentials using MFA token
#
# Usage:
#   source scripts/aws-mfa-login.ksh
#   . scripts/aws-mfa-login.ksh

# Your MFA device ARN
MFA_DEVICE="arn:aws-us-gov:iam::736539455039:mfa/bob"

# Prompt for MFA code (ksh compatible)
print -n "Enter MFA code: "
read MFA_CODE

# Validate MFA code (should be 6 digits)
if [[ ! "$MFA_CODE" =~ ^[0-9]{6}$ ]]; then
    print "Error: MFA code must be 6 digits"
    return 1 2>/dev/null || exit 1
fi

# Get temporary credentials
print "Requesting session token..."
CREDENTIALS=$(aws sts get-session-token \
    --serial-number $MFA_DEVICE \
    --token-code $MFA_CODE \
    --duration-seconds 43200 2>&1)

# Check if the command was successful
if [ $? -ne 0 ]; then
    print "Error getting session token:"
    print "$CREDENTIALS"
    return 1 2>/dev/null || exit 1
fi

# Export the credentials
export AWS_ACCESS_KEY_ID=$(print $CREDENTIALS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(print $CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(print $CREDENTIALS | jq -r '.Credentials.SessionToken')

# Verify credentials were set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ "$AWS_ACCESS_KEY_ID" = "null" ]; then
    print "Error: Failed to extract credentials"
    return 1 2>/dev/null || exit 1
fi

print "✅ MFA credentials set successfully for 12 hours"
print "Credentials expire at: $(print $CREDENTIALS | jq -r '.Credentials.Expiration')"
print ""
print "Environment variables set:"
print "  AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:0:20}..."
print "  AWS_SECRET_ACCESS_KEY=***"
print "  AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN:0:20}..."
