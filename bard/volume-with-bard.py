import boto3

# Get the session
session = boto3.Session()

# Create the EC2 client
ec2 = session.client('ec2')

# Create the volume
volume_size = 10
volume_type = 'gp2'
volume_name = 'my-volume'

response = ec2.create_volume(
  Size=volume_size,
  VolumeType=volume_type,
  TagSpecifications=[
    {
      'ResourceType': 'volume',
      'Tags': [
        {
          'Key': 'Name',
          'Value': volume_name
        }
      ]
    }
  ]
)

# Get the volume ID
volume_id = response['VolumeId']

# Wait for the volume to be created
ec2.wait_until_volume_available(VolumeId=volume_id)

# Create the VM
instance_type = 't2.micro'
ami_id = 'ami-0123456789abcdef0'
key_name = 'my-key-pair'

response = ec2.run_instances(
  InstanceType=instance_type,
  ImageId=ami_id,
  KeyName=key_name,
  TagSpecifications=[
    {
      'ResourceType': 'instance',
      'Tags': [
        {
          'Key': 'Name',
          'Value': 'my-instance'
        }
      ]
    }
  ]
)

# Get the instance ID
instance_id = response['Instances'][0]['InstanceId']

# Wait for the instance to be running
ec2.wait_until_instance_running(InstanceId=instance_id)

# Attach the volume to the instance
device_name = '/dev/xvdf'

response = ec2.attach_volume(
  VolumeId=volume_id,
  InstanceId=instance_id,
  Device=device_name
)

# Wait for the volume to be attached
ec2.wait_until_volume_in_use(VolumeId=volume_id)

# Get the instance public IP address
public_ip_address = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['PublicIpAddress']

# SSH to the instance
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(public_ip_address, username='ubuntu', password='password')

# Mount the volume
command = 'sudo mount /dev/xvdf /mnt'
stdin, stdout, stderr = ssh_client.exec_command(command)

# Write data to the volume
command = 'dd if=/dev/urandom of=/mnt/testfile bs=1M count=10'
dd if=/dev/urandom of=1gb.dat bs=1M count=1024 verify
stdin, stdout, stderr = ssh_client.exec_command(command)

# Check that the data was written
command = 'cat /mnt/testfile'
stdin, stdout, stderr = ssh_client.exec_command(command)

# Close the SSH connection
ssh_client.close()

# Validate that the write data went fine
assert stdout.read().strip() == b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
