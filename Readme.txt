python -m venv venv

venv\Scripts\activate

https://localhost:9384/

# Generate a new 2048-bit private key
openssl genrsa -out server.key 2048

# Generate a new self-signed certificate valid for 365 days
openssl req -new -x509 -key server.key -out server.crt -days 365

# windows specidifc
openssl req -new -x509 -key server.key -out server.crt -days 365 -config "C:\Program Files\Git\usr\ssl\openssl.cnf"