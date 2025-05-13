from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import ipaddress

# === PARAMÈTRES ===
ca_name = "LocalDev CA"
cert_name = "fastapi.local"
ip_address = "172.17.240.18"

# === 1. Générer la clé privée de la CA ===
ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open("ca.key", "wb") as f:
    f.write(ca_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))

# === 2. Créer le certificat de la CA (auto-signé) ===
ca_subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, ca_name)])
ca_cert = (
    x509.CertificateBuilder()
    .subject_name(ca_subject)
    .issuer_name(ca_subject)
    .public_key(ca_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=3650))
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    .sign(private_key=ca_key, algorithm=hashes.SHA256())
)

with open("ca.crt", "wb") as f:
    f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

# === 3. Générer clé privée du serveur ===
server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open("server.key", "wb") as f:
    f.write(server_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))

# === 4. Créer le CSR (Certificate Signing Request) ===
server_subject = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, cert_name),
])
csr = (
    x509.CertificateSigningRequestBuilder()
    .subject_name(server_subject)
    .add_extension(
        x509.SubjectAlternativeName([
            x509.IPAddress(ipaddress.IPv4Address(ip_address)),
        ]),
        critical=False
    )
    .sign(server_key, hashes.SHA256())
)

# === 5. Signer le certificat serveur avec la CA ===
server_cert = (
    x509.CertificateBuilder()
    .subject_name(csr.subject)
    .issuer_name(ca_cert.subject)
    .public_key(csr.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=365))
    .add_extension(
        x509.SubjectAlternativeName([
            x509.IPAddress(ipaddress.IPv4Address(ip_address)),
        ]),
        critical=False
    )
    .sign(ca_key, hashes.SHA256())
)

with open("server.crt", "wb") as f:
    f.write(server_cert.public_bytes(serialization.Encoding.PEM))

print("✅ Certificat généré :")
print("- server.crt (certificat serveur signé)")
print("- server.key (clé privée)")
print("- ca.crt     (certificat de l’autorité à installer dans Chrome)")
