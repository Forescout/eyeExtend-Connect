# OpenShift Virtualization Connect App

## Overview

The OpenShift Virtualization Connect App integrates Red Hat OpenShift Virtualization (KubeVirt) with Forescout eyeSight/eyeControl. This Connect App discovers both virtual machines and cluster nodes from OpenShift, resolves properties (CPU, memory, status, guest OS), and enables lifecycle actions directly from Forescout policies.

**Key Features:**
- **VM Discovery**: Discovers all VMs (running and stopped) with properties and lifecycle actions
- **Node Discovery**: Discovers OpenShift cluster nodes with capacity, usage, and management actions
- **VM Actions**: Start, stop, restart, pause/unpause virtual machines
- **Node Actions**: Cordon, uncordon, and drain nodes for maintenance

The app communicates with the OpenShift Kubernetes API using a ServiceAccount bearer token to fetch VirtualMachine (VM), VirtualMachineInstance (VMI), and Node resources.

## Requirements

### OpenShift Cluster
- **Red Hat OpenShift 4.x** with OpenShift Virtualization operator installed
- **KubeVirt API** available at `/apis/kubevirt.io/v1`
- **ServiceAccount** with RBAC permissions to:
  - `list`, `get` VirtualMachines in `kubevirt.io` API group (for VM discovery)
  - `list`, `get` VirtualMachineInstances in `kubevirt.io` API group (for VM runtime info)
  - `update` on `virtualmachines/start`, `virtualmachines/stop`, `virtualmachines/restart` subresources in `subresources.kubevirt.io` API group
  - `update` on `virtualmachineinstances/pause`, `virtualmachineinstances/unpause` subresources in `subresources.kubevirt.io` API group
  - `list`, `get` Nodes (for node discovery)
  - `patch` Nodes (for cordon/uncordon/drain actions)

### Forescout Requirements
- **Forescout CounterACT 8.x** or later
- **Network access** from Forescout appliance to OpenShift API server (typically port 6443)

### ServiceAccount Setup

Create a ServiceAccount with appropriate RBAC permissions on your OpenShift cluster:

```bash
# Create namespace (if needed)
oc create namespace forescout-connect

# Create ServiceAccount
oc create serviceaccount forescout-sa -n forescout-connect

# Create ClusterRole with required permissions
cat <<EOF | oc apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: forescout-kubevirt-access
rules:
- apiGroups: ["kubevirt.io"]
  resources: ["virtualmachines", "virtualmachineinstances"]
  verbs: ["get", "list"]
- apiGroups: ["subresources.kubevirt.io"]
  resources: ["virtualmachines/start", "virtualmachines/stop", "virtualmachines/restart", "virtualmachineinstances/pause", "virtualmachineinstances/unpause"]
  verbs: ["update"]
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "patch"]
EOF

# Bind ClusterRole to ServiceAccount
oc create clusterrolebinding forescout-kubevirt-binding \
  --clusterrole=forescout-kubevirt-access \
  --serviceaccount=forescout-connect:forescout-sa

# Extract the bearer token
TOKEN=$(oc create token forescout-sa -n forescout-connect --duration=8760h)
echo "Token: $TOKEN"
```

Save the token for use during Connect App configuration in Forescout.

## Installation


1. **Import the Connect App**:
   - In Forescout Console, navigate to **Tools > Options > Connect**
   - Click **Import** and select the `OpenShift_Virt_<version>.zip` file
   - Click **OK** to load the app

2. **Configure the connection**:
   - In the **Connect** panel, select **OpenShift Virt**
   - Click **Add** to create a new connection
   - Fill in the connection details:
     - **Cluster API URL**: Your OpenShift API server URL (e.g., `https://api.mycluster.example.com:6443`)
     - **Service Account Token**: The bearer token extracted in the ServiceAccount setup
     - **Validate server certificate**: Enable if using valid TLS certificates (disable for self-signed certs)
   - Configure proxy settings if required

3. **Assign Focal Appliance**:
   - In the **Assign CounterACT Devices** panel, select the appliance that will communicate with the OpenShift cluster
   - Click **Next**

4. **Configure discovery frequency**:
   - Set the **Discovery Frequency** (default: 240 minutes)
   - Enable **Discovery** if you want automatic VM and Node discovery
   - Click **Apply** to save

5. **Test the connection**:
   - Click **Test** to verify connectivity to the OpenShift API
   - A successful test will confirm:
     - Authentication is valid
     - Kubernetes API is accessible
     - KubeVirt API is available

## How It Works

