# Helm Chart for Check Point Infinity Next
## Introduction
Helm charts provide the ability to deploy a collection of kubernetes services and containers with a single command. This helm chart deploys an ingress controller integrated with the Check Point container images that include Check Point Infinity Next WAAP nano agent. If you want to integrate the Check Point Infinity Next WAAP nano agent with an ingress controller other than nginx, follow the instructions in the WAAP installation guide. Another option would be to download the helm chart and modify the parameters to match your Kubernetes/Application environment.
## Prerequisites
*   Properly configured access to a K8s cluster (helm and kubectl working)
*   Helm 3.x installed
*   Access to a repository that contains the Check Point nginx controller and cp-alpine images
*   An account in portal.checkpoint.com with access to Infinity Next

## Description of Helm Chart components
*   _Chart.yaml_ \- the basic definition of the helm chart being created. Includes helm chart type, version number, and application version number 
*   _values.yaml_ \- the application values (variables) to be applied when installing the helm chart. In this case, the CP WAAP nano agent token ID, the image repository locations, the type of ingress service being used and the ports, and specific application specifications can be defined in this file. These values can be manually overridden when launching the helm chart from the command line as shown in the example below.
*   _templates/configmap.yaml_ \- configuration information for nginx.
*   _templates/customresourcedefinition.yaml_ \- CustomResourceDefinitions for the ingress controller.
*   _templates/clusterrole.yaml_ \- specifications of the ClusterRole and ClusterRoleBinding role-based access control (rbac) components for the ingress controller.
*   _ingress-deploy-nano.yaml_ \- container specifications that pull the nginx image that contains the references to the CP Nano Agent and the CP Alpine image that includes the Nano Agent itself.
*   _templates/ingress.yaml_ \- specification for the ingress settings for the application.
*   _templates/secrets.yaml_ \- secrets file.
*   _templates/service.yaml_ \- specifications for the ingress controller, e.g. LoadBalancer listening on port 80, forwarding to nodePort 30080 of the application 
## Installing the Chart 

Define your application in the “Infinity Next” application of the Check Point Infinity Portal according to the CloudGuard WAAP Deployment Guide section on WAAP Management .

Once the application has been configured in the Infinity Next Portal, retrieve the value for the nanoToken.

Next, install the chart with the chosen release name (e.g. `my-release`), run:

```bash
$ helm repo add checkpoint https://raw.githubusercontent.com/CheckPointSW/charts/master/repository/
$ helm install my-release checkpoint/cpwaapingressctl --namespace="{your namespace}" --set nanoToken="{your Infinity Next token string here}" 
```
These are additional optional flags:
```bash
--set appURL="{your app URL}" 
--set mysvcname="{your app service name" 
--set mysvcport="{your app service port}"
--set image.nginxCtlCpRepo="{repo location of the Infinity Next nginx image}"  
--set image.cpRepo="{repo location of the Infinity Next Nano image}" 
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
$ helm install my-release --namespace="myappnamespace" checkpoint/cpwaapingressctl --set nanoToken="3574..." --set appURL="my-app.example.com" --set mysvcname="myappsvc" --set mysvcport="8080"

```
Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example,

```bash
$ helm install my-release -f values.yaml checkpoint/cpWaapJuice
```
> **Tip**: You can use the default [values.yaml](values.yaml)

The following table lists the configurable parameters of this chart and their default values.

| Parameter                                                  | Description                                                     | Default                                          |
| ---------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------ |
| `image.nginxCtlCpRepo`                                             | Dockerhub location of the nginx image integrated with Check Point Waap                     | `mnicholssync/nginx-ingress-ctl-cp:demo`                                              |
| `image.cpRepo`                                              | Dockerhub location of the Check Point Alpine image integrated with the NanoAgent              | `mnicholssync/nginx-ingress-ctl-cp:cp-agent-alpine`                                           |
| `appURL`                                           | URL of the application (must resolve to cluster IP address after deployment)              | `juice-shop.checkpoint.com`                                          |
| `mysvcname`                                           | K8s service name of your application               | `juice-shop`                         |
| `mysvcport`                                           | K8s listening port of your service               | `8080`                         |

### Generating WaaP results and Testing the Application

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
Enter any password and click “Log In”.  For the normal juice-shop app without Infinity Next WAAP, the results show a compromised application. With Infinity Next protection, you will see the login blocked.

Review the log files in the Infinity Portal to see the Results
* * *
