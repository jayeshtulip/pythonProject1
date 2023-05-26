import boto3

# Create a boto3 client for the EC2 service
ec2 = boto3.client('ec2')

# Create a VPC
vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
vpc_id = vpc_response['Vpc']['VpcId']

# Create a subnet
subnet_response = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.0.0/24')
subnet_id = subnet_response['Subnet']['SubnetId']

# Create an application load balancer
elbv2 = boto3.client('elbv2')
load_balancer_response = elbv2.create_load_balancer(
    Name='my-load-balancer',
    Subnets=[subnet_id]
)
load_balancer_arn = load_balancer_response['LoadBalancers'][0]['LoadBalancerArn']

# Create three EC2 instances
instance_response = ec2.run_instances(
    ImageId='ami-12345678',
    MinCount=3,
    MaxCount=3,
    SubnetId=subnet_id,
    InstanceType='t2.micro'
)
instance_ids = [instance['InstanceId'] for instance in instance_response['Instances']]

# Wait for the instances to be in the running state
ec2.wait_until_instances_running(InstanceIds=instance_ids)

# Attach the instances as targets to the load balancer
elbv2.register_targets(
    TargetGroupArn='my-target-group-arn',
    Targets=[{'Id': instance_id} for instance_id in instance_ids]
)

# Delete the EC2 instances
ec2.terminate_instances(InstanceIds=instance_ids)

# Wait for the instances to be terminated
ec2.wait_until_instances_terminated(InstanceIds=instance_ids)

# Delete the load balancer
elbv2.delete_load_balancer(LoadBalancerArn=load_balancer_arn)

# Delete the subnet
ec2.delete_subnet(SubnetId=subnet_id)

# Delete the VPC
ec2.delete_vpc(VpcId=vpc_id)