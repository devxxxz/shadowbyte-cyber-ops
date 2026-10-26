import socket
import ssl
from datetime import datetime, timezone

def run_dns_tls_check(hostname: str, timeout_seconds: int = 8) -> list[dict]:
    """Perform a bounded DNS lookup and TLS certificate inspection for one approved hostname."""
    findings: list[dict] = []
    socket.setdefaulttimeout(timeout_seconds)
    try:
        records = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
        addresses = sorted({item[4][0] for item in records})
        findings.append({
            "check": "dns_resolution",
            "status": "pass",
            "summary": "Hostname resolved successfully.",
            "evidence": {"addresses": addresses},
        })
    except (socket.gaierror, TimeoutError, OSError) as exc:
        findings.append({
            "check": "dns_resolution",
            "status": "warning",
            "summary": "DNS lookup failed or timed out.",
            "evidence": {"reason": type(exc).__name__},
        })
        return findings

    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=timeout_seconds) as raw:
            with context.wrap_socket(raw, server_hostname=hostname) as tls:
                cert = tls.getpeercert()
                not_after = cert.get("notAfter")
                expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc) if not_after else None
                days_left = (expiry - datetime.now(timezone.utc)).days if expiry else None
                findings.append({
                    "check": "tls_certificate",
                    "status": "pass" if days_left is None or days_left > 14 else "warning",
                    "summary": "TLS connection succeeded.",
                    "evidence": {
                        "tls_version": tls.version(),
                        "expires_at": expiry.isoformat() if expiry else None,
                        "days_until_expiry": days_left,
                    },
                })
    except (ssl.SSLError, TimeoutError, OSError, ValueError) as exc:
        findings.append({
            "check": "tls_certificate",
            "status": "warning",
            "summary": "TLS connection failed or certificate validation failed.",
            "evidence": {"reason": type(exc).__name__},
        })
    return findings
