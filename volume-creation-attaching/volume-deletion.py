import boto3

# Set up the client
CLUSTER_IP = '10.16.146.12'
#IMAGE_ID = 'ami-f57317037b5b45b4852cc8ecac50b381'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )
# List all volumes
print("test1")
response = ec2.describe_volumes()
print("test2", response)
# Loop through each volume and delete it
for volume in response['Volumes']:
    volume_id = volume['VolumeId']
    response = ec2.delete_volume(VolumeId=volume_id)
    print("Deleted volume:", volume_id)

