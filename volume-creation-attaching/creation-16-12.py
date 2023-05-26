import boto3


# Create an EC2 client
CLUSTER_IP = '10.16.146.48'
#IMAGE_ID = 'ami-f57317037b5b45b4852cc8ecac50b381'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="symphony",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )

# Launch a new EC2 instance
response = ec2.run_instances(
    ImageId='ami-f325fbe488974f58ba5b30d6609d81b3',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro'
)

# Get the ID of the new instance
instance_id = response['Instances'][0]['InstanceId']

# Create an EBS volume
response = ec2.create_volume(
    AvailabilityZone="symphony",
    Size=1
)
print("jayesh")
# Get the ID of the new volume
volume_id = response['VolumeId']

# Attach the volume to the instance
response = ec2.attach_volume(
    VolumeId=volume_id,
    InstanceId=instance_id,
    Device='/dev/sdm'
)

# Detach the volume from the instance
response = ec2.detach_volume(
    VolumeId=volume_id,
    InstanceId=instance_id,
    Device='/dev/sdh',
    Force=True
)

# Delete the volume
response = ec2.delete_volume(
    VolumeId=volume_id
)
# Terminate the instance
response = ec2.terminate_instances(
    InstanceIds=[instance_id]
)
