from botocore.exceptions import NoCredentialsError, ClientError
import boto3
import paramiko
import urllib3
import time
import subprocess
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CLUSTER_IP = '10.16.146.44'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )

# Key pair name and file path
key_pair_name = 'vpc-15'
private_key_path = r'C:\Users\jayes\Downloads\vpc-15.pem'
key_permissions = 0o400
try:
    # Create key pair
    key_pair = ec2.create_key_pair(KeyName=key_pair_name)
except ec2.exceptions.KeyPairAlreadyExists:
    print("Key pair already exists. Proceeding with further steps.")
    print("continue")
finally:
    # Launch EC2 instance
    username = 'ubuntu'
    name_prefix = "my-test-14-05-2023-vm"
    for i in range(1,2):
       vm_name = f" {name_prefix}-{i}"
       vm = ec2.run_instances(
           ImageId="ami-4ced6aae52914335a3512ea08645feef",  # Debian 9 AMI
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
       time.sleep(40)
       try:
           ssh_client = paramiko.SSHClient()
           ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
           key = paramiko.RSAKey.from_private_key_file(private_key_path)
           ssh_client.connect(hostname=public_ip, username='ubuntu', pkey=key)
           print("SSH connection established successfully!")
           stdin, stdout, stderr = ssh_client.exec_command('lsblk')
           # Read the command output
           output = stdout.read().decode('utf-8')
           # Print the output
           print("lsblk output:\n", output)
           time.sleep(2)
           mkdirectory_command = "sudo mkdir myvolume"
           stdin, stdout, stderr = ssh_client.exec_command(mkdirectory_command)
           list_command = "ls -l"
           stdin, stdout, stderr = ssh_client.exec_command(list_command)
           output2 = stdout.read().decode('utf-8')
           print("list command  output:\n", output2)
           mkfs_command = "sudo mkfs.ext4 /dev/vdb"
           stdin, stdout, stderr = ssh_client.exec_command(mkfs_command)
           time.sleep(2)
           mnt_command = "sudo mount /dev/vdb myvolume"
           stdin, stdout, stderr = ssh_client.exec_command(mnt_command)
           output4 = stdout.read().decode('utf-8')
           print(output4)
           time.sleep(10)
           move_command = "cd /home/ubuntu/myvolume"
           stdin, stdout, stderr = ssh_client.exec_command(move_command)
           time.sleep(2)
           pwd_command = "pwd"
           stdin, stdout, stderr = ssh_client.exec_command(pwd_command)
           output5 = stdout.read().decode('utf-8')
           print("pwd command  output:\n", output5)
           time.sleep(2)
           #device_name = 'home/ubuntu/myvolume'
           # Execute the dd command to write data to the attached volume
           #dd_command = f"sudo dd if=/path/to/source/file of=/dev/{device_name}"
           #dd_command = f"sudo dd if =/dev/zero of = bs = 1M count = 500"
           #dd_command = f'sudo dd if=/dev/zero of={device_name} bs=1M count=900'
           dd_command = f'sudo dd if=/dev/zero of=/home/ubuntu/myvolume/file.txt bs=1M count=800'
           stdin, stdout, stderr = ssh_client.exec_command(dd_command)
           time.sleep(2)
           output6 = stdout.read().decode('utf-8')
           print("dd command  output:\n", output6)

           stdin, stdout, stderr = ssh_client.exec_command('df -h')
           output7 = stdout.read().decode('utf-8')
           # Print the output
           print(output7)
           pattern = r'/dev/vdb\s+\d+M\s+\d+M\s+\d+M\s+(\d+)%'
           match = re.search(pattern, output7)
           if match:
               usage_percentage = int(match.group(1))
               if usage_percentage > 70:
                   print("Usage of Volume: {0} is more than 70 %:".format(volume_id))
               else:
                   print("Usage is below or equal to 70%")
           else:
               print("No match found for /dev/vdb")
           ssh_client.close()
       except paramiko.AuthenticationException:
           print("Authentication failed. Please check the private key and credentials.")
       except paramiko.SSHException as e:
           print(f"An error occurred while establishing the SSH connection: {str(e)}")
       except Exception as e:
           print(f"An unexpected error occurred: {str(e)}")
       finally:
           if ssh_client is not None and ssh_client.get_transport() is not None:
               ssh_client.close()

