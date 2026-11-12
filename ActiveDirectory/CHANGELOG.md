# Change history

This file records version-by-version changes to the Active Directory Connect app.

Version **0.3.33** normalizes the policy-template subgroup name from the
accidental plural **User Objects** to singular **User Object**, matching the
existing **Computer Object** subgroup. Its internal subgroup identifier, XML
folder, and icon path are now `connect_activedirectory_user_object`,
`User Object/`, and the corresponding singular icon path. Runtime property and
action identifiers are unchanged. The release workflow also creates a minimal,
versioned Forescout submission bundle containing the user guide, dependencies,
change history, and matching unsigned app ZIP.

Version **0.3.32** replaces the three User Objects internal template identifiers
so Connect 2.0.7's generated `ORDER` values display them as 1.0, 1.1, and 1.2.
Inspection of the installed framework showed that it stores policy definitions
in a default Java `HashMap` and assigns `ORDER` while iterating `entrySet()`;
changing the JSON array sequence in 0.3.31 therefore had no effect. The new IDs
use distinct ascending map buckets while visible labels, XML, and groups remain
unchanged.

Version **0.3.31** gives Computer Object and User Objects distinct computer/person
subgroup icons derived from the matching action icon artwork. Its attempted JSON
array reordering did not change the appliance's User Objects order. Manual
deployment files now live under `dependencies/`: the group export remains separate from the
endpoint collector, and the self-contained collector BAT is the only endpoint
script distributed. The obsolete standalone PS1 was removed so it cannot be
selected as a second Script Repository input and create an unused script-result
property.

Version **0.3.30** declares **Computer Object** and **User Objects** through
Connect's `policy_template_sub_groups` schema and assigns the five corresponding
templates to those subgroup identifiers. **Collect Computer/User Object GUIDs**
has no subgroup and remains directly under **Active Directory**. Subgroup icons
are packaged in their own `templatedirs` paths, matching the working C2C
Reporting app structure. The 0.3.29 appliance screenshot confirmed that nested
XML filenames alone render as a flat list; a later appliance screenshot confirms
that the explicit 0.3.30 subgroups render as the intended folders.

Version **0.3.29** replaces the prior single Script Runner template with the six
supplied Console exports. **Collect Computer/User Object GUIDs** remains at the
root of the Active Directory template group. Match-status and group-check
templates retain the `Computer Object` and `User Objects` XML folder paths. Those
paths were later confirmed not to create Console subgroups; 0.3.30 adds explicit
subgroup metadata. Every packaged policy and action is disabled, and every
exported segment is reduced to the anonymized `10.0.0.0/8` scope. Import/Apply
confirmed that all six templates were present but displayed as a flat list.

