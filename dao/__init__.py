"""Layer 2 — Data Access Objects.

One function per API call. Each function takes a :class:`RestClient`, issues a
single request, checks the status code, and raises :class:`ApiError` on failure
(so callers never inspect raw status codes). Functions are stateless — the
client carries all the state — so they are plain module-level functions, not
classes.
"""
