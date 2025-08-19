# AWS EC2 Controller Plugin for Dify

This plugin allows you to control AWS EC2 instances directly from your Dify workflows.

## Features

- ✅ **Start Instances** - Start stopped EC2 instances
- ✅ **Stop Instances** - Stop running EC2 instances  
- ✅ **Reboot Instances** - Reboot running instances
- ✅ **Check Status** - Get detailed instance information
- ✅ **Multi-Instance Support** - Control multiple instances at once
- ✅ **Error Handling** - Comprehensive error messages
- ✅ **Security** - Uses AWS credentials securely

## Installation

1. Copy the plugin folder to your Dify plugins directory
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your AWS credentials in the Dify plugin settings

## Configuration

### Required Credentials:
- **AWS Access Key ID**: Your AWS access key
- **AWS Secret Access Key**: Your AWS secret key
- **AWS Region** (optional): Default region for instances

### Tool Parameters:
- **Action**: start, stop, status, or reboot
- **Instance IDs**: Comma-separated list of instance IDs
- **Region** (optional): Override default region

## Usage Examples

### In Dify Workflow:

1. **Check Instance Status:**
   - Action: `status`
   - Instance IDs: `i-1234567890abcdef0`

2. **Start Multiple Instances:**
   - Action: `start`
   - Instance IDs: `i-1234567890abcdef0,i-0987654321fedcba0`

3. **Stop Instance in Different Region:**
   - Action: `stop`
   - Instance IDs: `i-1234567890abcdef0`
   - Region: `eu-west-1`

## Security Notes

- ⚠️ **Least Privilege**: Only grant necessary EC2 permissions
- ⚠️ **Credential Security**: Never expose AWS credentials in logs
- ⚠️ **Instance Access**: Restrict to specific instance IDs when possible

## IAM Policy Example

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:RebootInstances",
                "ec2:DescribeInstances"
            ],
            "Resource": [
                "arn:aws:ec2:*:*:instance/i-1234567890abcdef0",
                "arn:aws:ec2:*:*:instance/i-0987654321fedcba0"
            ]
        }
    ]
}
```

## Troubleshooting

### Common Errors:
- **InvalidInstanceID.NotFound**: Check instance ID format and existence
- **UnauthorizedOperation**: Verify IAM permissions
- **InvalidParameterValue**: Check region and parameter formats

### Support:
- Check AWS CloudTrail for detailed error logs
- Verify instance IDs are in the correct region
- Ensure instances are in a valid state for the requested operation
```


## Installation Instructions:

1. **Create the project structure** as shown above
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Copy to Dify plugins directory**: Usually `dify/plugins/`
4. **Configure AWS credentials** in Dify plugin settings
5. **Restart Dify** to load the new plugin
6. **Use in workflows** via the tool selector

This complete plugin provides:
- ✅ Full EC2 control (start/stop/reboot/status)
- ✅ Multi-instance support
- ✅ Comprehensive error handling
- ✅ Security best practices
- ✅ Unit tests
- ✅ Documentation
- ✅ Easy installation