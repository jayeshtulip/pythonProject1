import time
#Working#

import boto3

# Set up the EC2 client
CLUSTER_IP = '10.16.146.12'
#IMAGE_ID = 'ami-f57317037b5b45b4852cc8ecac50b381'
INSTANCE_TYPE = 't2.medium'
ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
    )

# List all instances
response = ''
instances = ''
response = ec2.describe_instances()
instances = response['Reservations']

# Loop through the instances and volumes
for instance in instances:
    instance_id = instance['Instances'][0]['InstanceId']
    volumes = instance['Instances'][0]['BlockDeviceMappings']

    # Print the instance ID and its volumes
    print("Instance ID:", instance_id)
    print("Volumes:")

    # Loop through the volumes attached to the instance
    for volume in volumes:
        volume_id = volume['Ebs']['VolumeId']
        print("testing", volume_id)
        try:
            # Detach the volume from the instance
            ec2.stop_instances(InstanceIds=[instance_id])

            # Wait for the instance to be stopped before terminating it
            ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])

            # Terminate the instance
            ec2.terminate_instances(InstanceIds=[instance_id])
            time.sleep(5)
            break
        except:
            ec2.detach_volume(
               VolumeId=volume_id,
               InstanceId=instance_id,
               Force=False
            )

            # Wait for the volume to detach
            waiter = ec2.get_waiter('volume_available')
            waiter.wait(VolumeIds=[volume_id])
            ec2.stop_instances(InstanceIds=[instance_id])

            # Wait for the instance to be stopped before terminating it
            ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])

            # Terminate the instance
            ec2.terminate_instances(InstanceIds=[instance_id])
            time.sleep(5)
            print("testing1")
            # Delete the volume
            ec2.delete_volume(VolumeId=volume_id)
            print("success")
            time.sleep(5)
            break
response = ec2.describe_volumes()
print("test2", response)
# Loop through each volume and delete it
for volume in response['Volumes']:
    volume_id = volume['VolumeId']
    response = ec2.delete_volume(VolumeId=volume_id)
    print("Deleted volume:", volume_id)


