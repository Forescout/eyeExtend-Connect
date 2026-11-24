# Custom Claroty xDome 1.0

This custom Forescout Connect app is based on the upstream Claroty xDome and Medigate 1.0.3 package. It is xDome-only and uses the distinct `connect_customclarotyxdome_` namespace so it can coexist with the upstream app.

## xDome Prerequisites

- An xDome API URL that supports `POST /api/v1/devices/`.
- An API token with permission to retrieve device inventory fields.
- The following scalar fields available in the xDome device response:
  - `site_group_name`
  - `site_name`
  - `device_purpose_functional_area`
  - `device_purpose_focus_factory`
  - `device_purpose_line`
  - `device_purpose_device_function`
  - `organization_zone_name`

The app requests these fields during discovery and maps them to corresponding `connect_customclarotyxdome_` Forescout properties. Missing or null values are omitted without interrupting discovery.

## Import

1. Import the .eca into the Forescout Connect plugin.
2. Configure the xDome API URL, API token, discovery settings, and any optional device filters.
3. Run the connection test, then start discovery.

TLS certificate verification is currently disabled by default. You can explicitly enable certificate validation in the connection configuration. Disabling verification leaves HTTPS connections vulnerable to server impersonation.

This app enforces the 5 MB per-file and 10 MB archive limits from the Forescout App Building Guide.

## Rollback

Stop and remove the `Custom Claroty xDome` app from Forescout Connect. This does not modify or remove the upstream Claroty xDome and Medigate app.
