import pytest
import boto3
''''To run this test, you would need to install pytest and boto3, and then run the pytest command in the same directory
 as the script.Please note that this is just a sample script and you may need to modify it to fit your specific use case. 
 For example, you would need to provide a valid AMI ID in the ImageId parameter when calling the create_instances() method.
  Additionally, you may need to adjust the availability zone and device name based on your requirements.'''

@pytest.fixture
def ec2_resource():
    # Create an EC2 resource object
    ec2 = boto3.resource('ec2')
    return ec2

def test_spawn_vm_create_volume_attach_volume(ec2_resource):
    # Spawn a new EC2 instance
    instance = ec2_resource.create_instances(
        ImageId='ami-12345678',
        MinCount=1,
        MaxCount=1
    )
    instance_id = instance[0].id

    # Create an EBS volume
    volume = ec2_resource.create_volume(
        Size=8,
        AvailabilityZone='us-east-1a'
    )
    volume_id = volume.id

    # Attach the volume to the EC2 instance
    ec2_resource.attach_volume(
        VolumeId=volume_id,
        InstanceId=instance_id,
        Device='/dev/xvdf'
    )

    # Verify that the volume is attached
    volume = ec2_resource.Volume(volume_id)
    assert volume.state == 'in-use'
