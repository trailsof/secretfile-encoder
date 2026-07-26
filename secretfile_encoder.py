import argparse
from pathlib import Path

DEFAULT_KEY_PATH = Path(__file__).resolve().parent / "example" / "key.txt"
DEFAULT_START_LINE = 2

def process_otp(input_data: bytes, key_bytes: bytes) -> bytes:
    """XORs input data with the key bytes (One-Time Pad cipher)."""
    if len(key_bytes) < len(input_data):
        raise ValueError("Key is shorter than the input data. A true OTP requires a key at least as long as the message.")
    
    return bytes(b ^ k for b, k in zip(input_data, key_bytes[:len(input_data)]))

def read_key_bytes(key_file_path: str, start_line: int = 1) -> bytes:
    """Reads key bytes from a file, starting at the requested 1-based line."""
    with open(key_file_path, "rb") as f:
        key_lines = f.readlines()

    if start_line < 1:
        raise ValueError("start_line must be 1 or greater.")

    return b"".join(key_lines[start_line - 1:])

def encrypt_message(message: str, key_file_path: str, start_line: int = 1) -> str:
    """Reads a key from a file/flash drive and encrypts a plaintext message."""
    key_bytes = read_key_bytes(key_file_path, start_line)
        
    message_bytes = message.encode("utf-8")
    ciphertext_bytes = process_otp(message_bytes, key_bytes)
    
    return ciphertext_bytes.hex()

def decrypt_message(ciphertext_hex: str, key_file_path: str, start_line: int = 1) -> str:
    """Reads a key from a file/flash drive and decrypts a hex-encoded ciphertext."""
    key_bytes = read_key_bytes(key_file_path, start_line)
        
    ciphertext_bytes = bytes.fromhex(ciphertext_hex)
    message_bytes = process_otp(ciphertext_bytes, key_bytes)
    
    return message_bytes.decode("utf-8")

def write_ciphertext_file(ciphertext_file_path: str, start_line: int, ciphertext_hex: str) -> None:
    """Writes a small header and the ciphertext to a file."""
    Path(ciphertext_file_path).write_text(
        f"start-line: {start_line}\n"
        f"ciphertext: {ciphertext_hex}\n",
        encoding="utf-8",
    )

def read_ciphertext_file(ciphertext_file_path: str) -> tuple[int, str]:
    """Reads the start line and ciphertext hex from a ciphertext file."""
    start_line = None
    ciphertext_hex = None

    for raw_line in Path(ciphertext_file_path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.lower().startswith("start-line:"):
            start_line = int(line.split(":", 1)[1].strip())
        elif line.lower().startswith("ciphertext:"):
            ciphertext_hex = line.split(":", 1)[1].strip()

    if start_line is None:
        raise ValueError("Ciphertext file is missing a start-line header.")
    if ciphertext_hex is None:
        raise ValueError("Ciphertext file is missing ciphertext hex.")

    return start_line, ciphertext_hex

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt and decrypt a message with a key file.")
    parser.add_argument("message", nargs="?", help="Plaintext message to encrypt")
    parser.add_argument("-o", "--ciphertext-file", help="Optional file path to write the ciphertext hex to")
    parser.add_argument("-d", "--decrypt-file", help="Path to a ciphertext file to decrypt")
    args = parser.parse_args()

    if bool(args.message) == bool(args.decrypt_file):
        parser.error("provide either a message to encrypt or --decrypt-file, but not both")
    if args.decrypt_file and args.ciphertext_file:
        parser.error("--ciphertext-file can only be used when encrypting a message")

    try:
        if args.decrypt_file:
            start_line, ciphertext_hex = read_ciphertext_file(args.decrypt_file)
            decrypted_text = decrypt_message(ciphertext_hex, str(DEFAULT_KEY_PATH), start_line)
            print(f"Decrypted: {decrypted_text}")
        else:
            encrypted_hex = encrypt_message(args.message, str(DEFAULT_KEY_PATH), DEFAULT_START_LINE)
            print(f"Ciphertext: {encrypted_hex}")

            if args.ciphertext_file:
                write_ciphertext_file(args.ciphertext_file, DEFAULT_START_LINE, encrypted_hex)
                print(f"Ciphertext saved to: {args.ciphertext_file}")
    except FileNotFoundError:
        print(f"Please make sure the default key file exists at: {DEFAULT_KEY_PATH}")