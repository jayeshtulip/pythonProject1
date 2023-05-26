from kubernetes import client, config

def test_create_pod_and_service():
    # Load the kubernetes configuration
    config.load_kube_config()

    # Create an instance of the CoreV1Api client
    core_v1_api = client.CoreV1Api()

    # Define the pod specification
    pod_spec = client.V1PodSpec(
        containers=[
            client.V1Container(
                name="my-container",
                image="nginx:latest"
            )
        ]
    )

    # Create the pod
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name="my-pod"),
        spec=pod_spec
    )
    core_v1_api.create_namespaced_pod(body=pod, namespace="default")

    # Create an instance of the AppsV1Api client
    apps_v1_api = client.AppsV1Api()

    # Define the service specification
    service_spec = client.V1ServiceSpec(
        selector={"app": "my-pod"},
        ports=[client.V1ServicePort(protocol="TCP", port=80)]
    )

    # Create the service
    service = client.V1Service(
        metadata=client.V1ObjectMeta(name="my-service"),
        spec=service_spec
    )
    apps_v1_api.create_namespaced_service(body=service, namespace="default")
