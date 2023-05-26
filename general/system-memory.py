import psutil

# Memory
memory = psutil.virtual_memory()
total_memory = memory.total / (1024.0 ** 2)  # total memory in MB
available_memory = memory.available / (1024.0 ** 2)  # available memory in MB
used_memory = total_memory - available_memory  # used memory in MB
memory_percent = memory.percent  # memory usage percentage
print("Total Memory: {:.2f}MB".format(total_memory))
print("Used Memory: {:.2f}MB".format(used_memory))
print("Available Memory: {:.2f}MB".format(available_memory))
print("Memory Usage: {:.2f}%".format(memory_percent))

# Disk
disk = psutil.disk_usage("/")
total_disk = disk.total / (1024.0 ** 3)  # total disk in GB
available_disk = disk.free / (1024.0 ** 3)  # available disk in GB
used_disk = total_disk - available_disk  # used disk in GB
disk_percent = disk.percent  # disk usage percentage
print("\nTotal Disk Space: {:.2f}GB".format(total_disk))
print("Used Disk Space: {:.2f}GB".format(used_disk))
print("Available Disk Space: {:.2f}GB".format(available_disk))
print("Disk Usage: {:.2f}%".format(disk_percent))

