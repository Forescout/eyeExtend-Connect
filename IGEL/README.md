# Forescout eyeExtend Connect for IGEL 
 
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
A list of our trademarks and patents can be found at <https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks>. Other brands, products, or service names may be trademarks or service marks of their respective owners.

## About the eyeExtend Connect for IGEL

IGEL (https://igel.com) provides an endpoint operating system for Virtual Desktop Infrastructure (VDI) which installs on all manner of devices. These thin clients are very common in hospitals and other healthcare organziations. The IGEL OS communications to the IGEL Universal Management Server (UMS) to recieve its configuration, updates, and controls.

This integration queries the UMS API to pull information into Forescout eyeSight/eyeControl and then policies can be built around those attriubtes.

Items provided from the IGEL UMS

- IGEL ID

- IGEL Firmware ID

- IGEL Last IP

- IGEL Links

- IGEL MAC Adress

- IGEL Moved to Bin

- IGEL Name

- IGEL Object TYpe

- IGEL Parent ID

- IGEL Unit ID

All of these can be used in a Forescout Policy

## Requirements

The App supports:

- Forescout eyeSight 8.2 or higher

- IGEL Management Suite 6

## Configuration of the Plugin

After installing the Connect Module and the Connect App, a connection to the IGEL UMS is needed. The following information is required:

- Hostname/IP Address of the UMS

- Port

- IGEL Username

- IGEL Password

- Server Certificate

- Refresh Rate

The IGEL Connect App can also be used for Host Discovery if the check box is enabled in the "IGEL Options" section of configuration.
