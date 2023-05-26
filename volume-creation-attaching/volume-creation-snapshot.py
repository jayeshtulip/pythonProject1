import boto3

# Replace with your AWS access key and secret key
aws_access_key_id = "ACCESS_KEY"
aws_secret_access_key = "SECRET_KEY"

# Create an EC2 client
ec2 = boto3.client("ec2", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Create 10 EC2 instances
for i in range(10):
    response = ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro"
    )

# Get the ID of each EC2 instance
instance_ids = [instance["InstanceId"] for instance in response["Instances"]]

# Create 10 EBS volumes
for i in range(10):
    response = ec2.create_volume(
        Size=1,
        AvailabilityZone="us-east-1a"
    )

# Get the ID of each EBS volume
volume_ids = [volume["VolumeId"] for volume in response["Volumes"]]

# Attach the EBS volumes to the EC2 instances
for i in range(10):
    ec2.attach_volume(
        VolumeId=volume_ids[i],
        InstanceId=instance_ids[i],
        Device="/dev/sdh"
    )

# Take snapshots of the EC2 instances
for i in range(10):
    ec2.create_snapshot(
        VolumeId=volume_ids[i],
        Description="Snapshot of EC2 instance"
    )

# Detach the EBS volumes from the EC2 instances
for i in range(10):
    ec2.detach_volume(
        VolumeId=volume_ids[i]
    )

# Delete the EBS volumes
for i in range(10):
    ec2.delete_volume(
        VolumeId=volume_ids[i]
    )

# Terminate the EC2 instances
for i in range(10):
    ec2.terminate_instances(
        InstanceIds=[instance_ids[i]]
    )
