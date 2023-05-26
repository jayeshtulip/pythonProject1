import boto3
import time
import sys
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Replace YOUR_REGION with the region where you want to create the VMs and volumes
CLUSTER_IP = '10.16.145.91'
#IMAGE_ID = 'ami-f57317037b5b45b4852cc8ecac50b381'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )
name_prefix = "my-test-22-04-2023-vm"

# Create the VMs and volumes
for i in range(1,2):
    '''
    vm_name = f"Testing vm {name_prefix}-{i}"
    vm = ec2.run_instances(
        ImageId="ami-855934314e554c2c8d2e6acd0e10d3f3",
        InstanceType="t2.micro",
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": vm_name
                    }
                ]
            }
        ]
    )
    instance_id = vm["Instances"][0]["InstanceId"]
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id, ])
    '''
    volume_name = f"Volume  {name_prefix}-volume-{i}"
    #print("tst1")
    volume_name = f"Scaling  {name_prefix}-volume-{i}"
    volume = ec2.create_volume(
        AvailabilityZone='symphony',
        Size=2,
        VolumeType='ssd-1',
        TagSpecifications=[
            {
                "ResourceType": "volume",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": volume_name
                    }
                ]
            }
        ]
    )
    # print the response to see the newly created volume details
    #print(response)

    #print("test2")
    '''

    volume_name1 = f"Scaling second  {name_prefix}-volume-{i}"
    volume1 = ec2.create_volume(
        AvailabilityZone='symphony',
        Size=2,
        VolumeType='ssd-1',
        TagSpecifications=[
            {
                "ResourceType": "volume",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": volume_name1
                    }
                ]
            }
        ]
    )
    '''
    volume_id = volume["VolumeId"]
    
    # Attach the volume to the VM
    waiter = ec2.get_waiter('volume_available')
    waiter.wait(VolumeIds=[volume_id, ])
    ec2.attach_volume(
        Device="/dev/sdm",
        InstanceId=instance_id,
        VolumeId=volume_id
    )
    print("Attached EBS: {0} to instance {1}:" .format(volume_id,instance_id))
