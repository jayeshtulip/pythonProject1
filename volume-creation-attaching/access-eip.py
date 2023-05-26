import boto3
import paramiko
CLUSTER_IP = '10.16.145.91'
#IMAGE_ID = 'ami-f57317037b5b45b4852cc8ecac50b381'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )
response = ec2.describe_instances(InstanceIds=[instance_id])
instance_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
private_key_path = 'C:/Users/jayes/Downloads/20-04.pem'
private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
ssh_client.connect(hostname=instance_ip, username='your_username', pkey=private_key)

# Replace /dev/xvdf with the appropriate volume device name
# Replace /path/to/source/file with the path to the source file you want to write to the volume
# Replace /dev/xvdg with the appropriate volume device name or path where you want to write the data
command = "dd if=/path/to/source/file of=/dev/xvdg"
stdin, stdout, stderr = ssh_client.exec_command(command)
# Wait for the command to complete
stdout.channel.recv_exit_status()
# Execute the dd command
command = "dd if=/path/to/source/file of=/dev/xvdg"
stdin, stdout, stderr = ssh_client.exec_command(command)
stdout.channel.recv_exit_status()

# Check disk usage using df -h
command = "df -h"
stdin, stdout, stderr = ssh_client.exec_command(command)
disk_usage = stdout.read().decode('utf-8')
print("Disk Usage:\n", disk_usage)

# Check volume presence using lsblk
command = "lsblk"
stdin, stdout, stderr = ssh_client.exec_command(command)
volume_info = stdout.read().decode('utf-8')
print("Volume Info:\n", volume_info)