### Discovery (Poll)
The `openshiftvirt_poll.py` script runs on the configured discovery schedule and performs the following:

**VM Discovery:**
1. **Fetch all VirtualMachines** from the cluster (across all namespaces)
2. **Fetch all VirtualMachineInstances** (VMIs) to correlate runtime state
3. **Extract MAC addresses** from VM spec or VMI status
4. **Extract IP addresses** from VMI network interfaces (for running VMs)
5. **Create VM endpoints** identified by MAC address (primary) or IP address
6. **Set online status** based on VMI phase (Running = online, Stopped = offline)

**Node Discovery:**
1. **Fetch all Nodes** from the cluster
2. **Extract node IP addresses** from node status
3. **Count VMs per node** for capacity tracking
4. **Create node endpoints** identified by node IP address
5. **Extract node properties** (capacity, allocatable resources, status, role)

### Property Resolution (Resolve)
**VM Resolution** (`openshiftvirt_resolve.py`):
- **Match by MAC or IP** against VMs in the cluster
- **Extract VM properties** from VM metadata, spec, and labels
- **Extract runtime properties** from VMI status (node, guest OS, IP addresses)
- **Return properties** to Forescout for policy evaluation

**Node Resolution** (`openshiftvirt_resolve_node.py`):
- **Match by IP** against nodes in the cluster
- **Extract node properties** from node metadata, spec, and status
- **Count VMs running on the node**
- **Return properties** to Forescout for policy evaluation

### Actions
**VM Actions** - Manage VM lifecycle using KubeVirt subresource APIs:
- **Start VM**: Sends `start` subresource request to the VM
- **Stop VM**: Sends `stop` subresource request to the VM
- **Restart VM**: Sends `restart` subresource request to the VM
- **Pause VM**: Sends `pause` subresource request to the VMI
- **Unpause VM**: Sends `unpause` subresource request to the VMI

**Node Actions** - Manage node scheduling and maintenance:
- **Cordon Node**: Patches node with `spec.unschedulable=true`
- **Uncordon Node**: Patches node with `spec.unschedulable=false`
- **Drain Node**: Cordons the node (simplified implementation - does not evict pods/VMs)

All actions support **undo** operations to revert changes.

## Properties
### VM Properties


The app discovers the following properties for each OpenShift VM:

| Property Tag                       | Label                        | Type    | Description                                          |
|------------------------------------|------------------------------|---------|------------------------------------------------------|
| `connect_openshiftvirt_vm_name`    | OpenShift VM Name            | String  | Virtual machine name                                 |
| `connect_openshiftvirt_namespace`  | OpenShift VM Namespace       | String  | Kubernetes namespace where the VM resides            |
| `connect_openshiftvirt_status`     | OpenShift VM Status          | String  | Current VM phase (Running, Stopped, Paused, etc.)    |
| `connect_openshiftvirt_node`       | OpenShift VM Node            | String  | OpenShift node hosting the VM instance               |
| `connect_openshiftvirt_cpu_cores`  | OpenShift VM CPU Cores       | Integer | Number of CPU cores allocated to the VM              |
| `connect_openshiftvirt_memory_mb`  | OpenShift VM Memory (MB)     | Integer | Memory allocated to the VM in megabytes              |
| `connect_openshiftvirt_os_type`    | OpenShift VM OS Type         | String  | OS type from vm.kubevirt.io/os label                 |
| `connect_openshiftvirt_creation_date` | OpenShift VM Creation Date | Date  | Date when the VM was created                         |
| `connect_openshiftvirt_labels`     | OpenShift VM Labels          | String  | Kubernetes labels applied to the VM                  |
| `connect_openshiftvirt_running`    | OpenShift VM Running         | Boolean | Whether the VM spec indicates it should be running   |
| `connect_openshiftvirt_guest_os`   | OpenShift VM Guest OS        | String  | Detailed guest OS info from QEMU guest agent         |
| `connect_openshiftvirt_template`   | OpenShift VM Template        | String  | OpenShift template used to create the VM             |
| `connect_openshiftvirt_description`| OpenShift VM Description     | String  | VM description from annotations                      |
| `connect_openshiftvirt_ip_addresses` | OpenShift VM IP Addresses  | String  | IP addresses reported by VMI network interfaces      |
### Node Properties

The app discovers the following properties for each OpenShift cluster node:

