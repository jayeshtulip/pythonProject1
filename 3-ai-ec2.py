import boto3

# Create a boto3 client for EC2
ec2 = boto3.client('ec2')

try:
    # Create two EC2 instances
    response = ec2.run_instances(
        ImageId='ami-0123456789abcdef',  # Replace this with the ID of an AMI in your account
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

    print(f"Successfully created instances with IDs: {instance_ids}")

except Exception as e:
    print(f"An error occurred: {e}")
