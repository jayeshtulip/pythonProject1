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
        #self.instances = []
        #self.volumes = []
    def launch_instance(self, image_id, instance_type):
        name_prefix = "my-test-17-01-10-vm"
        vm_name = f"{name_prefix}-{i}"
        response = self.ec2.run_instances(
            ImageId=image_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            TagSpecifications = [
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
        waiter = self.ec2.get_waiter('instance_running')
        #waiter.wait(InstanceIds= response['Instances'][0]['InstanceId'])
        #waiter.wait(InstanceIds=[instance_id, ])
        waiter.wait(InstanceIds=[response['Instances'][0]['InstanceId'], ])
        #self.instances.append(response['Instances'][0]['InstanceId'])

        return response['Instances'][0]['InstanceId']


    def create_volume(self, availability_zone, size):
        name_prefix = "my-volume-test-17-01"
        volume_name = f"{name_prefix}-{i}"
        response = self.ec2.create_volume(
            AvailabilityZone=availability_zone,
            Size=size,
            TagSpecifications = [
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
        time.sleep(10)
        waiter = self.ec2.get_waiter('volume_available')
        #waiter.wait(VolumeIds=response['VolumeId'])
        #waiter.wait(VolumeIds=[volume_id, ])
        waiter.wait(VolumeIds=[response['VolumeId'], ])
        #self.volumes.append(response['VolumeId'])
        self.ec2.create_snapshot(
                VolumeId=response['VolumeId'],
                Description="Snapshot of EC2 instance",
                TagSpecifications = [
            {
                "ResourceType": "snapshot",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": response['VolumeId']
                    }
                ]
               }
            ]
        )
        return response['VolumeId']

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
        #self.ec2.volumes.remove(volume_id)
        time.sleep(10)

    def terminate_instance(self, instance_id):
        self.ec2.terminate_instances(InstanceIds=[instance_id])
        #self.instances.remove(instance_id)
        time.sleep(10)

# Create an EC2Manager object
manager = EC2Manager()
for i in range(50):
    Instance_Id = manager.launch_instance('ami-58fb95f0fa484ce091e21a363db302f8', 't2.micro')
    #time.sleep(20)
    Volume_Id = manager.create_volume('symphony', 1)
    #time.sleep(20)
    manager.attach_volume(Instance_Id,Volume_Id, '/dev/sdm')
    #time.sleep(20)
    manager.detach_volume(Instance_Id,Volume_Id , '/dev/sdm')
    #time.sleep(500)
    manager.delete_volume(Volume_Id)
    manager.terminate_instance(Instance_Id)
