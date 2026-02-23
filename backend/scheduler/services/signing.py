import hashlib
import hmac
import time


def sign(payload_bytes: bytes, secret: str) -> dict:
    """
    Return headers for HMAC-SHA256 webhook signing.

    Header format follows the de-facto standard used by GitHub, Stripe, etc.:
      X-Cratos-Timestamp: <unix timestamp>
      X-Cratos-Signature: sha256=<hex digest of timestamp.payload>

    Including the timestamp in the signed message lets receivers reject
    replayed requests by checking that the timestamp is recent (e.g. < 5 min).
    """
    timestamp = str(int(time.time()))
    signed_content = f"{timestamp}.".encode() + payload_bytes
    digest = hmac.new(secret.encode(), signed_content, hashlib.sha256).hexdigest()
    return {
        "X-Cratos-Timestamp": timestamp,
        "X-Cratos-Signature": f"sha256={digest}",
    }
