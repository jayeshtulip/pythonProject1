import subprocess

def check_ip_reachability(public_ip):
    try:
        # Use the ping command to send 5 ICMP echo requests to the public IP
        output = subprocess.check_output(['ping', '-c', '5', public_ip])
        return True
    except subprocess.CalledProcessError:
        return False

# Provide the public IP address of the VM
public_ip = '10.16.146.44'

# Check if the public IP is reachable
reachable = check_ip_reachability(public_ip)
if reachable:
    print(f"The public IP {public_ip} is reachable.")
else:
    print(f"The public IP {public_ip} is not reachable.")