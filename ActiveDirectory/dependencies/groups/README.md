# Manual Forescout group import

[`Groups Structure.xml`](./Groups%20Structure.xml) is the supplied Forescout
group-tree export for the Connect AD policy examples. It creates this hierarchy:

```text
[Connect AD] Groups
└── [Connect AD] Policy Flow Groups
    ├── Trusted Computer Object Match
    └── Trusted User Object Match
```

The XML is stored unchanged for download and manual import. The Connect app has
no mechanism for creating or importing Forescout groups, so this file is not
included in the Connect app ZIP and importing or upgrading the app will not
install it.

Download the XML and import it separately with the supported group-import
workflow for the target Forescout deployment. Review the names, descriptions,
IDs, and destination hierarchy before importing. Import behavior has not been
validated on an appliance from this repository.

After importing the supporting groups, continue with the
[GUID collector policy installation](../endpoint-scripts/README.md). Its wizard
steps include selecting the production Forescout segment scope before editing
the main-rule device-group condition.
