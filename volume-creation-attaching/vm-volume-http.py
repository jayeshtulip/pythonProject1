import boto3
import paramiko

# Replace YOUR_REGION with the region where you want to create the VMs and volumes
region = "YOUR_REGION"

# Set the name and zone for the VMs and volumes
name_prefix = "my-vm"
zone = "us-east-1a"

# Create a client for the EC2 service
ec2 = boto3.client("ec2", region_name=region)

# Create the VMs and volumes
instance_ids = []
for i in range(20):
    # Create the VM
    vm_name = f"{name_prefix}-{i}"
    vm = ec2.run_instances(
        ImageId="ami-0ff8a91507f77f867",  # Debian 9 AMI
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
    instance_ids.append(instance_id)

    # Create the volume
    volume_name = f"{name_prefix}-volume-{i}"
    volume = ec2.create_volume(
        AvailabilityZone=zone,
        Size=2,
        VolumeType="gp2",
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
    volume_id = volume["VolumeId"]

    # Attach the volume to the VM
    ec2.attach_volume(
        Device="/dev/sda1",
        InstanceId=instance_id,
        VolumeId=volume_id
    )

# Wait for the VMs to be in the running state
ec2.get_waiter("instance_running").
# Install an HTTP server on each VM
for instance_id in instance_ids:
    # Get the public IP address of the VM
    instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]
    public_ip = instance["PublicIpAddress"]

    # Connect to the VM using SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_ip, username="ec2-user")

    # Install the HTTP server
    stdin, stdout, stderr = ssh.exec_command("sudo apt-get update && sudo apt-get install -y apache2")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"Successfully installed HTTP server on VM {instance_id}")
    else:
        print(f"Failed to install HTTP server on VM {instance_id}: {stderr.read().decode('utf-8')}")

    # Close the SSH connection
    ssh.close()

# Create an image of the VMs
image_name = "my-vm-image"
image_description = "An image of the my-vm VMs"
image = ec2.create_image(
    InstanceId=instance_ids[0],
    Name=image_name,
    Description=image_description,
    NoReboot=True
)
image_id = image["ImageId"]
print(f"Created image with ID {image_id}")
