
Forescout eyeExtend Connect Prometheus App README.md
 
## Contact Information
Forescout Technologies, Inc.
190 West Tasman Drive
San Jose, CA 95134 USA
https://www.Forescout.com/support/
Toll-Free (US): 1.866.377.8771
Tel (Intl): 1.408.213.3191
Support: 1.708.237.6591

## About the Documentation
- Refer to the Technical Documentation page on the Forescout website for additional documentation:
https://www.Forescout.com/company/technical-documentation/
- Have feedback or questions? Write to us at documentation@forescout.com

## Legal Notice
© 2020 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation.
A list of our trademarks and patents can be found at [https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks](https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks).
Other brands, products, or service names may be trademarks or service marks of their respective owners.

## About the eyeExtend Connect Prometheus App
[Prometheus](https://prometheus.io/docs/introduction/overview/) is an open-source systems monitoring toolkit that provides real-time metrics in a time series database (allowing for high dimensionality) built using a HTTP pull model, with flexible queries.

There are a number of [libraries and servers](https://prometheus.io/docs/instrumenting/exporters/) which help in exporting existing metrics from third-party systems as Prometheus metrics.

The Prometheus App discovers endpoint [targets](https://prometheus.io/docs/prometheus/latest/querying/api/#targets) and verifies that the target is valid in cache before attempting to query the database. Metrics are then queried and computed for the endpoint and returned as properties on the eyeSight Appliance.

A number of policy examples are provided in the "Prometheus System Templates" which can be tuned as appropriate for the customer use case.


## 1.0.0 Release
The 1.0.0 release of the Prometheus App provides:

#### Properties from the [Windows exporter](https://github.com/prometheus-community/windows_exporter):

<table>
<thead>
  <tr>
    <th>Property</th>
    <th>Value</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>connect_prometheus_win_load5</td>
    <td>Windows 5 Minute CPU Load Average</td>
  </tr>
  <tr>
    <td>connect_prometheus_win_load15</td>
    <td>Windows 15 Minute CPU Load Average</td>
  </tr>
  <tr>
    <td>connect_prometheus_win_disk</td>
    <td>Windows C Drive Percentage Use</td>
  </tr>
    <tr>
    <td>connect_prometheus_win_ram</td>
    <td>Windows Physical Memory Use</td>
  </tr>
</tbody>
</table>


#### Metrics from the [(Linux) Node Exporter](https://prometheus.io/docs/guides/node-exporter/):

<table>
<thead>
  <tr>
    <th>Property</th>
    <th>Value</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>connect_prometheus_lin_load5</td>
    <td>Linux 5 Minute CPU Load Average</td>
  </tr>
  <tr>
    <td>connect_prometheus_lin_load15</td>
    <td>Linux 15 Minute CPU Load Average</td>
  </tr>
  <tr>
    <td>connect_prometheus_lin_rootfs</td>
    <td>Linux rootfs percent used</td>
  </tr>
    <tr>
    <td>connect_prometheus_lin_ram</td>
    <td>Linux RAM percent used</td>
  </tr>
    <tr>
    <td>connect_prometheus_lin_swap</td>
    <td>Linux SWAP percent used</td>
  </tr>
    <tr>
    <td>connect_prometheus_lin_cpu_count</td>
    <td>Linux Total # of CPU</td>
  </tr>
    <tr>
    <td>connect_prometheus_lin_uptime</td>
    <td>Linux Machine Uptime</td>
  </tr>
</tbody>
</table>


## Requirements

The App supports:

* Tested with Prometheus Version 2.18.1
* Forescout eyeExtend Connect 1.2
* See license.txt file for license information

## Licenses
This App bundles with a license.txt file. Please review the license.txt file.
