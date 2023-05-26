import boto3
import time
import sys
import urllib3
import time
from botocore.exceptions import ClientError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Replace YOUR_REGION with the region where you want to create the VMs and volumes
CLUSTER_IP = '10.16.145.102'
#IMAGE_ID = 'ami-f57317037b5b45b4852cc8ecac50b381'
ec2 = boto3.client(
        service_name="ec2",
        region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )


def create_ebs_volume(volume_size, availability_zone, tag_key, tag_value):
    tag_specifications = [{'ResourceType': 'volume', 'Tags': [{'Key': tag_key, 'Value': tag_value}]}]
    try:
        response = ec2.create_volume(
            AvailabilityZone=availability_zone,
            VolumeType='vt-boto3',
            Size=volume_size,
            TagSpecifications=tag_specifications
        )
        volume_id = response['VolumeId']
        print(f"EBS volume {volume_id} created successfully!")
        return volume_id
    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"Error creating EBS volume: {error_message}")
        return None
volume_id = create_ebs_volume(volume_size=4, availability_zone='symphony', tag_key='Name', tag_value='MyEBSVolume')

