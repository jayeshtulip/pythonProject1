import subprocess

# Get the list of all pods in the cluster
pods = subprocess.check_output(["kubectl", "get", "pods", "-o", "json"])

# Iterate over the pods
for pod in pods:
  # Check if the pod is running
  if pod["status"] == "Running":
    # Get the pod's IP address
    ip = pod["status"]["podIP"]

    # Use the curl command to test the connectivity to the pod
    result = subprocess.check_output(["curl", "-I", ip])

    # Check the result of the curl command
    if "200 OK" in result:
      print(f"Connectivity to pod {pod['metadata']['name']} ({ip}) is OK")
    else:
      print(f"Connectivity to pod {pod['metadata']['name']} ({ip}) is NOT OK")
  else:
    print(f"Pod {pod['metadata']['name']} is not running")
