# changedetection.io tester-env notes

## Quick start

```bash
./tester-env reset --port 5029
./tester-env deploy --port 5029
./tester-env seed --port 5029
./tester-env verify --port 5029
```

Credentials: none by default.

## Seed profile

Theme: Northwind Digital Merchandising website-change monitoring.

`./tester-env seed` removes the two upstream default watches, clears tags, then creates three deterministic tags and six deterministic watches via the changedetection.io REST API.

Stable visible seed data:

- Tags: `Retail Intelligence`, `Vendor Portals`, `Compliance`.
- Watches: `Northwind Coffee product pricing`, `Northwind Coffee checkout banner`, `Acme Wholesale availability feed`, `Harbor Freight surcharge notice`, `California privacy policy update`, `Accessibility statement monitor`.
- Paused watches: `Northwind Coffee checkout banner`, `Accessibility statement monitor`.
- Relationship: each tag has exactly two watches.

Browser-checker path: open `http://host.docker.internal:5029/` after reset/deploy/seed/verify. Assert the dashboard shows the six watch titles above, the three tag names above, and visible paused controls/icons on the two paused watches. Use the tag filters to assert each seeded tag narrows the dashboard to two related watches.
