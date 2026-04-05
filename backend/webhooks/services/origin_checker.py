# webhooks/services/origin_checker.py
"""
Origin-based URL allowlist enforcement.

A callback URL is permitted only if its normalized origin (scheme + host + port)
matches a row in the AllowedOrigin table. All other URLs are rejected.

Default port resolution (only when the URL omits a port):
  http  -> 80
  https -> 443

Notes:
- Keep redirects disabled in your HTTP client, OR re-check each redirect target
  before following it, otherwise an allowlisted origin could redirect elsewhere.
"""

from urllib3.util.url import parse_url

from webhooks.models import AllowedOrigin
from webhooks.services.errors import URLPolicyError

_DEFAULT_PORTS = {"http": 80, "https": 443}


class OriginChecker:
    def check_url(self, url: str) -> None:
        scheme, host, port = self._extract_origin(url)
        if not AllowedOrigin.objects.filter(scheme=scheme, host=host, port=port).exists():
            raise URLPolicyError(
                f"Origin {scheme}://{host}:{port} is not allowed. "
                "Add it to AllowedOrigin to permit it."
            )

    def _extract_origin(self, url: str) -> tuple[str, str, int]:
        p = parse_url(url)

        # parse_url() may accept weird inputs; enforce what we need.
        if p.scheme not in _DEFAULT_PORTS or not p.host:
            raise URLPolicyError("Must be a valid HTTP/HTTPS URL.")

        scheme = p.scheme
        host = p.host.strip().lower().rstrip(".")
        port = int(p.port) if p.port is not None else _DEFAULT_PORTS[scheme]
        return scheme, host, port