| Property Tag                                | Label                                | Type    | Description                                          |
|---------------------------------------------|--------------------------------------|---------|------------------------------------------------------|
| `connect_openshiftvirt_node_name`           | OpenShift Node Name                  | String  | Node name                                            |
| `connect_openshiftvirt_node_role`           | OpenShift Node Role                  | String  | Node role (control-plane, worker, etc.)              |
| `connect_openshiftvirt_node_status`         | OpenShift Node Status                | String  | Node readiness status (Ready, NotReady, Unknown)     |
| `connect_openshiftvirt_node_cpu_capacity`   | OpenShift Node CPU Capacity (cores)  | Composite | Total CPU cores available on the node (supports fractional values) |
| `connect_openshiftvirt_node_cpu_allocatable`| OpenShift Node CPU Allocatable (cores)| Composite | CPU cores available for pod scheduling (supports fractional values, e.g. 79.5) |
| `connect_openshiftvirt_node_memory_capacity_gb` | OpenShift Node Memory Capacity (GB) | Composite | Total memory available on the node in GB       |
| `connect_openshiftvirt_node_memory_allocatable_gb` | OpenShift Node Memory Allocatable (GB) | Composite | Memory available for pod scheduling in GB |
| `connect_openshiftvirt_node_os_image`       | OpenShift Node OS Image              | String  | Operating system image running on the node           |
| `connect_openshiftvirt_node_kernel_version` | OpenShift Node Kernel Version        | String  | Linux kernel version running on the node             |
| `connect_openshiftvirt_node_container_runtime` | OpenShift Node Container Runtime  | String  | Container runtime version (CRI-O, etc.)              |
| `connect_openshiftvirt_node_kubelet_version`| OpenShift Node Kubelet Version       | String  | Kubelet version running on the node                  |
| `connect_openshiftvirt_node_labels`         | OpenShift Node Labels                | String  | Kubernetes labels applied to the node                |
| `connect_openshiftvirt_node_taints`         | OpenShift Node Taints                | String  | Node taints that affect pod scheduling               |
| `connect_openshiftvirt_node_vm_count`       | OpenShift Node VM Count              | Integer | Number of VMs running on this node                   |
| `connect_openshiftvirt_node_schedulable`    | OpenShift Node Schedulable           | Boolean | Whether the node is schedulable (not cordoned)       |


## Actions

### VM Actions

The app supports the following actions for VM lifecycle management:

| Action                               | Description                           | Undo Support |
|--------------------------------------|---------------------------------------|--------------|
| `connect_openshiftvirt_start`        | Start a stopped VM                    | Yes (Stop)   |
| `connect_openshiftvirt_stop`         | Stop a running VM                     | Yes (Start)  |
| `connect_openshiftvirt_restart`      | Restart a running VM                  | No           |
| `connect_openshiftvirt_pause`        | Pause a running VM                    | Yes (Unpause)|
| `connect_openshiftvirt_unpause`      | Unpause a paused VM                   | Yes (Pause)  |
### Node Actions

The app supports the following actions for node maintenance:

| Action                               | Description                           | Undo Support    |
|--------------------------------------|---------------------------------------|-----------------|
| `connect_openshiftvirt_cordon`       | Mark node as unschedulable            | Yes (Uncordon)  |
| `connect_openshiftvirt_uncordon`     | Mark node as schedulable              | Yes (Cordon)    |
| `connect_openshiftvirt_drain`        | Cordon node (simplified implementation) | No            |


## Files

| File                                | Purpose                                                      |
|-------------------------------------|--------------------------------------------------------------|
| `system.conf`                       | App metadata, connection fields, and UI panels               |
| `property.conf`                     | Property definitions, actions, and script mappings           |
| `openshiftvirt_lib.py`              | Shared library with HTTP helpers and parsing functions       |
| `openshiftvirt_test.py`             | Test script to validate connectivity                         |
| `openshiftvirt_poll.py`             | Discovery script that fetches all VMs and Nodes              |
| `openshiftvirt_resolve.py`          | Per-host property resolution script for VMs                  |
| `openshiftvirt_start.py`            | Action script to start a VM                                  |
| `openshiftvirt_start_cancel.py`     | Undo script for start action                                 |
| `openshiftvirt_stop.py`             | Action script to stop a VM                                   |
| `openshiftvirt_stop_cancel.py`      | Undo script for stop action                                  |
| `openshiftvirt_restart.py`          | Action script to restart a VM                                |
| `openshiftvirt_pause.py`            | Action script to pause a VM                                  |
| `openshiftvirt_pause_cancel.py`     | Undo script for pause action                                 |
| `openshiftvirt_unpause.py`          | Action script to unpause a VM                                |
| `openshiftvirt_unpause_cancel.py`   | Undo script for unpause action                               |
| `openshiftvirt_resolve_node.py`     | Per-host property resolution script for nodes                |
| `openshiftvirt_cordon.py`           | Action script to cordon a node                               |
| `openshiftvirt_cordon_cancel.py`    | Undo script for cordon action                                |
| `openshiftvirt_uncordon.py`         | Action script to uncordon a node                             |
| `openshiftvirt_uncordon_cancel.py`  | Undo script for uncordon action                              |
| `openshiftvirt_drain.py`            | Action script to drain a node                                |
| `images/`                           | Icon directory for UI elements                               |

