from botocore.exceptions import NoCredentialsError, ClientError
import boto3
import paramiko
import urllib3
import time
import re
import subprocess
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CLUSTER_IP = '10.16.145.79'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )

# Key pair name and file path
key_pair_name = 'vpc2'
private_key_path = r'C:\Users\jayes\Downloads\vpc2.pem'
key_permissions = 0o400
'''
try:
    # Create an EC2 client
    key_pair = ec2.create_key_pair(KeyName=key_pair_name)
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
        print("Key pair 'vpc-15' already exists.")
    else:
        print("An error occurred:", e)

'''
try:
    # Create key pair
    key_pair = ec2.create_key_pair(KeyName=key_pair_name)
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
        print("Key pair 'vpc-15' already exists.")
    else:
        print("An error occurred:", e)
finally:
    # Launch EC2 instance
    username = 'ubuntu'
    name_prefix = "test-25-05-2023-vm"
    for i in range(1,10):
       vm_name = f" {name_prefix}-{i}"
       vm = ec2.run_instances(
           ImageId="ami-045b56a405d14f36b04380715ef410a3",  # Debian 9 AMI
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
       #print(f'Allocation ID {eip_allocation["AllocationId"]}')
       #print(f'  - Elastic IP {eip_allocation["PublicIp"]} has been allocated')
       allocation_response1 = ec2.associate_address(
           InstanceId=instance_id,
           AllocationId=eip_allocation["AllocationId"]
       )
       volume_name = f"Volume {name_prefix}-volume-{i}"
       #print("tst1")
       volume = ec2.create_volume(
           AvailabilityZone='symphony',
           Size=10,
           VolumeType='199-vsa28-second',
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
       formatted_volume_id = re.sub(r'vol-([a-f0-9]{8})([a-f0-9]{4})([a-f0-9]{4})([a-f0-9]{4})([a-f0-9]{12})',
                                    r'\1-\2-\3-\4-\5', volume_id)
       # Attach the volume to the VM
       waiter = ec2.get_waiter('volume_available')
       waiter.wait(VolumeIds=[volume_id, ])
       ec2.attach_volume(
           Device="/dev/sdm",
           InstanceId=instance_id,
           VolumeId=volume_id
       )
       time.sleep(2)
       #print("Attached EBS: {0} to instance {1}:" .format(volume_id,instance_id))
       public_ip = eip_allocation["PublicIp"]
       time.sleep(40)
       try:
           ssh_client = paramiko.SSHClient()
           ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
           key = paramiko.RSAKey.from_private_key_file(private_key_path)
           ssh_client.connect(hostname=public_ip, username='ubuntu', pkey=key)
           '''
           #print("SSH connection established successfully!")
           stdin, stdout, stderr = ssh_client.exec_command('lsblk')
           # Read the command output
           output = stdout.read().decode('utf-8')
           # Print the output
           #print("lsblk output:\n", output)
           time.sleep(2)
           mkdirectory_command = "sudo mkdir myvolume"
           stdin, stdout, stderr = ssh_client.exec_command(mkdirectory_command)
           list_command = "ls -l"
           stdin, stdout, stderr = ssh_client.exec_command(list_command)
           output2 = stdout.read().decode('utf-8')
           #print("list command  output:\n", output2)
           mkfs_command = "sudo mkfs.ext4 /dev/vdb"
           stdin, stdout, stderr = ssh_client.exec_command(mkfs_command)
           time.sleep(2)
           mnt_command = "sudo mount /dev/vdb myvolume"
           stdin, stdout, stderr = ssh_client.exec_command(mnt_command)
           output4 = stdout.read().decode('utf-8')
           #print(output4)
           time.sleep(10)
           move_command = "cd /home/ubuntu/myvolume"
           stdin, stdout, stderr = ssh_client.exec_command(move_command)
           time.sleep(2)
           pwd_command = "pwd"
           stdin, stdout, stderr = ssh_client.exec_command(pwd_command)
           output5 = stdout.read().decode('utf-8')
           #print("pwd command  output:\n", output5)
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
           #print("dd command  output:\n", output6)
           '''
           commands = [
               'lsblk',
               'sudo mkdir myvolume',
               'sudo mkfs.ext4 /dev/vdb',
               'sudo mount /dev/vdb myvolume',
               'cd /home/ubuntu/myvolume',
               f'sudo dd if=/dev/zero of=/home/ubuntu/myvolume/file.txt bs=1M count=5000'

           ]
           ec2.create_snapshot(VolumeId=volume_id, Description="Snapshot of EC2 instance{i}")
           ec2.create_snapshot(VolumeId=volume_id)
           for command in commands:
               stdin, stdout, stderr = ssh_client.exec_command(command)
               output = stdout.read().decode('utf-8')
               error = stderr.read().decode('utf-8')
               print(f'Command: {command}\nOutput: {output}\nError: {error}\n')
               time.sleep(2)
           stdin, stdout, stderr = ssh_client.exec_command('df -h')
           output7 = stdout.read().decode('utf-8')
           # Print the output
           #print(output7)
           pattern = r'/dev/vdb\s+\d+M\s+\d+M\s+\d+M\s+(\d+)%'
           match = re.search(pattern, output7)
           if match:
               usage_percentage = int(match.group(1))
               if usage_percentage > 70:
                   #print("{name_prefix}-{i}Usage of Volume: {0} is more than 70 %:".format(volume_id),{name_prefix}-{i},"\n")
                   print(f"{name_prefix}-{i} vm, attached Volume {volume_id} usage is more than 70 % \n ")
                   print(f"Taking snapshot of {volume_id}")
                   ec2.create_snapshot(VolumeId=volume_id)
                   time.sleep(2)
               else:
                   print(f"{name_prefix}-{i} vm, attached Volume {volume_id} usage is less than 70 % \n ")
           else:
               print("No match found for /dev/vdb")
           ssh_client.close()
           ssh_client = paramiko.SSHClient()
           ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
           ssh_client.connect('10.16.4.189', username = 'root', password = 'rackattack')
           print("\n\nconncted to host sucessfully\n\n")
           command_symp1=f'symp -u user2 -d account2 -r vpc2-project -p Cloud@2024 -k volume retype {formatted_volume_id} --new-volume-type-id a92326d0-27ef-431e-9a58-60dd3185fc3a'
           stdin, stdout, stderr = ssh_client.exec_command(command_symp1)
           time.sleep(2)
           five = stdout.read().decode('utf-8')
           print("volume migration done\n", five)
           ssh_client.close()
       except Exception as e:
           print(f"An unexpected error occurred: {str(e)}")
       #finally:
           #if ssh_client is not None and ssh_client.get_transport() is not None:
               #ssh_client.close()

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
    formatted_volume_id1 = re.sub(r'vol-([a-f0-9]{8})([a-f0-9]{4})([a-f0-9]{4})([a-f0-9]{4})([a-f0-9]{12})',
                                 r'\1-\2-\3-\4-\5', volume_id)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect('10.16.4.189', username='root', password='rackattack')
    print("\n\nconncted to host second time sucessfully\n\n")
    command_symp2 = f'symp -u user2 -d account2 -r vpc2-project -p Cloud@2024 -k volume retype {formatted_volume_id1} --new-volume-type-id d6ad91a0-5eff-4b59-9452-5553e7a6ac32 --vpsa-id  04b08752-b68b-4120-a35b-8cb200a312ca'
    stdin, stdout, stderr = ssh_client.exec_command(command_symp2)
    time.sleep(2)
    five = stdout.read().decode('utf-8')
    print("volume migration done\n", five)
    ssh_client.close()
    #response = ec2.delete_volume(VolumeId=volume_id)
    #print("Deleted volume:", volume_id)


