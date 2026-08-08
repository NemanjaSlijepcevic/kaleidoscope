Bootstrap 5.3.3 — vendored, not fetched from a CDN.

Downloaded from the exact URLs django-bootstrap5 24.3 would have used:
  https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css
  https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js

Verified against the sha384 integrity hashes that package declares:
  css sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH
  js  sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz

The only edit is the trailing sourceMappingURL comment, removed from each.
Django's manifest static storage resolves that reference during
collectstatic, so leaving it in would fail the build unless the .map files
were shipped too — ~600 KB of no use in production.

The bundle is used (not bootstrap.min.js) because it includes Popper, which
the navbar dropdown needs.

Upgrading: bump django-bootstrap5, check the URLs and hashes it declares in
core.py, and re-vendor from those. Keep the two in step — the templates rely
on 5.3 for data-bs-theme and the --bs-* variables.
