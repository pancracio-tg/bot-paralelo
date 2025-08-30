import hashlib


def calcular_hash(ruta_archivo):
    """
    Calcula el hash SHA-256 de un archivo dado.

    Args:
        ruta_archivo (str): Ruta del archivo a procesar.

    Returns:
        str: Hash SHA-256 del archivo en formato hexadecimal.
    """
    sha256 = hashlib.sha256()
    with open(ruta_archivo, "rb") as f:
        for bloque in iter(lambda: f.read(4096), b""):
            sha256.update(bloque)
    return sha256.hexdigest()
