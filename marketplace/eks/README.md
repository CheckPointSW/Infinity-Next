# Check Point CloudGuard AppSec for EKS
## Overview
Check Point CloudGuard AppSec delivers access control, and advanced, multi-layered threat prevention including Web and API protection for mission-critical assets.

Helm charts provide the ability to deploy a collection of kubernetes services and containers with a single command. This helm chart deploys an Nginx-based (1.19) ingress controller integrated with the Check Point container images that include and Nginx Reverse Proxy container integrated with the Check Point CloudGuard AppSec nano agent container. It is designed to run in front of your existing Kubernetes Application. If you want to integrate the Check Point CloudGuard AppSec nano agent with an ingress controller other than nginx, follow the instructions in the CloudGuard AppSec installation guide. Another option would be to download the helm chart and modify the parameters to match your Kubernetes/Application environment.

## Architecture
**NOTE:** The following diagram shows a sample architecture with the application (optionally) exposed externally, using an Ingress and TLS configuration. The steps to enable the Ingress resource are in the sections below.
![Sample Architecture Diagram](resources/CP-CloudGuard_AppSec-Sample-Architecture.png)

The following table lists the configurable parameters of this chart and their default values.

| Parameter                                                  | Description                                                     | Default                                          |
| ---------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------ |
| `nanoToken`                                           | Check Point AppSec nanoToken from the CloudGuard Portal(required)                             | `034f3d-96093mf-3k43li... `                                          |
| `appURL`                                           | URL of the application (must resolve to cluster IP address after deployment,required)     | `myapp.mycompany.com`                                          |
| `mysvcname`                                           | K8s service name of your application(required)     | `myapp`                         |
| `mysvcport`                                           | K8s listening port of your service(required)     | `8080`                         |
| `myNodePort`                                           | Host Node Port used for inbound ingress     | `30080`                         |
| `mySSLNodePort`                                        |  Host Node Port used for SSL inbound ingress)     | `30443`                         |
| `platform`                                        |  Deployment Platform (EKS, AKS, GKE, private)     | `private`                         |
| `image.cpappsecnginxingress.properties.imageRepo`                                             | Dockerhub location of the nginx image integrated with Check Point AppSec                     | `checkpoint/infinity-next-nginx-ingress`                                              |
| `image.cpappsecnginxingress.properties.imageTag`                                             | Image Version to use                    | `1.0.2`                                              |
| `image.cpappsecnanoagent.properties.imageRepo`                                              | Dockerhub location of the Check Point nano agent image              | `checkpoint/infinity-next-nano-agent`                                           |
| `image.cpappsecnanoagent.properties.imageTag`                                              | Version to use              | `1.0.2`                                           |
| `TLS_CERTIFICATE_CRT`                                           | Default TLS Certificate               | `Certificate string`                         |
| `TLS_CERTIFICATE_KEY`                                           | Default TLS Certificate Key               | `Certificate Key string`                         | 

# Installation

## Command line instructions

You can use [AWS Cloud Shell](https://shell.AWS.com/#cloudshell/) or a local workstation to follow the steps below.

### Prerequisites
#### Configure your application in the [Check Point Infinity Next AppSec Portal](https://portal.checkpoint.com) 
Define the application you want to protect in the “Infinity Next AppSec” application of the Check Point Infinity Next AppSec Portal according to the CloudGuard AppSec Deployment Guide section on AppSec Management. [CP CloudGuard AppSec Admin Guide](https://github.com/CheckPointSW/Infinity-Next/blob/main/marketplace/gke/resources/CP_CloudGuard_AppSec_AdminGuide.pdf)

Once the application has been configured in the CloudGuard AppSec Portal, retrieve the value for the nanoToken to be used in a later step.

#### Set up command-line tools
You'll need the following tools in your development environment. If you are using Cloud Shell, `az`, `kubectl`, Docker, and Git are installed in your environment by default.

-   [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/)
-   [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
-   [openssl](https://www.openssl.org/)
-   [helm](https://helm.sh/)


### Provision a Kubernetes Cluster with EKS 
(You may already have one for your existing K8s Application)

The quickest way to setup a Kubernetes cluster using the command line is with `eksctl`. 

Follow the steps below to provision a Kubernetes Cluster with AKS. 

```bash
eksctl create cluster --name cpappsec --region us-east-1 --with-oidc --ssh-access --ssh-public-key /path-to-your-key --managed
```
The above command creates a new cluster named `cpappsec`. Then, install and configure `kubectl` with the credentials to the new EKS cluster, as shown below:

```bash
aws eks --region us-east-1 update-kubeconfig --name cpappsec
```

#### (Optional) Create a namespace in your Kubernetes cluster
If you use a different namespace than `default`, or the namespace does not exist
yet, run the command below to create a new namespace:

```shell
kubectl create namespace {yournamespace}
```

### Install the Application
Note: EKS REQUIRES the "platform" be specified in the variables.

```shell
helm install cpappsec cpappsec-1.0.3.tgz --set nanoToken="{your nanoToken}" --set appURL="{your AppURL}" --set mysvcname="{your App Svc Name}" --set mysvcport="{your app svc port}" --set platform="EKS" 
```

### Open your Application site
Get the external IP of your Application site using the following command:

```
SERVICE_IP=$(kubectl get ingress $APP_INSTANCE_NAME-cp-ingress-ctl-svc \
  --namespace $NAMESPACE \
  --output jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "https://${SERVICE_IP}/"
```
The command shows you the URL for inbound traffic to your site through the Check Point AppSec Ingress Controller.

After the Ingress Controller container creation is finished, the Check Point Agent will register in the Check Point Infinity Next portal and your application will be protected based on the policy you define there.

# Uninstall the Application

## Using the AWS Cloud Platform Console

1.  In the AWS Portal, select your Kubernetes Cluster from
    [Kubernetes Services](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.ContainerService%2FmanagedClusters).

1.  From the list of applications, select "Workloads" from Kubernetes Resources.

1.  Select **cpappsec** and  click **Delete**.

## Using the command line

```
helm delete cpappsec
```











