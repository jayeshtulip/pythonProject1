import boto3
import time
import sys
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CLUSTER_IP = '10.16.145.79'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )
'''
name_prefix = "test-05-May"
# Create the VMs and volumes
for i in range(1,100):
    vm_name = f" {name_prefix}-{i}"
    vm = ec2.run_instances(
        ImageId="ami-8bfdb0ad7ffe47ef89a770e0526eb917",  # Debian 9 AMI
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

    volume_name = f"Volume {name_prefix}-volume-{i}"
    #print("tst1")
    volume = ec2.create_volume(
        AvailabilityZone='symphony',
        Size=1,
        VolumeType='vt-boto3',
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
    time.sleep(2)
    print("Attached EBS: {0} to instance {1}:" .format(volume_id,instance_id))
    #ec2.create_snapshot(VolumeId=volume_id, Description="Snapshot of EC2 instance{i}")

    ec2.create_snapshot(VolumeId=volume_id)
    time.sleep(2)
'''
response = ''
instances = ''
response = ec2.describe_instances()
instances = response['Reservations']

# Loop through the instances and volumes
for instance in instances:
    instance_id = instance['Instances'][0]['InstanceId']
    volumes = instance['Instances'][0]['BlockDeviceMappings']

    # Print the instance ID and its volumes
    print("Instance ID:", instance_id)
    print("Volumes:")

    # Loop through the volumes attached to the instance
    for volume in volumes:
        volume_id = volume['Ebs']['VolumeId']
        print("testing", volume_id)
        try:
            # Detach the volume from the instance
            ec2.stop_instances(InstanceIds=[instance_id])

            # Wait for the instance to be stopped before terminating it
            ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])

            # Terminate the instance
            ec2.terminate_instances(InstanceIds=[instance_id])
            time.sleep(5)
            break
        except:
            ec2.detach_volume(
               VolumeId=volume_id,
               InstanceId=instance_id,
               Force=False
            )

            # Wait for the volume to detach
            waiter = ec2.get_waiter('volume_available')
            waiter.wait(VolumeIds=[volume_id])
            ec2.stop_instances(InstanceIds=[instance_id])

            # Wait for the instance to be stopped before terminating it
            ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])

            # Terminate the instance
            ec2.terminate_instances(InstanceIds=[instance_id])
            time.sleep(5)
            print("testing1")
            # Delete the volume
            break
response = ec2.describe_volumes()
print("test2", response)
# Loop through each volume and delete it
for volume in response['Volumes']:
    volume_id = volume['VolumeId']
    response = ec2.delete_volume(VolumeId=volume_id)
    print("Deleted volume:", volume_id)
    break

'''
    # Replace with the IP address or hostname of your EC2 instance
    hostname = eip_allocation["PublicIp"]

    # Replace with the username for your EC2 instance
    username = "zadara"

    # Replace with the password for your EC2 instance
    password = "zadara"

    # Create a new SSH client
    client = paramiko.SSHClient()

    # Set missing host key policy to AutoAddPolicy
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the EC2 instance
    client.connect(hostname=hostname, username=username, password=password)

    # Execute the command to install nginx
    stdin, stdout, stderr = client.exec_command("sudo yum install -y nginx")

    # Print the output of the command
    print(stdout.read())

    # Close the SSH client
    client.close()

    '''