## Troubleshooting

### Authentication Failed (401)
- **Cause**: Invalid or expired ServiceAccount token
- **Solution**: Regenerate the token and update the configuration:
  ```bash
  oc create token forescout-sa -n forescout-connect --duration=8760h
  ```

### Authorization Failed (403)
- **Cause**: ServiceAccount lacks RBAC permissions
- **Solution**: Verify ClusterRole and ClusterRoleBinding are correctly configured. Check permissions:
  ```bash
  oc auth can-i list virtualmachines.kubevirt.io --as=system:serviceaccount:forescout-connect:forescout-sa
  oc auth can-i update virtualmachines/start.subresources.kubevirt.io --as=system:serviceaccount:forescout-connect:forescout-sa
  oc auth can-i patch nodes --as=system:serviceaccount:forescout-connect:forescout-sa
  ```

### KubeVirt API Not Found (404)
- **Cause**: OpenShift Virtualization operator is not installed
- **Solution**: Install the OpenShift Virtualization operator via OperatorHub in the OpenShift console

### VMs Show CPU 0 or Memory 0
- **Cause**: VM spec does not define CPU/memory (values are in VMI spec instead)
- **Solution**: This is expected behavior. The app now checks VMI spec as a fallback. Ensure VMs are running to get accurate resource info.

### No IP Address for Running VM
- **Cause**: VM network interface has no IP assigned, or QEMU guest agent is not running
- **Solution**: 
  - Verify the VM has a network interface configured
  - Install and enable `qemu-guest-agent` inside the VM guest OS
  - Check VMI status: `oc get vmi <vm-name> -n <namespace> -o yaml | grep -A5 interfaces`

### Connection Error from Forescout
- **Cause**: Network connectivity issue or proxy misconfiguration
- **Solution**:
  - Verify the Forescout appliance can reach the OpenShift API URL
  - Check proxy settings if using a proxy
  - Verify firewall rules allow traffic on port 6443

### Actions Fail with "VM Not Found"
- **Cause**: VM name or namespace changed since discovery
- **Solution**: Trigger a new discovery cycle to refresh VM data
### Nodes Not Discovered
- **Cause**: Nodes do not have IP addresses assigned (rare, but possible in some configurations)
- **Solution**: Ensure nodes have valid internal IP addresses. Check with: `oc get nodes -o wide`

### Node Actions Fail with "Forbidden"
- **Cause**: ServiceAccount lacks `patch` permission on `nodes` resource
- **Solution**: Ensure the ClusterRole includes `patch` verb for nodes:
  ```bash
  oc auth can-i patch nodes --as=system:serviceaccount:forescout-connect:forescout-sa
  ```

### Drain Action Only Cordons Node
- **Cause**: This is expected. The drain action is a simplified implementation that only cordons the node without performing pod/VM eviction.
- **Solution**: To perform a full drain with eviction, use the `oc` CLI directly: `oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data`


### Logs Location
Forescout Connect App logs are located on the appliance at:
```
/usr/local/forescout/plugin/connect/<app-name>/logs/
```

Enable debug logging in **Tools > Options > Connect > Advanced** to see detailed API request/response logs.

## Version History

- **1.0.0** (Initial Release)
  - VM discovery and property resolution
  - Lifecycle actions (start, stop, restart, pause/unpause)
  - Support for MAC and IP-based endpoint identification
  - CPU/memory parsing from VMI spec fallback
- **1.0.1** (Bug Fix & Documentation)
  - Fixed CPU/memory parsing from VMI spec
  - Added comprehensive README documentation
- **1.0.2** (Branding Update)
  - Updated all property labels to include "OpenShift" prefix
- **1.0.3** (Node Discovery)
  - Added OpenShift node discovery as endpoints
  - Added 15 node properties (capacity, allocatable, status, role, etc.)
  - Added 3 node management actions (cordon, uncordon, drain)
- **1.0.4** (Node CPU Precision)
  - Improved node CPU quantity parsing to preserve millicore precision
  - Node CPU values now support fractional cores (e.g., `79500m` -> `79.5`)
