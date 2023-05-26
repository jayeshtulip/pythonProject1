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
name_prefix = "test-12-May"
# Create the VMs and volumes
# Key pair details
# Specify the key pair name
key_pair_name = 'my-key-pair12'

# Create the key pair
response = ec2.create_key_pair(KeyName=key_pair_name)

# Save the private key file locally
private_key_path = r'C:\Users\jayes\Downloads\test.pem'
private_key_content = response['KeyMaterial']
with open(private_key_path, 'w') as key_file:
    key_file.write(private_key_content)

# Set permissions on the private key file
os.chmod(private_key_path, 0o600)
username = 'ubuntu'
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
    #ec2.create_snapshot(VolumeId=volume_id, Description="Snapshot of EC2 instance{i}")

        #ec2.create_snapshot(VolumeId=volume_id)
        #time.sleep(2)
    # Create an SSH client and configure it with the private key
    public_ip=eip_allocation["PublicIp"]
    key = paramiko.RSAKey.from_private_key_file(private_key_path)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=public_ip, username='ubuntu', pkey=key)
        stdin, stdout, stderr = ssh_client.exec_command('echo "Hello, world!"')
        output = stdout.read().decode()
        print(output)
        # Close the SSH connection
        ssh_client.close()
    except NoCredentialsError:
        print("AWS credentials could not be found.")
    except ClientError as e:
        print("An error occurred while connecting to the instance:", e)
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your SSH key and username.")
    except paramiko.SSHException as ssh_exception:
        print("An error occurred while establishing SSH connection:", ssh_exception)
    except Exception as e:
        print("An error occurred:", e)



    # Run a command on the instance


    # Connect to the VM using the Elastic IP address and private key
    '''
    time.sleep(2)
    mkdirectory_command = "sudo mkdir myvolume"
    stdin, stdout, stderr = ssh_client.exec_command(mkdirectory_command)
    mkfs_command = "sudo mkfs.ext4 /dev/vdb"
    stdin, stdout, stderr = ssh_client.exec_command(mkfs_command)
    time.sleep(2)
    mnt_command = "mount /dev/vdb myvolume"
    stdin, stdout, stderr = ssh_client.exec_command(mnt_command)
    device_name = '/dev/vdb'
    # Execute the dd command to write data to the attached volume
    dd_command = f"dd if=/path/to/source/file of={device_name}"
    stdin, stdout, stderr = ssh_client.exec_command(dd_command)

    # Wait for the command to complete
    stdout.channel.recv_exit_status()

    # Check disk usage using df -h
    df_command = "df -h"
    stdin, stdout, stderr = ssh_client.exec_command(df_command)
    disk_usage = stdout.read().decode('utf-8')
    print("Disk Usage:\n", disk_usage)

    # Check volume presence using lsblk
    lsblk_command = "lsblk"
    stdin, stdout, stderr = ssh_client.exec_command(lsblk_command)
    volume_info = stdout.read().decode('utf-8')
    print("Volume Info:\n", volume_info)

    # Close the SSH connection
    ssh_client.close()
    '''
