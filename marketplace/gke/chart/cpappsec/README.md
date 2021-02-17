# Helm Chart for Check Point CloudGuard AppSec
## Overview
Check Point CloudGuard AppSec delivers access control and advanced threat prevention including web and api protection for mission-critical assets.  Check Point CloudGuard AppSec delivers advanced, multi-layered threat prevention to protect customer assets in Kubernetes clusters from web attacks and sophisticated threats.

Helm charts provide the ability to deploy a collection of kubernetes services and containers with a single command. This helm chart deploys an ingress controller integrated with the Check Point container images that include Check Point CloudGuard AppSec nano agent. If you want to integrate the Check Point CloudGuard AppSec nano agent with an ingress controller other than nginx, follow the instructions in the AppSec installation guide. Another option would be to download the helm chart and modify the parameters to match your Kubernetes/Application environment.

## Description of Helm Chart components
*   _Chart.yaml_ \- the basic definition of the helm chart being created. Includes helm chart type, version number, and application version number 
*   _values.yaml_ \- the application values (variables) to be applied when installing the helm chart. In this case, the CP AppSec nano agent token ID, the image repository locations, the type of ingress service being used and the ports, and specific application specifications can be defined in this file. These values can be manually overridden when launching the helm chart from the command line as shown in the example below.
*   _templates/configmap.yaml_ \- configuration information for nginx.
*   _templates/customresourcedefinition.yaml_ \- CustomResourceDefinitions for the ingress controller.
*   _templates/clusterrole.yaml_ \- specifications of the ClusterRole and ClusterRoleBinding role-based access control (rbac) components for the ingress controller.
*   _ingress-deploy-nano.yaml_ \- container specifications that pull the nginx image that contains the references to the CP Nano Agent and the CP Alpine image that includes the Nano Agent itself.
*   _templates/ingress.yaml_ \- specification for the ingress settings for the application.
*   _templates/secrets.yaml_ \- secrets file.
*   _templates/service.yaml_ \- specifications for the ingress controller, e.g. LoadBalancer listening on port 80, forwarding to nodePort 30080 of the application 

The following table lists the configurable parameters of this chart and their default values.

| Parameter                                                  | Description                                                     | Default                                          |
| ---------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------ |
| `nanoToken`                                           | Check Point AppSec nanoToken from the CloudGuard Portal(required)                             | `034f3d-96093mf-3k43li... `                                          |
| `appURL`                                           | URL of the application (must resolve to cluster IP address after deployment,required)     | `myapp.mycompany.com`                                          |
| `mysvcname`                                           | K8s service name of your application(required)     | `myapp`                         |
| `mysvcport`                                           | K8s listening port of your service(required)     | `8080`                         |
| `image.nginxCtlCpRepo`                                             | Dockerhub location of the nginx image integrated with Check Point AppSec                     | `checkpoint/infinity-next-nginx`                                              |
| `image.cpRepo`                                              | Dockerhub location of the Check Point nano agent image              | `checkpoint/infinity-next-nano-agent`                                           |
| `TLS_CERTIFICATE_CRT`                                           | Default TLS Certificate               | `Certificate string`                         |
| `TLS_CERTIFICATE_KEY`                                           | Default TLS Certificate Key               | `Certificate Key string`                         | 

# Installation

Define your application in the “CloudGuard AppSec” application of the Check Point CloudGuard Portal according to the CloudGuard AppSec Deployment Guide section on AppSec Management .

Once the application has been configured in the CloudGuard AppSec Portal, retrieve the value for the nanoToken.

Next, install the chart with the chosen release name (e.g. `my-release`), run:

```bash
$ helm repo add checkpoint https://raw.githubusercontent.com/CheckPointSW/charts/master/repository/
$ helm install my-release checkpoint/cpappsec-ingress-ctl --namespace="{your namespace}" --set nanoToken="{your CloudGuard AppSec token string here}" 
```
These are additional optional flags:
```bash
--set appURL="{your app URL}" 
--set mysvcname="{your app service name" 
--set mysvcport="{your app service port}"
--set image.nginxCtlCpRepo="{repo location of the CloudGuard AppSec nginx image}"  
--set image.cpRepo="{repo location of the CloudGuard AppSec Nano image}" 
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
$ helm install my-release --namespace="myappnamespace" checkpoint/cpappsec-ingress-ctl --set nanoToken="3574..." --set appURL="my-app.example.com" --set mysvcname="myappsvc" --set mysvcport="8080"

```
Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example,

```bash
$ helm install my-release -f values.yaml checkpoint/cpappsec-Juice
```
> **Tip**: You can use the default [values.yaml](values.yaml)

The following table lists the configurable parameters of this chart and their default values.

### Generating AppSec results and Testing the Application

Use kubectl to get the IP address of the ClusterIP
																																										   

														   
			
														 
							  
						   
										 
	   
																  

			
															 
															 
	   
												

																				
													 

		
									 
```
kubectl get all

																		  
															 

		
							   
```

Ensure your DNS or host file maps the application URL to the IP address of the ClusterIP. 

Open a Firefox browser tab (If you are testing the juice-shop application, Chrome redirects to https, which will not work for the juice-shop example) and go to _**http://{yourapplicationURL}**_

For testing with the juice-shop application, deploy the app in your Kubernetes environment. Click on “Account” and select “Login”. In the username field, enter 
```
select * from ‘1’=’1’ --
```
Enter any password and click “Log In”.  For the normal juice-shop app without CloudGuard AppSec, the results show a compromised application. With CloudGuard AppSec protection, you will see the login blocked.

Review the log files in the CloudGuard Portal to see the Results
* * *
