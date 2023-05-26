import boto3

# Create a boto3 client for the EC2 service
CLUSTER_IP = '10.16.146.105'

# Create an EC2 client
#ec2 = boto3.client('ec2')
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )

def test_create_volume():
    # Create a new volume in the specified availability zone
    response = ec2.create_volume(
        AvailabilityZone='us-east-1a',
        Size=100
    )
    print("successfull")
    # Ensure that the volume was created successfully
    assert 'VolumeId' in response
print(response['VolumeId'])


'''
second script


import boto3
import pytest

# create an AWS client
ec2 = boto3.client('ec2')

def test_create_volume():
    # create an EBS volume
    response = ec2.create_volume(
        Size=1,  # size of the volume in GB
        AvailabilityZone='us-east-1a',  # availability zone
        VolumeType='gp2'  # volume type
    )

    # assert that the volume was created successfully
    assert 'VolumeId' in response

    # get the volume ID
    volume_id = response['VolumeId']

    # get information about the volume
    volume_info = ec2.describe_volumes(VolumeIds=[volume_id])

    # assert that the volume has the expected size
    assert volume_info['Volumes'][0]['Size'] == 1

    # assert that the volume has the expected availability zone
    assert volume_info['Volumes'][0]['AvailabilityZone'] == 'us-east-1a'

    # assert that the volume has the expected type
    assert volume_info['Volumes'][0]['VolumeType'] == 'gp2'
'''