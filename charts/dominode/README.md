# Using the chart

## TL;DR;

This instruction is for production usage to install directly using helm into your target cluster:

Add the helm repo of the dependencies.

```bash
helm repo add kartoza https://kartoza.github.io/charts
``` 

Clone this git repo into your favorite working folder:

```bash
git clone https://github.com/dominodeorg/dominode.git
cd dominode
```

Notes: If you want to use it for local development, don't forget to build the image first:

```bash
cd geonode_dominode/scripts/spcgeonode
make build
```

Go into the charts directory, which is where this README.md is located (from the root directory of this repo):

```bash
cd charts/dominode
```

Install the chart from this current location.
As always, before installing, make sure your kubectl context already target the correct kubernetes cluster and uses your target namespace.

To check where your cluster is:

```bash
kubectl cluster-info
kubectl config get-contexts
```

To set your default namespace for subsequent operations:

```bash
kubectl config set-context --current --namespace <your namespace name>
```

Assuming your release name `dominode`: 

```bash
helm install dominode .
```

The `.` is the location of this chart. If you use helm from different directory, please provide the correct location.

If you want to override some values, like the site name:

```bash
helm install dominode . --set global.geonodeSiteName=mysite.org
```

You can chain your values overrides.

It is best for production deployment that you have the full overridden `values.yaml` according to how you want to deploy the chart. Supply it to helm install.

```bash
helm install dominode . -f production-values.yaml
``` 

If you change the values OR the chart, you can upgrade:

```bash
helm upgrade dominode . 
```

Again, if you have overridden values, supply that as well.

```bash
helm upgrade dominode . -f production-values.yaml
```

This will only install the charts with headless connections. If you need to expose it, you need to do it according to your cluster policy (via Ingress, NodePort, etc)

## Local deployment

You may want to deploy it in your local cluster for testing reasons. You need to adapt from the basic installation instructions to fit your need.

### Volume provisioning

Most local cluster will not have dynamic provisioning. The installation will 
succeed but the pods will be in pending state because someone must give them volumes. 
You can give static volumes or dynamically provision them. The chart is equipped with local volume template (using hostPath type).
Install the chart by overriding this value sections:

```yaml
local_persistence:
  enabled: false
  storageClass: ""
  media:
    host_path: /tmp/dominode-media
  static:
    host_path: /tmp/dominode-static
  postgis:
    host_path: /tmp/dominode-postgis
  geoserver_data_dir:
    host_path: /tmp/dominode-geoserver-data-dir
  geowebcache_cache_dir:
    host_path: /tmp/dominode-geowebcache-cache-dir
```

Switch `local_persistence.enabled` to `true`, then supply the location of the host path. Remember that this only works in single node kubernetes cluster.

If you want to do this without relying on the chart, you con do so by first figuring out the volume claim. List the volume claim first:

```bash
kubectl get pvc
```

Then you can declare the volume and assign them to the exact claim name. For example, this manifest create a hostPath volume and assign it to media directory.

```yaml
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: media-dir
  labels:
    provisioner: local
spec:
  capacity:
    storage: 8Gi
  accessModes:
    - ReadWriteOnce
  claimRef:
    name: media-dir
    namespace: default
  hostPath:
    path: /path/to/my/media/dir
...
```

Alternatively, you can use dynamic provisioning depending on your cloud providers where you install your cluster.
When you are using dynamic provisioning, the volumes will be created by default storage class.

In case you are using bare metal cluster, or k8s distros that you install manually, you may want to install 3rd party dynamic volume provisioner.

These are some volume provisioner that might help you for local development:

- Rancher's local path provisioner: https://github.com/rancher/local-path-provisioner
- Rancher's Longhorn: https://longhorn.io/

### File organizations

If there are any upstream chart changes, you can update dependencies using:

```bash
helm dependency update
```

This will update `Chart.lock` and `charts` directory. To change the upstream chart version, do so in `Chart.yaml` then run helm dependency update.

The `templates` directory is used to store any k8s manifests that must be generated first.

The `manifests` directory can be used to store **your** local development k8s manifests. This will not be committed to the git repo because it's context depends on each developer on how they deploy the charts in their own environment.

You can store any `-values.yaml` in this directory. Each developer will override the values a little bit different due to different network and or password they use. This will not be committed in the repo.


