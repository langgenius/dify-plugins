import gevent.monkey
gevent.monkey.patch_all()
import json
import boto3
from typing import Any, Dict, List, Union
from botocore.exceptions import ClientError, BotoCoreError
from dify_plugin import Tool

from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get instance ID (dynamic from env)
instance_id = os.getenv("EC2_INSTANCE_ID")


class EC2ControlTool(Tool):
    """
    AWS EC2 Instance Control Tool
    
    This tool allows users to manage EC2 instances through Dify workflows.
    Supported operations: start, stop, reboot, status
    """
    
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> str:
        """
        Invoke the EC2 control tool
        
        Args:
            user_id: The ID of the user invoking the tool
            tool_parameters: Dictionary containing:
                - action: The action to perform (start|stop|status|reboot)
                - instance_ids: Comma-separated string of instance IDs
                - region: AWS region (optional)
        
        Returns:
            String containing the result of the operation
        """
        try:
            # Extract parameters
            action = tool_parameters.get('action', '').lower()
            instance_ids_str = tool_parameters.get('instance_ids', '')
            region = tool_parameters.get('region') or self.runtime.credentials.get('aws_region', 'us-east-1')
            
            # Validate action
            if action not in ['start', 'stop', 'status', 'reboot']:
                return self._create_error_response("Invalid action. Supported actions: start, stop, status, reboot")
            
            # Parse instance IDs
            if not instance_ids_str:
                return self._create_error_response("Instance IDs are required")
            
            instance_ids = [id.strip() for id in instance_ids_str.split(',') if id.strip()]
            
            if not instance_ids:
                return self._create_error_response("No valid instance IDs provided")
            
            # Validate instance ID format
            for instance_id in instance_ids:
                if not self._validate_instance_id(instance_id):
                    return self._create_error_response(f"Invalid instance ID format: {instance_id}")
            
            # Create EC2 client
            ec2_client = self._create_ec2_client(region)
            
            # Execute the requested action
            if action == 'status':
                return self._get_instance_status(ec2_client, instance_ids)
            elif action == 'start':
                return self._start_instances(ec2_client, instance_ids)
            elif action == 'stop':
                return self._stop_instances(ec2_client, instance_ids)
            elif action == 'reboot':
                return self._reboot_instances(ec2_client, instance_ids)
            else:
                # This should never happen due to validation above, but ensures all paths return
                return self._create_error_response("Unknown action specified")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            return self._create_error_response(f"AWS Error ({error_code}): {error_message}")
        except BotoCoreError as e:
            return self._create_error_response(f"AWS Configuration Error: {str(e)}")
        except Exception as e:
            return self._create_error_response(f"Unexpected error: {str(e)}")
    
    def _create_ec2_client(self, region: str):
        """Create and configure EC2 client"""
        credentials = self.runtime.credentials
        
        return boto3.client(
            'ec2',
            aws_access_key_id=credentials.get('aws_access_key_id'),
            aws_secret_access_key=credentials.get('aws_secret_access_key'),
            region_name=region
        )
    
    def _validate_instance_id(self, instance_id: str) -> bool:
        """Validate EC2 instance ID format"""
        import re
        # EC2 instance ID pattern: i- followed by 8 or 17 hexadecimal characters
        pattern = r'^i-[0-9a-f]{8}([0-9a-f]{9})?$'
        return bool(re.match(pattern, instance_id.lower()))
    
    def _get_instance_status(self, ec2_client, instance_ids: List[str]) -> str:
        """Get status information for EC2 instances"""
        try:
            response = ec2_client.describe_instances(InstanceIds=instance_ids)
            
            instances_info = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_info = {
                        'InstanceId': instance['InstanceId'],
                        'State': instance['State']['Name'],
                        'InstanceType': instance['InstanceType'],
                        'LaunchTime': instance.get('LaunchTime', 'N/A').isoformat() if instance.get('LaunchTime') else 'N/A',
                        'PublicIpAddress': instance.get('PublicIpAddress', 'N/A'),
                        'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                        'Platform': instance.get('Platform', 'Linux/UNIX')
                    }
                    instances_info.append(instance_info)
            
            # Format response for readability
            result = f"📊 **EC2 Instance Status Report**\n\n"
            for info in instances_info:
                status_emoji = self._get_status_emoji(info['State'])
                result += f"{status_emoji} **{info['InstanceId']}**\n"
                result += f"   • State: {info['State']}\n"
                result += f"   • Type: {info['InstanceType']}\n"
                result += f"   • Platform: {info['Platform']}\n"
                result += f"   • Public IP: {info['PublicIpAddress']}\n"
                result += f"   • Private IP: {info['PrivateIpAddress']}\n"
                result += f"   • Launch Time: {info['LaunchTime']}\n\n"
            
            return result
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                return self._create_error_response("One or more instance IDs not found")
            raise
    
    def _start_instances(self, ec2_client, instance_ids: List[str]) -> str:
        """Start EC2 instances"""
        response = ec2_client.start_instances(InstanceIds=instance_ids)
        
        result = "🚀 **Starting EC2 Instances**\n\n"
        for instance in response['StartingInstances']:
            current_state = instance['CurrentState']['Name']
            previous_state = instance['PreviousState']['Name']
            result += f"• **{instance['InstanceId']}**: {previous_state} → {current_state}\n"
        
        result += f"\n✅ Successfully initiated start command for {len(instance_ids)} instance(s)"
        return result
    
    def _stop_instances(self, ec2_client, instance_ids: List[str]) -> str:
        """Stop EC2 instances"""
        response = ec2_client.stop_instances(InstanceIds=instance_ids)
        
        result = "🛑 **Stopping EC2 Instances**\n\n"
        for instance in response['StoppingInstances']:
            current_state = instance['CurrentState']['Name']
            previous_state = instance['PreviousState']['Name']
            result += f"• **{instance['InstanceId']}**: {previous_state} → {current_state}\n"
        
        result += f"\n✅ Successfully initiated stop command for {len(instance_ids)} instance(s)"
        return result
    
    def _reboot_instances(self, ec2_client, instance_ids: List[str]) -> str:
        """Reboot EC2 instances"""
        ec2_client.reboot_instances(InstanceIds=instance_ids)
        
        result = "🔄 **Rebooting EC2 Instances**\n\n"
        for instance_id in instance_ids:
            result += f"• **{instance_id}**: Reboot initiated\n"
        
        result += f"\n✅ Successfully initiated reboot command for {len(instance_ids)} instance(s)"
        return result
    
    def _get_status_emoji(self, state: str) -> str:
        """Get emoji for instance state"""
        emoji_map = {
            'pending': '🟡',
            'running': '🟢', 
            'shutting-down': '🟠',
            'terminated': '🔴',
            'stopping': '🟠',
            'stopped': '⚫'
        }
        return emoji_map.get(state.lower(), '❓')
    
    def _create_error_response(self, message: str) -> str:
        """Create formatted error response"""
        return f"❌ **Error**: {message}"


# Export the tool class
__all__ = ['EC2ControlTool']
