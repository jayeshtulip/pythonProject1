import boto3
import paramiko
import boto3
import time
import sys
import urllib3
import time
import platform
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Replace YOUR_REGION with the region where you want to create the VMs and volumes
CLUSTER_IP = '10.16.146.12'
#IMAGE_ID = 'ami-f57317037b5b45b4852cc8ecac50b381'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )

# Set the name and zone for the VMs and volumes
name_prefix = "account2-test-15-01"

# Create a client for the EC2 service
#ec2 = boto3.client("ec2", region_name=region)

# Create the VMs and volumes
for i in range(1,3):
    # Create the VM
    vm_name = f" {name_prefix}-{i}"
    vm = ec2.run_instances(
        ImageId="ami-58fb95f0fa484ce091e21a363db302f8",  # Debian 9 AMI
        InstanceType="t2.micro",
        MaxCount=1,
        MinCount=1,
        KeyName='my-key-pair',
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": vm_name
                    }
                ]
            }
        ]
    )
    instance_id = vm["Instances"][0]["InstanceId"]
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id, ])
    eip_allocation = ec2.allocate_address(
        Domain='vpc',
        TagSpecifications=[
            {
                'ResourceType': 'elastic-ip',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'my-elastic-ip'
                    },
                ]
            },
        ]
    )
    print(f'Allocation ID {eip_allocation["AllocationId"]}')
    print(f'  - Elastic IP {eip_allocation["PublicIp"]} has been allocated')
    allocation_response1 = ec2.associate_address(
        InstanceId=instance_id,
        AllocationId=eip_allocation["AllocationId"]
    )
    print("instance with public ip created")

    volume_name = f"Testing{name_prefix}-volume-{i}"
    #print("tst1")
    volume = ec2.create_volume(
        AvailabilityZone='symphony',
        Size=2,
        TagSpecifications=[
            {
                "ResourceType": "volume",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": volume_name
                    }
                ]
            }
        ]
    )
    #print("test2")
    volume_id = volume["VolumeId"]
    # Attach the volume to the VM
    waiter = ec2.get_waiter('volume_available')
    waiter.wait(VolumeIds=[volume_id, ])
    ec2.attach_volume(
        Device="/dev/sdm",
        InstanceId=instance_id,
        VolumeId=volume_id
    )
    # SSH to instances and mount volumes
    print("testing 1")
    key_name = 'my-key-pair'
    response = ec2.describe_key_pairs(KeyNames=[key_name])
    print("jayesh", response)
    private_key = response['KeyPairs'][0]['KeyFingerprint']

    # save key pair to file
    if platform.system() == 'Windows':
        import tempfile

        pem_file = os.path.join(tempfile.gettempdir(), f'{key_name}.ppk')
        ppk = paramiko.RSAKey(data=private_key)
        ppk.write_private_key_file(pem_file)
    else:
        pem_file = os.path.join(os.path.expanduser('~'), f'{key_name}.pem')
        with open(pem_file, 'w') as f:
            f.write(private_key)
        os.chmod(pem_file, 0o400)

ssh_client.close()
