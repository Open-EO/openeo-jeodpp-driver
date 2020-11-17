## Static pod in kubernetes
We created in k8s with the images
`jeoreg.cidsn.jrc.it:5000/jeodpp-k8s/base_gdal_py3_deb10_openeo:0.1.0 `
and Volumes:
`/eos` and `/scratch2`

inside the **openeo** namespace

## build a test image in 150 and run the test container

`docker build -t kubectl -f Dockerfile_kubectl .`

The file kube_config is not in this repo for security reason but is here in EOS
`/eos/jeodpp/home/users/marlelu/openeo/kube_config`

`docker run -it  --name kubectl kubectl bash`

## Test
Test to connect the pod in k8s from a contaienr with kubectl on 150 and execute a command there.

`docker exec -it kubectl bash`

`kubectl get pods -n openeo`
> NAME                         READY   STATUS    RESTARTS   AGE
> openeotest-6589984f8-9vxft   1/1     Running   0          30m

> kubectl exec -n openeo openeotest-6589984f8-9vxft -- python3 /home/install/openeo-master-cd09b74ea9eab60d60c225d9a843bfc9538a2c81/back_end/run_test.py

for editing the script inside the pod

> kubectl exec --stdin --tty openeotest-6589984f8-9vxft -n openeo -- /bin/bash
> vim /home/install/openeo-master-cd09b74ea9eab60d60c225d9a843bfc9538a2c81/back_end/run_test.py


## link for kubectl
https://www.mankier.com/package/kubernetes-client
