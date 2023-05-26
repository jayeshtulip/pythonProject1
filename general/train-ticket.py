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

# Key pair name and file path
key_pair_name = 'key-19-05'
private_key_path = r'C:\Users\jayes\Downloads\key-19-05.pem'
key_permissions = 0o400
try:
    # Create key pair
    key_pair = ec2.create_key_pair(KeyName=key_pair_name)
    private_key_content = key_pair['KeyMaterial']

    # Save private key to file
    with open(private_key_path, 'w') as key_file:
       key_file.write(private_key_content)

    # Set permissions on the file
    os.chmod(private_key_path, key_permissions)
except ec2.exceptions.KeyPairAlreadyExists:
    print("Key pair already exists. Proceeding with further steps.")
    print("continue")
# Launch EC2 instance
username = 'ubuntu'
name_prefix = "my-test-18-05-2023-vm"
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

    # Create a test file on the VM
    public_ip = eip_allocation["PublicIp"]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    '''
    # Load the PPK key
    try:
        key = paramiko.RSAKey.from_private_key_file(private_key_path)
        print("The .ppk file was loaded successfully.")
    except paramiko.PasswordRequiredException:
        print("The .ppk file is password-protected. Provide the password to load it.")
    except paramiko.SSHException:
        print("Failed to load the .ppk file.")
    except FileNotFoundError:
        print("The specified .ppk file does not exist.")
    except paramiko.PEMException:
        print("The .ppk file is in an invalid format.")
    '''
    # Connect to the VM using the private key and username
    key = r'C:\Users\jayes\Downloads\key-19-05.ppk'
    ssh_client.connect(hostname=public_ip, username='ubuntu', pkey=key)

    # Perform operations on the VM
    stdin, stdout, stderr = ssh_client.exec_command('ls -l')

    # Print the output
    print(stdout.read().decode())

    # Close the SSH connection
    ssh_client.close()

