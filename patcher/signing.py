import struct

APK_SIG_BLOCK_MAGIC = b"APK Sig Block 42"
# APK Signature Scheme v2 and v3 block IDs.
SIGNATURE_SCHEME_IDS = (0x7109871A, 0xF05368C0)


def _read_length_prefixed(data: bytes, offset: int):
    (length,) = struct.unpack("<I", data[offset:offset + 4])
    offset += 4
    return data[offset:offset + length], offset + length


def get_signing_certificate(apk_path: str) -> bytes:
    """
    Return the DER-encoded signing certificate from the APK Signing Block.

    Recent Moovit releases are only signed with the v2/v3 schemes, so there is
    no META-INF/*.RSA to read the certificate from.
    See https://source.android.com/docs/security/features/apksigning/v2
    """
    with open(apk_path, "rb") as f:
        data = f.read()
    eocd = data.rfind(b"PK\x05\x06")
    (cd_offset,) = struct.unpack("<I", data[eocd + 16:eocd + 20])
    if data[cd_offset - 16:cd_offset] != APK_SIG_BLOCK_MAGIC:
        raise ValueError(f"APK Signing Block not found in {apk_path}")
    (block_size,) = struct.unpack("<Q", data[cd_offset - 24:cd_offset - 16])
    offset = cd_offset - block_size
    blocks = {}
    while offset < cd_offset - 24:
        (pair_length,) = struct.unpack("<Q", data[offset:offset + 8])
        (block_id,) = struct.unpack("<I", data[offset + 8:offset + 12])
        blocks[block_id] = data[offset + 12:offset + 8 + pair_length]
        offset += 8 + pair_length

    for block_id in SIGNATURE_SCHEME_IDS:
        if block_id not in blocks:
            continue
        # signers -> first signer -> signed data -> (digests, certificates)
        signers, _ = _read_length_prefixed(blocks[block_id], 0)
        signer, _ = _read_length_prefixed(signers, 0)
        signed_data, _ = _read_length_prefixed(signer, 0)
        _, offset = _read_length_prefixed(signed_data, 0)
        certificates, _ = _read_length_prefixed(signed_data, offset)
        certificate, _ = _read_length_prefixed(certificates, 0)
        return certificate
    raise ValueError(f"No v2/v3 signature found in {apk_path}")
