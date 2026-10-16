# DNS Queries Connect App 1.0.0

## Contact Information

Forescout Technologies, Inc.  
190 West Tasman Drive  
San Jose, CA 95134 USA  
https://www.Forescout.com/support/  
Toll-Free (US): 1.866.377.8771  
Tel (Intl): 1.408.213.3191  
Support: 1.708.237.6591

## About the Documentation

Refer to the Technical Documentation page on the Forescout website for additional documentation: https://www.Forescout.com/company/technical-documentation/

Have feedback or questions? Write to documentation@forescout.com.

## Legal Notice

© 2026 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation. A list of Forescout trademarks and patents is available at https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks. Other brands, products, or service names may be trademarks or service marks of their respective owners.

eyeExtend Connect app for DNS query visibility. This is the initial public 1.0.0 release.

## Target-device scope

The new **Target devices** option lets an operator choose:

- **Only devices with Function = Unknown** — the default. Retain query events for all client IPs, return the DNS Queries property only when the resolver receives an endpoint whose `function` is `Unknown`, and clear an existing value when it becomes classified.
- **All devices** — an explicit opt-in that publishes DNS domains immediately for every endpoint matched by the query client IP.

The default protects performance and limits property churn in large deployments. Unknown-only mode preserves observations if an endpoint later becomes Unknown, while preventing DNS data from being published to currently classified endpoints. Configure policy/property rechecks so the resolver evaluates the current Function classification.

## Result

- Property label: **DNS Queries**.
- Property tag: `connect_dnsqueries_domains` (the approved replacement for `fsapi_DNS_queries`). Connect requires its own property namespace.
- Keeps the **20 most recently seen distinct domains per client IP**, with a **seven-day** window. Repeated queries refresh recency; A and AAAA queries for the same domain share one entry. Domain names are lowercase with at most one terminal root-label dot removed; malformed empty labels are rejected. The returned list is alphabetically ordered; selection is based on recency.
- Retention uses the time Forescout processes the message, not its syslog timestamp. Replaying old logs makes them newly observed.
- Uses the DNS client IP inside the event, not the syslog sender IP or an answer's IP.
- Cached answers, forwarded queries, replies, unrelated messages, and loopback/link-local/multicast/unspecified clients are ignored. `_ldap._tcp` names are supported.
- Updates existing endpoints without changing their online status. It does not intentionally create hosts from syslog.

## Install and configure

1. Import `ForeScout-eca-dnsqueries-1.0.0.eca` in **Options > Connect > Import**, using your existing allowance for unsigned apps.
2. Add an app configuration. Choose a descriptive Source name, leave **Target devices** at its safe default (**Only devices with Function = Unknown**) unless broad enrichment is required, and select **dnsmasq** as the DNS log format.
3. Assign the connecting Forescout appliance. Enable **Use Syslog Source** and enter **192.168.2.98** for the sender in the supplied capture. If a relay forwards the logs, use the source identity Forescout actually receives from that relay. Configure each source once.
4. Ensure the Forescout Syslog plugin receives the traffic at **192.168.2.94** on the configured listener/transport; the supplied capture uses UDP 514. The app consumes the existing Syslog plugin stream and does not bind another socket. The sender/relay must preserve the original DNS event and its client IP. Keep dnsmasq query logging enabled.
5. Apply the configuration and run **Test**. This checks parser settings and Connect persistent storage; it cannot prove network delivery. Start the app.
6. **Required for expiry on idle devices:** create an eyeSight policy in the desired endpoint scope that evaluates the **DNS Queries** property, and configure its property/policy recheck interval to **five minutes**. Verify a recheck invokes `dnsqueries_resolve.py`. Expired values are removed on new query events or property resolves. Without rechecks, a silent device's displayed values can remain past seven days; with five-minute rechecks, expect up to five minutes of display delay.
7. Inspect an existing device's **DNS Queries** property after a real DNS request. For the supplied examples, `192.168.2.96` should receive `demo-rancher.serapisdev.com`; `192.168.2.94` and `192.168.2.92` should receive `_ldap._tcp.ie.com` and `_ldap._tcp.ie.es`. The `ui.com` query from `127.0.0.1` is ignored.

