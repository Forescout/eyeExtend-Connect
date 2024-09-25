# Connect SentinelOne
Connect plugin for ForeScout

Forescout connect plugin for SentinelOne using EyeConnect (OIM) module.

## **Release Notes**

### **Version 1.1.2**
- **New Features:**
  - Added a **hostname down select** feature which forces the resolver to use both MAC and Hostname. This helps eliminate MAC address collisions, particularly in cases such as VPN clients.

- **Improvements:**
  - Abandoned the legacy `urllib` library in favor of the more modern and efficient `requests` library, enhancing the plugin's stability and compatibility with modern APIs.
  - Updated **debug logging** to provide more granular and detailed information, improving the troubleshooting experience for users and support teams.

### **Version 1.1.0**
- **New Features:**
  - Enhanced API integration for more comprehensive asset information retrieval.
  - Improved automation capabilities for asset management and alerting:
    - Decommissioning
    - Network quarantine
    - Initiate system scan
  - Added support for 64 SentinelOne data fields.

- **Bug Fixes:**
  - Fixed an issue causing intermittent connection failures.
  - Resolved data mismatch issues between Forescout and SentinelOne assets.

- **Improvements:**
  - Optimized data import process for faster synchronization.
  - Enhanced logging for better troubleshooting and support.

**Summary:** This release of the Forescout SentinelOne integration plugin introduces significant enhancements to API integration, allowing for more comprehensive asset information retrieval and improved automation capabilities. Additionally, various bugs have been fixed, and performance improvements have been made to ensure a smoother user experience. The plugin now supports 64 additional SentinelOne data fields, providing users with a more detailed view of their assets. Automation capabilities have been expanded to include decommissioning, network quarantine, and the ability to initiate system scans.

## **Requirements**
- Valid OIM subscription
- SentinelOne subscription with API access

## **Configuration**
- **SentinelOne Management URL:** (e.g. [https://usea1-012.sentinelone.net/login](https://usea1-012.sentinelone.net/login))
- **SentinelOne API:** 

## **Functions**
Utilizes Forescout to compare online Forescout assets against SentinelOne. If the asset exists in SentinelOne, the plugin then imports various agent information. The user can then add further automation in the form of responses such as auto disconnect via Forescout or alerting.

## **Example Output**
![SentinelOne ForeScout Actions](https://github.com/PoesRaven/public/blob/068bb61035595a2d7336f7fc6e11e9f6ab21e362/ForescoutS1Actions.png?raw=true)

![SentinelOne ForeScout Properties](https://raw.githubusercontent.com/PoesRaven/public/068bb61035595a2d7336f7fc6e11e9f6ab21e362/ForescoutS1Properties.png)

![SentinelOne ForeScout Results](https://raw.githubusercontent.com/PoesRaven/public/068bb61035595a2d7336f7fc6e11e9f6ab21e362/ForescoutS1Results.png)

