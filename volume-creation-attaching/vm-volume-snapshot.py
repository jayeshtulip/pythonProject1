import urllib3
import time
import boto3
import paramiko
import sys

# Set up the Boto3 client for EC2 (Elastic Compute Cloud)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Replace YOUR_REGION with the region where you want to create the VMs and volumes
CLUSTER_IP = '172.16.10.80'
#IMAGE_ID = 'ami-f57317037b5b45b4852cc8ecac50b381'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )
# Create the VMs
name_prefix = "my-test-02-01-10-vm"
vm_instances = []
for i in range(2):
    vm_name = f"Testing{name_prefix}-{i}"
    vm = ec2.run_instances(
        ImageId="ami-3b6e4a9810e94b8fa2d6b7a751b5a499",  # Debian 9 AMI
        InstanceType="t2.micro",
        MaxCount=1,
        MinCount=1,
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

  # Create the volumes
    volumes = []
    volume_name = f"Testing volume {name_prefix}-{i}"
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
    # print("test2")
    volume_id = volume["VolumeId"]
    print("volume creation")

# Attach the volumes to the VMs

    ec2.attach_volume(
        VolumeId=volume_id,
        InstanceId=vm_instances[i]['InstanceId'],
        Device='/dev/sdm'  # Replace with the desired device name
    )
    time.sleep(10)

    ec2.attach_volume(
        Device="/dev/sdm",
        InstanceId=instance_id,
        VolumeId=volume_id
    )

# Install Nginx on each VM
for i in range(2):
    # Connect to the VM using SSH
    # (Replace the key pair and user name with the ones you specified when you created the VM)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(vm_instances[i]['PublicIp'], username='ubuntu', key_filename='lcs-03-01.ppk')

    # Install Nginx
    stdin, stdout, stderr = ssh_client.exec_command('sudo yum install -y nginx')
    stdout.read()  # Read the output to prevent hanging
    print("paramiko")
    time.sleep(10)

# Create snapshots of each volume
for i in range(2):
    ec2.create_snapshot(VolumeId=volumes[i])
    time.sleep(10)
    print("test2")