The app requires the Connect `persistent_util.PersistUtil` feature documented in Forescout's App Building Guide v2.0.3. The Test button should fail clearly if the installed Connect runtime does not expose it. The package deliberately uses no unsupported file access, process execution, or socket listener.

## Other syslog/DNS sources

Syslog is a transport, not a uniform DNS event format. Any sender or relay supported by the Forescout Syslog plugin can be used; arbitrary DNS payloads still need a suitable parser. Choose one of:

| Mode | Accepted payload |
| --- | --- |
| dnsmasq | `query[A] example.com from 192.168.2.96`, including dnsmasq extra-log prefixes |
| Automatic | dnsmasq query format or the BIND format below |
| BIND query log | `client 192.168.2.96#53420 (example.com): query: example.com IN A +` (also accepts `client @0x...`) |
| Normalized JSON | `{"event":"query","client_ip":"192.168.2.96","qname":"example.com"}` after an optional syslog header |
| Custom query expression | A bounded custom-expression template containing named groups `client_ip` and `domain` |

Example custom payload:

```text
DNS_QUERY src=192.168.2.96 name=example.com
```

Custom expression:

```text
DNS_QUERY src=(?P<client_ip>\S+) name=(?P<domain>\S+)$
```

Custom expressions are intentionally not general Python regular expressions. They must have fixed literal text before and between the two named groups, end with the second group followed by `$`, and each group must be one of `\S+`, `\d+`, or `\w+`. The named groups may appear in either order. This restricted form uses a bounded deterministic matcher and prevents a configuration or syslog payload from causing regex backtracking. Validate another vendor's expression against actual query and reply samples before deployment. Messages over 16 KiB, multiline payloads, and non-ASCII names that are not already punycode are ignored.

## Persistence, matching, and operating limits

Connect stores each domain observation under its own client-IP and absolute-day key in a rotating eight-day table ring. This avoids cross-worker read/modify/write loss: concurrent observations use different keys. A property resolve enumerates the eight bucket tables to collect records for its client IP and returns at most 20 domains. On the first event that reuses a table, maintenance removes only keys from older bucket generations, so overlapping workers cannot remove a fresh record.

The app uses eight rotating event tables and one health-check table, within the documented ten-table limit. Each table is limited by Connect's documented 100 MB table limit. When a table is reused after eight days, the first incoming event removes keys from older generations. This is an initial visibility integration, not a high-throughput DNS analytics store; sustained production event rates require an appliance load test. Storage errors return an error rather than pretending the query was saved.

Syslog processing is enabled on all appliances (`focal only syslog: false`) so host property resolves can use the local cache on the managing appliance. Verify forwarding and resolution in your deployment. Configure sources sharing an IP namespace consistently. Caches are local to each appliance; historical data is not guaranteed to move when host management or appliance assignments change. Rechecks for devices that no longer exist will not occur, so their cached records can remain until that IP is processed again or app data is administratively removed.

IP is the only endpoint identity in the supplied logs. NAT, overlapping address spaces, and DHCP address reuse cannot be disambiguated without additional identity data; history may follow a reused IP during the seven-day window. No API credentials are needed. There is no outbound API call or transmission of DNS data from this app.

## References

Based on the configuration and runtime contracts in the [Forescout eyeExtend-Connect repository](https://github.com/Forescout/eyeExtend-Connect), including its DHCP syslog examples and App Building Guide (property naming/list replacement, syslog response objects, injected library files, and Persistent Data).

See also [Forescout Connect syslog support](https://docs.forescout.com/eyeextend/eyeextend-connect-plugin/eyeextend-connect-plugin/leverageplugins.htm) and [app import documentation](https://docs.forescout.com/eyeextend/eyeextend-connect-plugin/eyeextend-connect-plugin/buttons-connect-pane.htm). This custom app is not signed or certified by Forescout. If published to the public eyeExtend-Connect repository, it is community contributed and community supported rather than covered by Forescout Customer Support.
