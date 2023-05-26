import pytest

class TestVM:
    def test_spawn_vm(self):
        # Code for spawning a VM goes here
        assert vm_spawned == True

    def test_create_volume(self):
        # Code for creating a volume goes here
        assert volume_created == True

    def test_attach_volume(self):
        # Code for attaching the volume to the VM goes here
        assert volume_attached == True

    def test_delete_volume(self):
        # Code for deleting the volume goes here
        assert volume_deleted == True

    def test_delete_vm(self):
        # Code for deleting the VM goes here
        assert vm_deleted == True
