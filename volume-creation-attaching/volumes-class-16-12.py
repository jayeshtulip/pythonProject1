import boto3
import time
class EC2Manager:
    def __init__(self):
        CLUSTER_IP = '10.16.146.12'
        self.ec2 = boto3.client(
        service_name="ec2", region_name="zCompute",
        endpoint_url="https://%s/api/v2/ec2/" % CLUSTER_IP,
        verify=False
        )
        self.instances = []
        self.volumes = []

    def launch_instance(self, image_id, instance_type):
        response = self.ec2.run_instances(
            ImageId=image_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type
        )
        self.instances.append(response['Instances'][0]['InstanceId'])
        time.sleep(50)
        #waiter = self.ec2.get_waiter('instance_running')
        #waiter.wait(InstanceIds=[instance_id, ])

    def create_volume(self, availability_zone, size):
        response = self.ec2.create_volume(
            AvailabilityZone=availability_zone,
            Size=size
        )
        time.sleep(10)
        #waiter = self.ec2.get_waiter('volume_available')
        #waiter.wait(VolumeIds=[volume_id, ])
        self.volumes.append(response['VolumeId'])

    def attach_volume(self, instance_id, volume_id, device):
        self.ec2.attach_volume(
            VolumeId=volume_id,
            InstanceId=instance_id,
            Device=device
        )
        time.sleep(10)
    def detach_volume(self, instance_id, volume_id, device):
        self.ec2.detach_volume(
            VolumeId=volume_id,
            InstanceId=instance_id,
            Device=device,
            Force=True
        )
        time.sleep(10)
    def delete_volume(self, volume_id):
        self.ec2.delete_volume(VolumeId=volume_id)
        self.volumes.remove(volume_id)

    def terminate_instance(self, instance_id):
        self.ec2.terminate_instances(InstanceIds=[instance_id])
        self.instances.remove(instance_id)

# Create an EC2Manager object
manager = EC2Manager()

# Launch three new EC2 instances
for i in range(1,20):
    manager.launch_instance('ami-58fb95f0fa484ce091e21a363db302f8', 't2.micro')
# Create three new EBS volumes
    manager.create_volume('symphony', 1)
    manager.attach_volume(manager.instances[i], manager.volumes[i], '/dev/sdm')
    manager.detach_volume(manager.instances[i], manager.volumes[i], '/dev/sdm')
    manager.delete_volume(volume_id)

# Detach the volumes from the instances
'''
for i in range(3):
    manager.detach_volume(manager.instances[i], manager.volumes[i], '/dev/sdm')
    time.sleep(500)


time.sleep(500)

# Delete the volumes
for volume_id in manager.volumes:
    manager.delete_volume(volume_id)
    time.sleep(500)


time.sleep(500)

# Terminate the instances
for instance_id in manager.instances:
    manager.terminate_instance(instance_id)
    time.sleep(500)

'''