Version **0.3.28** includes disconnected RDP sessions in the endpoint GUID
collector because those users remain signed in. Multiple sessions for the same
account count once; different signed-in accounts remain ambiguous. Replace the
BAT in Forescout's Windows script repository using the updated
`dist/ConnectAD-GUID-Policy.zip`; importing the app alone does not deploy this
change. The filename, result schema/tag, policy timing, dependencies, and app
runtime are unchanged. See [collector behavior and deployment](docs/guid-policy.md#endpoint-requirements-and-behavior).

Version **0.3.27** displays **No user** in Managed User GUID Script Result when
the collector reports `no_active_user`, retaining the original collection time
and schema while removing all account identity fields. Each new collection time
can change the managed evidence value. Missing raw evidence still clears it.
When User Object finds no current AD user, its response clears both User Object
and User Groups, without waiting for a Groups resolver on an empty dependency.
Current native username fallback, dependency definitions, and collection timing
are preserved. See [the logout behavior and lab checks](docs/user-session-clearing.md).

Version **0.3.26** recognizes Forescout's expanded empty composite dependencies.
The live 0.3.25 trace showed that a stored `{}` reached User Object as empty
strings plus a zero collection date; it failed schema validation and left the
old successful match visible. Both managed-user and User Object input handling
now accept only correctly typed empty defaults as a clear. This lets the empty
state pass through to User Groups. Populated/malformed evidence still undergoes
normal validation. See [the captured input and verification](docs/user-session-clearing.md).

Version **0.3.25** explicitly replaces stale user properties on logout and local
login. Missing/no-active-user collector results return an empty managed-user
composite; local-user evidence replaces the previous account's fields. User
Object becomes empty when no AD user is available or a local login is detected,
and an empty/missing User Object clears User Groups without querying AD. Native
username fallback remains available when the collector has no user identity.
Dependencies, collector timing, and group-action safeguards are unchanged. See
[the live diagnosis and deployment check](docs/user-session-clearing.md).

Version **0.3.24** exposes **[Connect AD] Computer Groups** and **[Connect AD]
User Groups** in the Console Inventory tab. Both group devices by the full
Group DN only. User Groups shows devices whose matched AD user belongs to the
selected group. Existing membership data, dependencies, and lookup schedules
are unchanged. See [using AD groups in Inventory](docs/configuration.md#ad-groups-in-inventory).

Version **0.3.23** lets Computer Object fall back to scoped name matching when
the collected computer GUID is invalid, empty, missing, or returns no matching
AD computer. A successful GUID match still takes precedence; a name match earns
the confidence of the actual NetBIOS, DHCP, or DNS source. Domain mismatches,
`not_domain_joined`, ambiguous results, and LDAP errors still stop resolution.
Group actions retain strict GUID checks; Groups follows the GUID of the newly
matched Object. User matching and property dependencies are unchanged.

Version **0.3.22** adds **Check certificate revocation (CRL)**, enabled by default.
With **Validate server certificate** enabled, clearing the new checkbox skips
CRL checks while retaining Forescout's trust store, certificate-chain/validity
checks, and hostname validation. It applies to LDAPS and required StartTLS,
including lookups, actions, and undo. Revoked certificates may be accepted when
CRL checking is disabled. The setting is ignored for plaintext LDAP or when
server validation is disabled. See [TLS settings and verification](docs/tls-validation.md).

Version **0.3.21** makes Computer Groups depend only on Computer Object, and
User Groups only on User Object, with both redo flags enabled. Separate Groups
resolvers read memberships live by the matched Object GUID and publish only
Groups. Object resolvers retain native-name/managed-evidence matching and publish
only Object. Successful add/remove/undo actions still return live Groups
immediately. No collection timing changes. See the [dependency graph and cache
limitations](docs/property-dependencies.md); live dependency propagation remains
to be verified after import/Apply.

Version **0.3.20** honors **Validate server certificate** for both LDAPS and
required StartTLS. It uses Forescout's supplied `ssl_context` unchanged, including
its nonvalidating context when the checkbox is cleared. TLS still must succeed
before binding. Connection errors now include the certificate verification or
OpenSSL handshake reason; a missing CRL identifies Forescout's revocation-store
requirement. The lab's checked-validation failure was reproduced as **unable to
get certificate CRL** for `lab-AD01-CA`. See [TLS behavior and lab evidence](docs/tls-validation.md).

Version **0.3.19** restores Computer Groups dependencies on `hostname`,
`hostnames_list`, `nbthost`, `nbtdomain`, `dhcp_hostname_v2`, and
`connect_activedirectory_managed_computer_guid_script_details`, with both redo
flags enabled. It consumes managed computer evidence and supports hostname
fallback again. These direct Groups dependencies are superseded by 0.3.21.

Version **0.3.18** changed the property dependency graph (the Computer Groups
exception below is superseded by 0.3.19).
Both managed GUID properties depend only on the raw script result. Computer
Object uses the managed-computer composite; User Object and User Groups use
the managed-user composite, retaining their native name dependencies. Computer
Groups has a separate resolver whose only dependency is the raw script result;
it requires the collected computer GUID. Parsing user evidence no longer reads
native usernames; the AD user lookup still checks them against the observation.
Successful group actions continue to return a fresh Groups list immediately.
Collection timing and policy settings are unchanged.

Version **0.3.17** returns a freshly queried **Computer Groups** or **User
Groups** list in each successful group action's response. After add/remove
verification, it reads the same account by GUID on the same DC and retrieves
all direct and primary memberships, including other changes visible to that
DC. Successful no-op actions and membership-changing cancellation undo also
refresh the list. A failed refresh preserves the confirmed action/undo cookie,
reports the problem in Last group action's Reason, and does not publish a
partial list or repeat the write. See [post-action refresh](docs/action-group-refresh.md).

Version **0.3.16** adds Windows Active Users (`va_comp_users_logged_in`), Linux
User (`linux_logged_users`), and Macintosh User (`mac_logged_users`) as username
fallbacks alongside `user`. Windows domain/name pairs retain their NetBIOS
qualification and must match the connection's configured domain alias. All
four sources initially triggered refresh of User Object, User Groups, and Managed
User GUID Script Result; 0.3.18 removes them from the managed evidence property's
dependencies. A username change still blocks lookup with incompatible GUID evidence;
it never substitutes a different user's GUID or fabricates collector output.
The collection template now includes a disabled **Recheck Host** action in the
Windows Users Change subrule. Enable it in the deployed policy to request a
fresh native collection on a matching change. Importing the app does not modify
existing policies. See [username sources and deployment checks](docs/username-sources.md).

Version **0.3.15** preserves **Last group action** when a failed or uncertain
action is cancelled without a successful-action cookie. Cancellation still
finishes without contacting AD, but no longer overwrites the original Result,
Reason, Time, or target details with a cancellation row. A live 0.3.14 trace
confirmed that overwrite after a denied action. This fixes that separate loss
of diagnostics. Separately, live lab core logs showed Reason being discarded as
an unknown subfield despite the updated disk definition. An approved CounterACT
service restart on the owning appliance resolved that mismatch; a new failed
action retained Reason in the stored property. See [diagnostic evidence](docs/action-reason-diagnostics.md).

Version **0.3.14** reports failed add/remove/undo actions through Connect 2.0.7's
failure callback, correcting the success state previously shown for failed
actions. **[Connect AD] Last group action** includes a **Reason** for whitelist
denials, LDAP permissions, invalid/missing groups, and other failures. Account DN
is retained after a fresh lookup and AD server identifies the last attempted DC.
Blank whitelists with Allow any group unchecked block all group changes before
LDAP and now explain that explicitly. Uncertain writes remain **Unknown**, fail
the action, and are never replayed on another DC. Import and Apply the update;
the next action populates the new Reason field. Existing history is not backfilled.

Version **0.3.13** adds separate **Computer Group Whitelist** and **User Group
Whitelist** connection panels. Enter allowed full group DNs, one per line.
An empty/missing whitelist blocks all group changes, including after upgrading
an existing connection. Each panel has an **Allow any group (DANGEROUS)**
checkbox, disabled by default; it bypasses only that object type's whitelist.
The current whitelist also applies to cancellation undo. Removing a group from
the whitelist blocks undo for that group until it is allowed again. Reporting
and collection timing are unaffected. Import and Apply, then configure the
connection's whitelists before resuming group actions. See [configuration](docs/configuration.md#group-whitelists).

Version **0.3.12** adds **[Connect AD] User DN** to every User Groups row. It
contains the matched user's full AD distinguished name, repeated for each linked
or primary group alongside Group DN, Last Successful Lookup, and Responding AD
Server. The value comes from the same lookup as the memberships, with no extra
LDAP query. Import and Apply, then re-resolve User Groups to populate the field.

Version **0.3.11** includes each computer/user account's primary group alongside
its direct `memberOf` groups. AD omits primary membership from `memberOf`, which
previously hid groups such as Domain Computers, Domain Controllers, and Domain
Users. The app derives the primary group's SID from `objectSid` and
`primaryGroupID`, then retrieves its actual full DN from the same domain/DC.
Renamed/custom primary groups work without assuming a group name or container.
This adds one targeted LDAP search per successful lookup; polling and collector
timing are unchanged. Import and Apply, then re-resolve Computer/User Groups.
Nested memberships remain excluded. Primary groups can be reported but not
removed or reassigned by the group actions.

Version **0.3.10** uses the native Forescout `user` property when the collector
reports `no_active_user` without a GUID and one native identity is available.
For example, `administrator` searches AD `sAMAccountName` in the configured
domain and reports **Medium / Unqualified username**. A native value ending
in ` (local)` (case-insensitive) stops user lookup and forward user group actions
before LDAP, even with a cached GUID. Other negative/ambiguous collector states
still block fallback. Managed User GUID Script Result remains unset for
`no_active_user`; User Object/Groups can resolve independently through the name.
Import and Apply, then re-resolve User Object/Groups. No collector or policy
timing change is required.

Version **0.3.9** adds examples to User Object Match Method option labels:
`Domain-qualified username (DOMAIN\username)`,
`User principal name (username@example.com)`, and
`Unqualified username (username)`. Stored option values and matching behavior
are unchanged, preserving existing policy selections. Import and Apply to load
the updated labels.

Version **0.3.8** clarifies failed DNS lookups: each fallback explicitly names
the AD domain searched and distinguishes an exact-domain match from a
parent-domain fallback. Duplicate DNS evidence is shown once.

Version **0.3.7** adds a second computer lookup when the observed-name search
returns no objects. For DNS properties `hostname` and `hostnames_list`, it splits
the first hostname label from the suffix, then searches `sAMAccountName=<label>$`
if that suffix equals the connection's AD domain or is a child of it. For a
`lab.REDACTED.com` connection, `nas-simulator.lab.REDACTED.com` tries
`nas-simulator$`, and `proxy01.kasm.lab.REDACTED.com` tries `proxy01$`;
`Media-Manager.home.REDACTED.com` cannot use this fallback. Matches report
**Low / DNS-derived account name**. No extra query runs after a successful or
ambiguous initial match. Import and Apply, then re-resolve Computer Object/Groups.
See [lookup scope and connection routing limitations](docs/configuration.md).

Version **0.3.6** adds **[Connect AD] Match Confidence** and **[Connect AD] Match
Method** to both Object composites. Confidence offers Exact, High, Medium,
and Low in policy conditions; each resolved object has one confidence value.
The strongest identifier that actually matched determines the value, without
extra LDAP queries. Import and Apply, then re-resolve Computer/User Object.
See [confidence definitions and validation](docs/match-confidence.md).

Version **0.3.5** reports **Computer is not AD joined; not attempting the lookup**
when the collector returns `not_domain_joined`, without contacting AD.
Read-only computer lookup by name is allowed when the collector
returns `error` without a GUID. The reported computer
domain is checked first; a workgroup/domain mismatch names both the reported
domain and the connection's AD domain. Matching uses all available NetBIOS,
DHCP, and DNS names, and a not-found error lists the names and search base used.
DHCP Hostname (`dhcp_hostname_v2`) is now a dependency. Valid GUIDs retain
precedence, and negative computer collector evidence still blocks group writes.
User fallback from `no_active_user` is added in 0.3.10 as described above.
Import and Apply, then re-resolve Computer Object/Groups.

Version **0.3.4** changes Computer/User Groups to a composite list with one row
per full group DN, repeating the lookup time and responding AD server. Connect
2.0.7 converts nested string lists into JSON text, which caused the displayed
array. Group DN is now a scalar subfield. Each successful lookup replaces the
whole list; in 0.3.4, zero linked memberships returned an empty list, with lookup
metadata still available in Object. Import and Apply the app, then re-resolve both Groups
properties. Existing internal tags, connection settings, and collector remain
unchanged. See [converter evidence and upgrade checks](docs/group-list-compatibility.md).

Version **0.3.3** updates **Collect AD Object GUIDs** from the supplied
`User Object GUIDs.xml` export. It preserves the main managed-device group
condition, the new **User Change - Update Object GUIDs** subrule, the fallback
collection subrule, and exported timing. The policy is packaged disabled with
an anonymized scope. Both script conditions use the same confirmed result tag.
Import and Apply the app before using the renamed-schema collector; running the
new BAT with an older applied app can produce `Unsupported GUID collector schema`.

Version **0.3.2** renames the collector result schema to `connectad-guid-v1`.
Managed Computer GUID evidence contains only status, collection time, schema,
GUID, DNS domain, and account name. UPN and Session Identity are user-only fields.
All evidence identity fields are scalar strings; unavailable values are omitted.
Import and Apply this app before replacing `ConnectAD-CollectObjectGuids.bat` in
Forescout's script repository. The app accepts cached `nativead-guid-v1` results
while the collector rolls out. Keep the same filename and policy parameters;
the existing script-result tag and collection timing stay valid.

Version **0.3.1** fixes `expecting COMPOSITE` when resolving Computer/User Object
on Connect 2.0.7. Account Expiration Date is a scalar epoch date when set and is
omitted for never-expiring accounts. The previous empty/single-element date
arrays fail Connect's composite converter. See the [diagnosis and verification](docs/composite-date-compatibility.md).
Import the updated app, Apply, and resolve the Object properties again; the
connection settings, property tags, and endpoint collector are unchanged.

Version **0.3.0** expands Managed Computer/User Object GUID Script Result into
composites containing collection status/time, schema, GUID, domain, account name,
UPN, and session identity. Missing results and `no_active_user` leave the entire
property unset. Version 0.3.0 used zero-or-one lists for optional values; 0.3.2
replaces these with omitted/scalar subfields.
The new internal tags end in `_guid_script_details`; replace existing conditions
on the old scalar `_guid_script_result` tags with the new composite subfields.

All four group actions are cancellable and include **Undo when action cancelled**,
checked by default. Cancellation restores prior membership only when the action
recorded a verified change. Uncheck the option before applying an action to retain
its change on cancellation. See [cancellation behavior](docs/action-cancellation.md)
for identity checks, original-DC requirements, and pre-upgrade actions.

Version **0.2.3** adds AD's domain-scope control to computer/user subtree searches.
With blank search bases, AD can return a matching account followed by continuation
referrals to subordinate naming contexts; earlier versions rejected the entire
lookup with `LDAP search: referral refused (code 10)`. The control suppresses
those continuations while keeping the lookup within one domain. Unexpected
referrals still fail without returning partial properties or following their URLs.
The original failure and corrected lookup were both verified against the lab DC;
the updated shipped resolution script returned the matching computer and two
direct groups. No live directory changes were performed.

Version **0.2.2** explicitly enables `asset_portal` for all seven app properties.
Missing GUID collector evidence and negative account statuses return no property
value (irresolvable), instead of an empty scalar that can appear as `null` in the
asset view. Valid GUIDs still refresh when the underlying script result changes.

Version **0.2.1** restores the exported **P-Managed Windows Devices** group filter
(ID `4952753181631154625`) in the GUID collection policy. Collection/cache timing
is preserved. The user reports that the lab now runs Connect **2.0.7**; appliance
validation of this build is pending.

Version **0.2.0** uses the supplied Console policy export and confirmed
`script_result.b249e1c035a662f102d2aba7094d9777` dependency. Computer and User each
have an **Object** composite, a **Groups** composite, and a **Managed Computer/User
Object GUID Script Result** property. The nested Group DNs list introduced in
0.2.0 is replaced by one composite row per DN in 0.3.4.
All six properties request re-resolution when the script result first appears or
changes. Parsed GUID properties do not contact AD. The exported collection/cache
timing is preserved, and GUID evidence has no maximum age.

This layout replaces the old flat properties. Update existing policy conditions
to the new composites and their subfields; the new Groups tag is
`connect_activedirectory_<computer|user>_group_details` to avoid changing the type
of an existing tag. The app and connection identifiers remain unchanged.

Version **0.1.9** renames the endpoint collectors to
`ConnectAD-CollectObjectGuids.bat` and `Get-ConnectADObjectGuids.ps1`, with matching
policy XML and deployment bundle names. Existing policies must select the newly
uploaded BAT in their Windows Expected Script Result condition. The JSON result
schema stayed `nativead-guid-v1` in that release; 0.3.2 emits `connectad-guid-v1`.

Version **0.1.8** supplies the policy template group's missing `full_description`
and adds template help text. The 0.1.7 appliance log showed successful import
validation, followed by `JSONObject["full_description"] not found` during Apply
while generating `netlocal.xml`. That interrupted registration of the app's
properties and actions. Packaging now checks `full_description` on both the
template group and each policy. Appliance Apply and GUI visibility need retesting.

Version **0.1.7** labels the main property group **[Connect] Active Directory**
and prefixes every property and composite subfield with **[Connect AD]**. Computer
and user properties retain their object type in the label. Internal identifiers
and the imported app name remain unchanged. The package includes 20 transparent
16×16 PNG icons for the condition/property group, action group, template group,
GUID template, and all four actions with normal, waiting, failed, and gray states.
`make config` regenerates the pixel artwork from `scripts/generate_icons.py`;
no imaging package is required. Packaging checks the expected paths and dimensions.

Version **0.1.6** adds the missing descriptions to the **Servers and Failover**
and **Object Search** wizard panels. The locally installed Console's Connect code
accepts missing descriptions during parsing but dereferences them while building
the Add wizard. An isolated call to that installed method reproduced a
`NullPointerException` with a null message. Packaging now requires a string
description on every panel. Full Console retesting of this version is pending.

Version **0.1.5** renames the imported app to **Active Directory**. Forescout
requires identifiers derived from the app name, so configuration fields,
properties, and actions now use `connect_activedirectory_`; the policy template
group is exactly `connect_activedirectory`. Import this as a new app and create
its connection settings. Existing **Native AD** settings and policy references
are not automatically migrated. The `nativead-guid-v1` result format remains
compatible with existing collectors.

Version **0.1.4** changes **Port override** to a text field with default `"0"`.
Forescout's native integer control supports only 1–2,147,483,647, so the previous
integer default of `0` violated its documented range. This change did **not**
resolve the immediate `Failed to add a configuration: null` error on Forescout
8.5.5 with Connect Plugin 2.0.6; it persisted in 0.1.5. Python still validates
ports as 0–65535; automatic port selection is preserved.

Version **0.1.3** corrected the policy template group name to exactly
`connect_nativead`. Packaging now enforces that exact name instead of accepting
an arbitrary suffix. Python validation passed on the appliance with **0.1.2**;
**0.1.3** reached the System Description screen.

Version **0.1.2** removed the explicit `super().__init__` call rejected by Connect's
Python import validator. LDAP errors retain their messages and result codes, and
packaging now rejects explicit `__init__` calls/attribute access.

Version **0.1.1** corrected the dropdown metadata that caused the Console import
error `Missing mapping "display"`. Both connection security and server-discovery
options now use `display`/`value`; packaging rejects missing display labels.
