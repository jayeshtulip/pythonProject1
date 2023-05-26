import boto3

# Set the date you want to search for
search_date = '2022-12-14'

# Create an EC2 client
CLUSTER_IP = '10.16.146.105'

# Create an EC2 client
#ec2 = boto3.client('ec2')
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )

# Get a list of all the EBS volumes
volumes = ec2.describe_volumes()['Volumes']

# Iterate over the volumes and print the ones that were created on the specified date
for volume in volumes:
    if volume['CreateTime'].strftime('%Y-%m-%d') == search_date:
        print(volume['VolumeId'])
