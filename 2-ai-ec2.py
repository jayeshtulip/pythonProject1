import boto3

# Create a boto3 client for EC2
CLUSTER_IP = '10.16.146.105'

# Create an EC2 client
#ec2 = boto3.client('ec2')
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )


# Create two EC2 instances
response = ec2.run_instances(
    ImageId='ami-44df8b3e31964f359dccc90c54210ba0',
    MinCount=2,
    MaxCount=2,
    InstanceType='t2.micro'
)

# Get the IDs of the two instances
instance_ids = [instance['InstanceId'] for instance in response['Instances']]

# Allocate an Elastic IP address for each instance
for instance_id in instance_ids:
    response = ec2.allocate_address(Domain='vpc')
    elastic_ip = response['AllocationId']
    ec2.associate_address(InstanceId=instance_id, AllocationId=elastic_ip)

# Now you can ping each instance using their Elastic IP addresses
