import pytest

from my_aws_library import create_vpc, create_ec2_instance, create_elb, create_volume, attach_volume, detach_volume, delete_volume, delete_elb, delete_ec2_instance, delete_vpc

@pytest.fixture
def vpc():
    vpc = create_vpc()
    yield vpc
    delete_vpc(vpc)

@pytest.fixture
def ec2_instance(vpc):
    ec2_instance = create_ec2_instance(vpc)
    yield ec2_instance
    delete_ec2_instance(ec2_instance)

@pytest.fixture
def elb(vpc, ec2_instance):
    elb = create_elb(vpc, ec2_instance)
    yield elb
    delete_elb(elb)

@pytest.fixture
def volume(ec2_instance):
    volume = create_volume()
    attach_volume(ec2_instance, volume)
    yield volume
    detach_volume(ec2_instance, volume)
    delete_volume(volume)

def test_my_aws_setup(vpc, ec2_instance, elb, volume):
    # test that your VPC, EC2 instance, ELB, and volume are all set up correctly
    assert vpc.exists()
    assert ec2_instance.exists()
    assert elb.exists()
    assert volume.exists()
