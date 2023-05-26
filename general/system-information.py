import psutil
import platform
import socket
import uuid

# Get information about the system's memory usage
memory_info = psutil.virtual_memory()
total_memory = memory_info.total
used_memory = memory_info.used
free_memory = memory_info.free

# Print the memory usage information
print("Total memory:", total_memory)
print("Used memory:", used_memory)
print("Free memory:", free_memory)

# Get the CPU usage information
cpu_percent = psutil.cpu_percent()

# Print the CPU usage information
print("CPU usage:", cpu_percent)




# Get the system's operating system
os_name = platform.system()

# Print the operating system
print("Operating system:", os_name)

# Get the system's IP address
ip_address = socket.gethostbyname(socket.gethostname())

# Print the IP address
print("IP address:", ip_address)

# Get the system's MAC address
mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:]

# Print the MAC address
print("MAC address:", mac_address)
