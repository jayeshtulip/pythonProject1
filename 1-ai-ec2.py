import boto3

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
    InstanceType='t2.micro',
    MinCount=2,
    MaxCount=2
)

# Get the IDs of the instances
instance_ids = [i['InstanceId'] for i in response['Instances']]

# Wait for the instances to be in the 'running' state
#ec2.wait_until_instances_running(InstanceIds=instance_ids)

# Get the Elastic IPs of the instances
response = ec2.describe_instances(InstanceIds=instance_ids)
instance_ips = [i['PublicIpAddress'] for r in response['Reservations'] for i in r['Instances']]

# Ping each instance using its Elastic IP
for ip in instance_ips:
    response = ec2.ping(InstanceId=ip)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f"Instance at {ip} is reachable")
    else:
        print(f"Instance at {ip} is NOT reachable")
