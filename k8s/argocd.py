from kubernetes import client, config
import time


class KubernetesCluster:

    def __init__(self, master_node_name, worker_node_names):
        self.master_node_name = master_node_name
        self.worker_node_names = worker_node_names
        self.api = None

    def create_cluster(self):
        # Load the Kubernetes configuration from the default location
        config.load_kube_config()

        # Create a Kubernetes API client object
        self.api = client.CoreV1Api()

        # Define the YAML for the master node deployment
        master_yaml = """
        apiVersion: v1
        kind: Pod
        metadata:
          name: {0}
          labels:
            role: master
        spec:
          containers:
          - name: kube-apiserver
            image: k8s.gcr.io/kube-apiserver:v1.22.3
            command:
            - kube-apiserver
            - --bind-address=0.0.0.0
            - --secure-port=6443
            - --etcd-servers=http://127.0.0.1:2379
          - name: etcd
            image: k8s.gcr.io/etcd:3.5.0-0
            command:
            - etcd
            - --advertise-client-urls=http://127.0.0.1:2379
            - --listen-client-urls=http://0.0.0.0:2379
            - --data-dir=/var/lib/etcd
          - name: kube-controller-manager
            image: k8s.gcr.io/kube-controller-manager:v1.22.3
            command:
            - kube-controller-manager
            - --bind-address=0.0.0.0
            - --leader-elect=true
            - --kubeconfig=/etc/kubernetes/controller-manager.conf
          - name: kube-scheduler
            image: k8s.gcr.io/kube-scheduler:v1.22.3
            command:
            - kube-scheduler
            - --bind-address=0.0.0.0
            - --leader-elect=true
            - --kubeconfig=/etc/kubernetes/scheduler.conf
        """.format(self.master_node_name)

        # Create the master node
        self.api.create_namespaced_pod(body=client.V1Pod(metadata=client.V1ObjectMeta(name=self.master_node_name),
                                                         spec=client.V1PodSpec(
                                                             containers=[client.V1Container(name="kube-apiserver",
                                                                                            image="k8s.gcr.io/kube-apiserver:v1.22.3",
                                                                                            command=["kube-apiserver",
                                                                                                     "--bind-address=0.0.0.0",
                                                                                                     "--secure-port=6443",
                                                                                                     "--etcd-servers=http://127.0.0.1:2379"]),
                                                                         client.V1Container(name="etcd",
                                                                                            image="k8s.gcr.io/etcd:3.5.0-0",
                                                                                            command=["etcd",
                                                                                                     "--advertise-client-urls=http://127.0.0.1:2379",
                                                                                                     "--listen-client-urls=http://0.0.0.0:2379",
                                                                                                     "--data-dir=/var/lib/etcd"]),
                                                                         client.V1Container(
                                                                             name="kube-controller-manager",
                                                                             image
                                                                         "k8s.gcr.io/kube-controller-manager:v1.22.3",
                                                                         command = ["kube-controller-manager",
                                                                                    "--bind-address=0.0.0.0",
                                                                                    "--leader-elect=true",
                                                                                    "--kubeconfig=/etc/kubernetes/controller-manager.conf"]),
        client.V1Container(name="kube-scheduler",
                           image="k8s.gcr.io/kube-scheduler:v1.22.3",
                           command=["kube-scheduler",
                                    "--bind-address=0.0.0.0",
                                    "--leader-elect=true",
                                    "--kubeconfig=/etc/kubernetes/scheduler.conf"]))))

        # Wait for the master node to become ready
        self.wait_for_node_ready(self.master_node_name)

        # Define the YAML for the worker nodes
        worker_yaml = """
    apiVersion: v1
    kind: Pod
    metadata:
      name: {0}
      labels:
        role: worker
    spec:
      containers:
      - name: kubelet
        image: k8s.gcr.io/kubelet:v1.22.3
        command:
        - kubelet
        - --register-node
        - --kubeconfig=/etc/kubernetes/kubelet.conf
        - --pod-manifest-path=/etc/kubernetes/manifests
    """.format(self.worker_node_names[0])

        # Create the worker nodes
        for node_name in self.worker_node_names:
            self.api.create_namespaced_pod(body=client.V1Pod(metadata=client.V1ObjectMeta(name=node_name),
                                                             spec=client.V1PodSpec(
                                                                 containers=[client.V1Container(name="kubelet",
                                                                                                image="k8s.gcr.io/kubelet:v1.22.3",
                                                                                                command=["kubelet",
                                                                                                         "--register-node",
                                                                                                         "--kubeconfig=/etc/kubernetes/kubelet.conf",
                                                                                                         "--pod-manifest-path=/etc/kubernetes/manifests"])])))
        # Wait for the worker node to become ready
        self.wait_for_node_ready(node_name)

        # Install Argo CD on the cluster
        argocd_yaml = """
    apiVersion: v1
    kind: Namespace
    metadata:
      name: argocd
    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: argocd-application-controller
      namespace: argocd
    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: argocd-server
      namespace: argocd
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: argocd-server
      namespace: argocd
      labels:
        app: argocd
        service: server
    spec:
      ports:
      - name: http
        port: 80
        targetPort: http
      selector:
        app: argocd
        component: server
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: argocd-server
      namespace: argocd
      labels:
        app: argocd
        component: server
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: argocd
          component: server
      template:
        metadata:
          labels:
            app: argocd
            component: server
        spec:
          containers:
          - name: argocd-server
            image: argoproj/argocd:v2.1.4
            args: ["argocd-server", "--staticassets=/shared/app"]
            env:
            - name: ARGOCD_OPTS
              value: "--staticassets=/shared/app"
            - name: ARGOCD_SERVER_PORT
              value: "80"
            ports:
            - containerPort: 80
              name: http
              protocol: TCP
            volumeMounts:
            - name: argocd-server-static-assets
              mountPath: /shared/app
              readOnly: true
            readinessProbe:
              httpGet:
                path: /healthz
                port: http
              initialDelaySeconds: 30
              timeoutSeconds: 5
              periodSeconds: 10
              successThreshold: 3
              failureThreshold: 3
          volumes:
          - name: argocd-server-static-assets
            configMap:
              name: argocd-server-static-assets
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: argocd-application-controller
      namespace: argocd
      labels:
        app: argocd
        service: application-controller
    spec:
      selector:
        app: argocd
        component: application-controller
      ports:
      - name: http
        port: 8082
        targetPort: http
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: argocd-application-controller
      namespace: argocd
      labels:
        app: argocd
        component: application-controller
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: argocd
          component: application-controller
      template:
        metadata:
          labels:
            app: argocd
            component: application-controller
        spec:
          containers:
          - name: argocd-application-controller
            image: argoproj/argocd:v2.1.4
            command:
              - argocd-application-controller
            args:
              - --redis
              - argocd-redis:6379
            env:
            - name: ARGOCD_OPTS
              value: "--redis argocd-redis:6379"
            readinessProbe:
              httpGet:
                path: /healthz
                port: http
              initialDelaySeconds: 5
              timeoutSeconds: 3
              periodSeconds: 10
              successThreshold: 1
              failureThreshold: 3
    """
    self.create_k8s_resource(argocd_yaml)

    # Create an application using Argo CD
    app_yaml = """
    apiVersion: argoproj.io/v1alpha1
    kind: Application
    metadata:
      name: guestbook
      namespace: default
    spec:
      project: default
      source:
        repoURL: https://github.com/argoproj/argocd-example-apps.git
        path: guestbook
        targetRevision: HEAD
      destination:
        server: 'https://kubernetes.default.svc'
        namespace: default
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
    """
    self.create_k8s_resource(app_yaml)

    # Wait for the application to become ready
    self.wait_for_k8s_resource_ready("application/guestbook", "argocd")

def wait_for_node_ready(self, node_name):
    """
    Waits for a Kubernetes node to become ready.
    """
    while True:
        node = self.api.read_node_status(node_name)
        conditions = node.status.conditions
        for condition in conditions:
            if condition.type == "Ready" and condition.status == "True":
                return
        time.sleep(10)

        def wait_for_k8s_resource_ready(self, resource_name, namespace):
            """
            Waits for a Kubernetes resource to become ready.
            """
            while True:
                resource = self.api.get(resource_name, namespace)
                if resource.metadata.labels.get(
                        "app.kubernetes.io/part-of") == "argocd" and resource.status.sync.status == "Synced":
                    return
                time.sleep(10)

        def create_k8s_resource(self, yaml):
            """
            Creates a Kubernetes resource from YAML.
            """
            resource = yaml.safe_load(yaml)
            kind = resource["kind"].lower()
            if kind == "configmap":
                self.api.create_config_map(resource["metadata"]["name"], resource["data"],
                                           resource["metadata"]["namespace"])
            elif kind == "deployment":
                self.api.create_deployment(resource["metadata"]["name"], resource["metadata"]["namespace"],
                                           resource["spec"]["replicas"], resource["spec"]["selector"]["matchLabels"],
                                           resource["spec"]["template"])
            elif kind == "service":
                self.api.create_service(resource["metadata"]["name"], resource["metadata"]["namespace"],
                                        resource["spec"]["selector"], resource["spec"]["ports"])
            elif kind == "persistentvolumeclaim":
                self.api.create_persistent_volume_claim(resource["metadata"]["name"], resource["metadata"]["namespace"],
                                                        resource["spec"]["resources"]["requests"]["storage"])
            elif kind == "secret":
                self.api.create_secret(resource["metadata"]["name"], resource["metadata"]["namespace"],
                                       resource["data"])
            elif kind == "namespace":
                self.api.create_namespace(resource["metadata"]["name"])
            elif kind == "ingress":
                self.api.create_ingress(resource["metadata"]["name"], resource["metadata"]["namespace"],
                                        resource["spec"]["rules"])
            elif kind == "application":
                self.api.create_argo_application(resource["metadata"]["name"], resource["metadata"]["namespace"],
                                                 resource["spec"])
            else:
                raise ValueError(f"Unknown kind: {kind}")

        def delete_k8s_resource(self, yaml):
            """
            Deletes a Kubernetes resource from YAML.
            """
            resource = yaml.safe_load(yaml)
            kind = resource["kind"].lower()
            name = resource["metadata"]["name"]
            namespace = resource["metadata"]["namespace"]
            if kind == "configmap":
                self.api.delete_config_map(name, namespace)
            elif kind == "deployment":
                self.api.delete_deployment(name, namespace)
            elif kind == "service":
                self.api.delete_service(name, namespace)
            elif kind == "persistentvolumeclaim":
                self.api.delete_persistent_volume_claim(name, namespace)
            elif kind == "secret":
                self.api.delete_secret(name, namespace)
            elif kind == "namespace":
                self.api.delete_namespace(name)
            elif kind == "ingress":
                self.api.delete_ingress(name, namespace)
            elif kind == "application":
                self.api.delete_argo_application(name, namespace)
            else:
                raise ValueError(f"Unknown kind: {kind}")

        def cleanup(self):
            """
            Cleans up the resources created by the program.
            """
            # Delete the Argo CD application
            app_yaml = """
                apiVersion: argoproj.io/v1alpha1
                kind: Application
                metadata:
                  name: guestbook
                  namespace: default
                """
            self.delete_k8s_resource(app_yaml)

            # Delete the Argo CD resources
            self.delete_k8s_resource(ARGOCD_YAML)

            # Delete the Kubernetes resources
            self.delete_k8s_resource(KUBERNETES_YAML)
