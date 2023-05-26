import subprocess

# Define the name of the cluster
cluster_name = 'my-k8s-cluster'

# Define the IP addresses of the worker nodes
worker1_ip = 'worker1_ip_address'
worker2_ip = 'worker2_ip_address'

# Install kubeadm, kubelet, and kubectl on the VMs
subprocess.run('sudo apt-get update', shell=True, check=True)
subprocess.run('sudo apt-get install -y apt-transport-https curl', shell=True, check=True)
subprocess.run('curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -', shell=True, check=True)
subprocess.run('sudo touch /etc/apt/sources.list.d/kubernetes.list', shell=True, check=True)
subprocess.run('echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list', shell=True, check=True)
subprocess.run('sudo apt-get update', shell=True, check=True)
subprocess.run('sudo apt-get install -y kubelet kubeadm kubectl', shell=True, check=True)
subprocess.run('sudo apt-mark hold kubelet kubeadm kubectl', shell=True, check=True)

# Initialize the cluster using kubeadm on the master node
subprocess.run(f'sudo kubeadm init --apiserver-advertise-address=<master_ip> --pod-network-cidr=10.244.0.0/16 --node-name {cluster_name}', shell=True, check=True)

# Set up kubectl to use the new cluster configuration
subprocess.run(f'mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config', shell=True, check=True)

# Install a pod network add-on to enable communication between pods
subprocess.run('sudo kubectl apply -f https://docs.projectcalico.org/v3.18/manifests/calico.yaml', shell=True, check=True)

# Generate join command for worker nodes
join_command = subprocess.run(f'sudo kubeadm token create --print-join-command', shell=True, check=True, stdout=subprocess.PIPE)
join_command_str = join_command.stdout.decode('utf-8').strip()

# Join the worker nodes to the cluster
subprocess.run(f'ssh user@{worker1_ip} "{join_command_str}"', shell=True, check=True)
subprocess.run(f'ssh user@{worker2_ip} "{join_command_str}"', shell=True, check=True)
