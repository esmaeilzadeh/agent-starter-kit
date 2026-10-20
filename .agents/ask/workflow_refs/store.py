"""Immutable integrity catalog publication and resolution."""


class CatalogError(ValueError):
    """A catalog is invalid, stale, unavailable, or conflicts with history."""


def initialize_catalog(path, owner):
    return {}


def register_revision(catalog_path, owner, logical_id, snapshot, item_id, profile, payload,
                     expected_generation=None, after_publish=None, revision=None, **kwargs):
    return None


def resolve_version(catalog_path, reference, repository_root=None, payload=None, semantics=None):
    return {}
