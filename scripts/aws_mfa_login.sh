#!/bin/bash
#
# AWS MFA Login Script
#
# This script gets temporary AWS credentials using MFA and stores them
# in your AWS credentials file under a new profile.
#
# Usage:
#   ./scripts/aws_mfa_login.sh [MFA_CODE]
#
# Example:
#   ./scripts/aws_mfa_login.sh 123456
#
# After running, use the profile:
#   aws s3 ls --profile govcloud-mfa
#   export AWS_PROFILE=govcloud-mfa
#

set -e

# Configuration
BASE_PROFILE="default"  # Your base AWS profile (from aws configure)
MFA_PROFILE="govcloud-mfa"  # Profile name for MFA session
REGION="us-gov-west-1"
SESSION_DURATION=43200  # 12 hours (max for IAM users)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "AWS MFA Authentication"
echo "=========================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ ERROR: AWS CLI not installed${NC}"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if base profile is configured
if ! aws configure get aws_access_key_id --profile $BASE_PROFILE > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Base AWS profile '$BASE_PROFILE' not configured${NC}"
    echo ""
    echo "Please run: aws configure --profile $BASE_PROFILE"
    exit 1
fi

# Get current user identity
echo "Step 1: Getting your AWS identity..."
IDENTITY=$(aws sts get-caller-identity --profile $BASE_PROFILE --region $REGION 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Failed to get AWS identity${NC}"
    echo "$IDENTITY"
    exit 1
fi

USER_ARN=$(echo $IDENTITY | jq -r .Arn)
ACCOUNT_ID=$(echo $IDENTITY | jq -r .Account)
USERNAME=$(echo $USER_ARN | awk -F'/' '{print $NF}')

echo -e "${GREEN}✅ Identity verified${NC}"
echo "   User: $USERNAME"
echo "   Account: $ACCOUNT_ID"
echo "   ARN: $USER_ARN"
echo ""

# Construct MFA device ARN
# Format: arn:aws-us-gov:iam::ACCOUNT_ID:mfa/USERNAME
MFA_DEVICE_ARN="arn:aws-us-gov:iam::${ACCOUNT_ID}:mfa/${USERNAME}"

echo "Step 2: MFA Device Detection..."
echo "   Expected MFA ARN: $MFA_DEVICE_ARN"
echo ""

# Verify MFA device exists
echo "Step 3: Verifying MFA device is registered..."
MFA_DEVICES=$(aws iam list-mfa-devices --user-name $USERNAME --profile $BASE_PROFILE --region $REGION 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Could not verify MFA device${NC}"
    echo "   Proceeding anyway..."
else
    DEVICE_COUNT=$(echo $MFA_DEVICES | jq -r '.MFADevices | length')
    if [ "$DEVICE_COUNT" -eq 0 ]; then
        echo -e "${RED}❌ ERROR: No MFA device registered for user $USERNAME${NC}"
        echo ""
        echo "You need to register an MFA device in AWS Console:"
        echo "1. Go to: https://console.amazonaws-us-gov.com/"
        echo "2. Click your name (top right) → Security Credentials"
        echo "3. Under 'Multi-factor authentication (MFA)' click 'Assign MFA device'"
        exit 1
    fi

    ACTUAL_MFA_ARN=$(echo $MFA_DEVICES | jq -r '.MFADevices[0].SerialNumber')
    echo -e "${GREEN}✅ MFA device found${NC}"
    echo "   Device ARN: $ACTUAL_MFA_ARN"

    # Use the actual ARN if different from expected
    if [ "$ACTUAL_MFA_ARN" != "$MFA_DEVICE_ARN" ]; then
        echo -e "${YELLOW}   (Using actual ARN instead of constructed one)${NC}"
        MFA_DEVICE_ARN=$ACTUAL_MFA_ARN
    fi
fi
echo ""

# Get MFA code
if [ -z "$1" ]; then
    echo "Step 4: Enter your MFA code"
    echo -n "MFA Code (6 digits from your authenticator app): "
    read MFA_CODE
else
    MFA_CODE=$1
    echo "Step 4: Using provided MFA code"
fi

# Validate MFA code format
if ! [[ $MFA_CODE =~ ^[0-9]{6}$ ]]; then
    echo -e "${RED}❌ ERROR: Invalid MFA code format${NC}"
    echo "   MFA code must be 6 digits"
    exit 1
fi

echo ""
echo "Step 5: Requesting temporary session credentials..."
echo "   Duration: $SESSION_DURATION seconds ($(($SESSION_DURATION / 3600)) hours)"

# Get session token with MFA
SESSION_OUTPUT=$(aws sts get-session-token \
    --profile $BASE_PROFILE \
    --region $REGION \
    --serial-number "$MFA_DEVICE_ARN" \
    --token-code "$MFA_CODE" \
    --duration-seconds $SESSION_DURATION \
    2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Failed to get session token${NC}"
    echo "$SESSION_OUTPUT"
    echo ""
    echo "Common causes:"
    echo "  - Invalid MFA code (check your authenticator app)"
    echo "  - MFA code already used (wait for new code)"
    echo "  - Incorrect MFA device ARN"
    echo "  - Clock skew (check your system time)"
    exit 1
fi

# Extract credentials
ACCESS_KEY=$(echo $SESSION_OUTPUT | jq -r .Credentials.AccessKeyId)
SECRET_KEY=$(echo $SESSION_OUTPUT | jq -r .Credentials.SecretAccessKey)
SESSION_TOKEN=$(echo $SESSION_OUTPUT | jq -r .Credentials.SessionToken)
EXPIRATION=$(echo $SESSION_OUTPUT | jq -r .Credentials.Expiration)

echo -e "${GREEN}✅ Session credentials obtained${NC}"
echo "   Expires: $EXPIRATION"
echo ""

# Store credentials in AWS credentials file
echo "Step 6: Storing credentials in AWS profile '$MFA_PROFILE'..."

aws configure set aws_access_key_id "$ACCESS_KEY" --profile $MFA_PROFILE
aws configure set aws_secret_access_key "$SECRET_KEY" --profile $MFA_PROFILE
aws configure set aws_session_token "$SESSION_TOKEN" --profile $MFA_PROFILE
aws configure set region "$REGION" --profile $MFA_PROFILE

echo -e "${GREEN}✅ Credentials stored${NC}"
echo ""

# Test the credentials
echo "Step 7: Testing MFA session..."
TEST_RESULT=$(aws sts get-caller-identity --profile $MFA_PROFILE --region $REGION 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ MFA session is active and working${NC}"
    echo ""

    # Show how to use
    echo "=========================================="
    echo "✅ Success! MFA Authentication Complete"
    echo "=========================================="
    echo ""
    echo "Your temporary credentials are valid for $(($SESSION_DURATION / 3600)) hours"
    echo "Expiration: $EXPIRATION"
    echo ""
    echo "To use these credentials:"
    echo ""
    echo "  Option 1 - Specify profile in each command:"
    echo "    aws s3 ls --profile $MFA_PROFILE"
    echo "    aws s3 mb s3://cortap-documents-dev --profile $MFA_PROFILE --region $REGION"
    echo ""
    echo "  Option 2 - Set as default profile for this terminal session:"
    echo "    export AWS_PROFILE=$MFA_PROFILE"
    echo "    aws s3 ls"
    echo ""
    echo "  Option 3 - Update your .env file:"
    echo "    AWS_PROFILE=$MFA_PROFILE"
    echo ""
    echo "=========================================="
    echo ""
    echo "Next step: Run the S3 bucket setup script:"
    echo "  export AWS_PROFILE=$MFA_PROFILE"
    echo "  ./scripts/setup_s3_dev_bucket.sh"
    echo ""
else
    echo -e "${RED}❌ ERROR: MFA session test failed${NC}"
    echo "$TEST_RESULT"
    exit 1
fi
