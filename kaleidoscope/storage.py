from whitenoise.storage import CompressedManifestStaticFilesStorage


class JsModuleManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """Static files storage that also hashes ES module import specifiers.

    Django hashes each file's name for cache busting, but by default it only
    rewrites references inside CSS. An `import ... from "./pagination.js"` in a
    JS module is left untouched, so gallery.js gets a fresh hashed URL on every
    deploy while the pagination.js it imports keeps a stable, cacheable one.

    A browser could then run a new gallery.js against a cached older
    pagination.js — which breaks the moment the two files' interface changes,
    with an error pointing at a line number that doesn't match the deployed
    source. Turning this on rewrites the import to the hashed filename, so the
    module and its dependencies are always busted together.
    """

    support_js_module_import_aggregation = True
