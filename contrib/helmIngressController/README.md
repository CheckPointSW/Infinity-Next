# Helm Chart for Check Point CloudGuard AppSec
## Overview
NOTE: This chart will not work on EKS. For eks, use https://github.com/CheckPointSW/Infinity-Next/tree/main/marketplace/eks
Check Point CloudGuard AppSec delivers access control and advanced threat prevention including web and api protection for mission-critical assets.  Check Point CloudGuard AppSec delivers advanced, multi-layered threat prevention to protect customer assets in Kubernetes clusters from web attacks and sophisticated threats based on Contextual AI.

Helm charts provide the ability to deploy a collection of kubernetes services and containers with a single command. This helm chart deploys an Nginx-based (1.19) ingress controller integrated with the Check Point container images that include and Nginx Reverse Proxy container integrated with the Check Point CloudGuard AppSec nano agent container. It is designed to run in front of your existing Kubernetes Application. If you want to integrate the Check Point CloudGuard AppSec nano agent with an ingress controller other than nginx, follow the instructions in the CloudGuard AppSec installation guide. Another option would be to download the helm chart and modify the parameters to match your Kubernetes/Application environment.
## Architecture
The following table lists the configurable parameters of this chart and their default values.

| Parameter                                                  | Description                                                     | Default                                          |
| ---------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------ |
| `nanoToken`                                           | Check Point AppSec nanoToken from the CloudGuard Portal(required)                             | `034f3d-96093mf-3k43li... `                                          |
| `appURL`                                           | URL of the application (must resolve to cluster IP address after deployment,required)     | `myapp.mycompany.com`                                          |
| `mysvcname`                                           | K8s service name of your application(required)     | `myapp`                         |
| `mysvcport`                                           | K8s listening port of your service(required)     | `8080`                         |
| `myNodePort`                                           | Host Node Port used for inbound ingress     | `30080`                         |
| `mySSLNodePort`                                        |  Host Node Port used for SSL inbound ingressred)     | `30443`                         |
| `image.cpappsecnginxingress.properties.imageRepo`                                             | Dockerhub location of the nginx image integrated with Check Point AppSec                     | `checkpoint/infinity-next-nginx-ingress`                                              |
| `image.cpappsecnginxingress.properties.imageTag`                                             | Image Version to use                    | `latest`                                              |
| `image.cpappsecnanoagent.properties.imageRepo`                                              | Dockerhub location of the Check Point nano agent image              | `checkpoint/infinity-next-nano-agent`                                           |
| `image.cpappsecnanoagent.properties.imageTag`                                              | Version to use              | `latest`                                           |
| `TLS_CERTIFICATE_CRT`                                           | Default TLS Certificate               | `Certificate string`                         |
| `TLS_CERTIFICATE_KEY`                                           | Default TLS Certificate Key               | `Certificate Key string`                         | 

## Prerequisites
*   Properly configured access to a K8s cluster (helm and kubectl working)
*   Helm 3.x installed
*   Access to a repository that contains the Check Point Infinity-Next-Nginx controller and Infinity-Next-Nano-Agent images
*   An account in portal.checkpoint.com with access to CloudGuard AppSec

## Description of Helm Chart components
*   _Chart.yaml_ \- the basic definition of the helm chart being created. Includes helm chart type, version number, and application version number 
*   _values.yaml_ \- the default application values (variables) to be applied when installing the helm chart. In this case, the CP AppSec nano agent token ID, the image repository locations, the type of ingress service being used and the ports, and specific application specifications can be defined in this file. These values can be manually overridden when launching the helm chart from the command line as shown in the example below.
*   _templates/configmap.yaml_ \- configuration information for Nginx.
*   _templates/customresourcedefinition.yaml_ \- CustomResourceDefinitions for the ingress controller.
*   _templates/clusterrole.yaml_ \- specifications of the ClusterRole and ClusterRoleBinding role-based access control (rbac) components for the ingress controller.
*   _ingress-deploy-nano.yaml_ \- container specifications that pull the nginx image that contains the references to the CP Nano Agent.
*   _templates/ingress.yaml_ \- specification for the ingress settings for the application that point to your inbound service.
*   _templates/secrets.yaml_ \- secrets file.
*   _templates/service.yaml_ \- specifications for the ingress controller, e.g. LoadBalancer listening on port 80, forwarding to nodePort 30080 of the application 
## Installing the Chart 
Define your application in the CloudGuard AppSec application of the Check Point Infinity Portal according to the CloudGuard AppSec Deployment Guide section on AppSec (WAAP) Management .

Once the application has been configured in the CloudGuard Portal, retrieve the value for the nanoToken.

Download the latest release of the chart here:
```bash
https://github.com/CheckPointSW/Infinity-Next/tree/main/deployments
```
Next, install the chart with the chosen release name (e.g. `my-release`), run:

```bash
$ helm install my-release cpappsec-1.0.2.tgz --namespace="{your namespace}" --set nanoToken="{your AppSec token string here}" --set appURL="{your appURL}" --set mysvcname="{your app Service Name}" --set mysvcport="{your app service port}" 
```
These are additional optional flags:
```bash
--set cpappsec.mysvcport="Your Service Port"
--set cpappsec.myNodePort="The Host Node Port to be assigned"
--set image.cpappsecnginxingress.properties.imageRepo="{a different repo}"
--set image.cpappsecnginxingress.properties.imageTag="{a specific tag/version}"
--set image.cpappsecnanoagent.properties.imageRepo="{a different repo}"
--set image.cpappsecnanoagent.properties.imageTag="{a specific tag/version}"
```
## Uninstalling the Chart
To uninstall/delete the `my-release` deployment:
```bash
$ helm delete my-release -n {your namespace}
```
This command removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

Refer to [values.yaml](values.yaml) for the full run-down on defaults. These are the Kubernetes directives that map to environment variables for the deployment.

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example,

```bash
$ helm install my-release checkpoint/cpappsec-1.0.2.tgz --namespace="myns" --set nanoToken="4339fab-..." --set appURL="myapp.mycompany.com" --set mysvcname="myapp" --set mysvcport="8080" 
```
Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example,

```bash
$ helm install my-release -f values.yaml checkpoint/cpappsec
```
> **Tip**: You can use the default [values.yaml](values.yaml)

### Generating results and Testing the Application

Deploy your Application into the Kubernetes Cluster (e.g., juice-shop.yaml)
Deploy the helm chart
Use kubectl to get the IP address of the cpappsec service.
```
kubectl get all
```

Ensure your DNS or host file maps the application URL to the IP address of the cpappsec service IP. 

Open a Firefox browser tab (If you are testing the juice-shop application, which will not work for the juice-shop example) and go to _**http://{yourapplicationURL}**_

For testing with the juice-shop application, deploy the app in your Kubernetes environment. Click on “Account” and select “Login”. In the username field, enter 
```
select * from ‘1’=’1’ --
```
Enter any password and click “Log In”.  For the normal juice-shop app without CloudGuard AppSec, the results show a compromised application. With CloudGuard AppSec protection, you will see the login blocked.

Review the log files in the Infinity Portal to see the Results
* * *
