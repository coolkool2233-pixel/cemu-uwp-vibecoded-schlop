"""Check the app identity and both signing paths in a patched source tree."""
from pathlib import Path
import re
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET

MANIFEST = "src/gui/host/uwp/Package.appxmanifest"
NS = {
    "f": "http://schemas.microsoft.com/appx/manifest/foundation/windows10",
    "uap": "http://schemas.microsoft.com/appx/manifest/uap/windows10",
    "mp": "http://schemas.microsoft.com/appx/2014/phone/manifest",
}


def validate(tree: Path, original_manifest: bytes):
    original = ET.fromstring(original_manifest)
    manifest = ET.parse(tree / MANIFEST).getroot()
    identity = manifest.find("f:Identity", NS)
    old_identity = original.find("f:Identity", NS)
    assert identity.get("Name") == "Coolkool2233Pixel.CemuBOTWPrecache"
    assert re.fullmatch(r"[A-Za-z0-9.-]{3,50}", identity.get("Name"))
    assert identity.get("Name") != old_identity.get("Name")
    assert identity.get("Publisher") != old_identity.get("Publisher")
    assert identity.get("Version") == old_identity.get("Version")
    assert manifest.find("f:Properties/f:DisplayName", NS).text == "Cemu BOTW Precache"
    assert manifest.find("f:Properties/f:PublisherDisplayName", NS).text == "coolkool2233-pixel"
    app = manifest.find("f:Applications/f:Application", NS)
    old_app = original.find("f:Applications/f:Application", NS)
    assert app.get("Id") == "BotwPrecache" and app.get("Id") != old_app.get("Id")
    # Runtime entry point and executable token are ABI requirements, not branding.
    assert app.get("EntryPoint") == old_app.get("EntryPoint")
    assert app.get("Executable") == old_app.get("Executable")
    assert app.find("uap:VisualElements", NS).get("DisplayName") == "Cemu BOTW Precache"
    protocol = app.find("f:Extensions/uap:Extension/uap:Protocol", NS)
    assert protocol.get("Name") == "cemu-botw-precache"
    assert not manifest.findall(".//uap:Protocol[@Name='cemu']", NS)
    phone = manifest.find("mp:PhoneIdentity", NS)
    assert uuid.UUID(phone.get("PhoneProductId"))
    assert phone.get("PhoneProductId") != original.find("mp:PhoneIdentity", NS).get("PhoneProductId")
    # Identity changes must retain deployment dependencies and runtime capabilities.
    for section in ("Dependencies", "Capabilities"):
        assert ET.tostring(manifest.find("f:" + section, NS)) == ET.tostring(original.find("f:" + section, NS))

    local = (tree / "tools/build-uwp-local.ps1").read_text()
    ci = (tree / ".github/workflows/uwp_fork_ci.yml").read_text()
    subject = re.search(r'-subj "(/CN=[^"]+)"', local).group(1)
    ci_subject = re.search(r'-Subject "([^"]+)"', ci).group(1)
    assert subject[1:] == ci_subject == identity.get("Publisher")
    assert "CemuUWP_local.pfx" not in local
    assert "CemuBOTWPrecache_local.pfx" in local
    assert "CemuUWP_TemporaryKey.pfx" not in ci
    assert ci.count("CemuBOTWPrecache_TemporaryKey.pfx") == 2
    assert "CemuBOTWPrecache.cer" in ci
    assert "build-botw-precache-local" in local and "build-uwp-local" not in local
    assert '$origBytes = [System.IO.File]::ReadAllBytes($manifest)' in local
    assert 'finally { [System.IO.File]::WriteAllBytes($manifest, $origBytes) }' in local
    assert "git -C $repo checkout" not in local
    # Use the real version expression to check that stamping preserves the identity.
    stamp_pattern = re.search(r"\$orig -replace '([^']+)'", local).group(1)
    stamped = re.sub(stamp_pattern, 'Version="0.1.901.0"', (tree / MANIFEST).read_text())
    stamped_identity = ET.fromstring(stamped).find("f:Identity", NS)
    assert stamped_identity.get("Version") == "0.1.901.0"
    assert stamped_identity.get("Name") == identity.get("Name")
    assert stamped_identity.get("Publisher") == identity.get("Publisher")
    assert "cemu-uwp-x64.zip" not in ci
    assert "name: cemu-botw-precache-uwp-x64" in ci
    assert "HostTools::StartUpdateCheck();" not in (tree / "src/gui/host/HostApp.cpp").read_text()
    assert "Cemu UWP by PrismFox67" in (tree / "src/gui/host/HostUI.cpp").read_text()

    # Verify that OpenSSL accepts the configured publisher DN and puts it in a real certificate.
    with tempfile.TemporaryDirectory(prefix="botw-signing-") as directory:
        key = Path(directory) / "test-key.pem"
        cert = Path(directory) / "test-cert.pem"
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
                        "-subj", subject, "-keyout", str(key), "-out", str(cert),
                        "-addext", "extendedKeyUsage=codeSigning", "-addext", "basicConstraints=CA:FALSE"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = subprocess.run(["openssl", "x509", "-in", str(cert), "-noout", "-subject", "-nameopt", "RFC2253"],
                                check=True, stdout=subprocess.PIPE).stdout.decode().strip()
        assert result == "subject=" + identity.get("Publisher")
    print("PASS: independent package/app/protocol IDs; matching local/CI certificate subjects; version stamping; manifest restore guard; real OpenSSL certificate")
