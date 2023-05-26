from botocore.exceptions import NoCredentialsError, ClientError
import boto3
import paramiko
import urllib3
import time
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CLUSTER_IP = '10.16.145.159'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )
key_pair_name = 'key-14-05'
response = ec2.create_key_pair(KeyName=key_pair_name)
private_key_path = r'C:\Users\jayes\Downloads\key-14-05.pem'
private_key_content = response['KeyMaterial']
key_permissions = 0o400
os.chmod(private_key_path, key_permissions)

# Validate the permissions
stat_info = os.stat(private_key_path)
file_permissions = stat_info.st_mode & 0o400 # Extract the permissions from the file's mode

if file_permissions == key_permissions:
    print("Correct permissions set for the file.")
else:
    print("Permissions mismatch for the file.")
with open(private_key_path, 'w') as key_file:
    key_file.write(private_key_content)

# Set permissions on the private key file

username = 'ubuntu'
name_prefix = "my-test-13-05-2023-vm"
for i in range(1,2):
    vm_name = f" {name_prefix}-{i}"
    vm = ec2.run_instances(
        ImageId="ami-4b1eb7cfe99147ca93f6abdc90a17d8f",  # Debian 9 AMI
        InstanceType="t2.micro",
        KeyName=key_pair_name,
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
    public_ip = eip_allocation["PublicIp"]
    #ec2.create_snapshot(VolumeId=volume_id, Description="Snapshot of EC2 instance{i}")
    try:
        # Create a Paramiko SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the PPK key
        key = paramiko.RSAKey.from_private_key_file(private_key_path)

        # Connect to the VM using the private key and username
        ssh_client.connect(hostname=public_ip, username='ubuntu', pkey=key)

        # Perform operations on the VM
        stdin, stdout, stderr = ssh_client.exec_command('ls -l')

        # Print the output
        print(stdout.read().decode())

        # Close the SSH connection
        ssh_client.close()

    except ClientError as e:
        print("An error occurred while connecting to the instance:", e)

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your SSH key and username.")

    except paramiko.SSHException as ssh_exception:
        print("An error occurred while establishing SSH connection:", ssh_exception)

    except Exception as e:
        print("An error occurred:", e)
