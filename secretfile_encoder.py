import argparse
import secrets
from pathlib import Path

DEFAULT_KEY_PATH = Path(__file__).resolve().parent / "example" / "key.txt"
DEFAULT_STATE_PATH = Path(__file__).resolve().parent / "example" / "next_line.txt"
FIRST_KEY_LINE = 2
BLOCK_SIZE = 100
LENGTH_SIZE = 2
MAX_MESSAGE_SIZE = BLOCK_SIZE - LENGTH_SIZE

def process_otp(input_data: bytes, key_bytes: bytes) -> bytes:
    """XORs input data with the key bytes (One-Time Pad cipher)."""
    if len(key_bytes) < len(input_data):
        raise ValueError("Key is shorter than the input data. A true OTP requires a key at least as long as the message.")

    result = bytearray()
    for input_byte, key_byte in zip(input_data, key_bytes):
        # XOR each input byte with the matching key byte.
        result.append(input_byte ^ key_byte)

    return bytes(result)

def read_key_line(key_file_path: str, line_number: int) -> bytes:
    """Reads one 100-byte key line, excluding its newline."""
    if line_number < 1:
        raise ValueError("Key line number must be 1 or greater.")

    with open(key_file_path, "rb") as f:
        key_lines = f.readlines()

    if line_number > len(key_lines):
        raise ValueError(f"Key file has no line {line_number}.")

    key_bytes = key_lines[line_number - 1].rstrip(b"\r\n")
    if len(key_bytes) != BLOCK_SIZE:
        raise ValueError(
            f"Key line {line_number} must contain exactly {BLOCK_SIZE} bytes; "
            f"found {len(key_bytes)}."
        )

    return key_bytes

def reserve_next_key_line(key_file_path: str, state_file_path: str) -> tuple[int, bytes]:
    """Returns the next unused key line and advances the state file."""
    state_path = Path(state_file_path)
    if state_path.exists():
        line_number = int(state_path.read_text(encoding="utf-8").strip())
    else:
        line_number = FIRST_KEY_LINE

    key_bytes = read_key_line(key_file_path, line_number)

    # Advance before encryption so a failed write burns the line instead of
    # risking accidental key reuse on the next attempt.
    state_path.write_text(f"{line_number + 1}\n", encoding="utf-8")
    return line_number, key_bytes

def pad_message(message: str) -> bytes:
    """Creates a 100-byte block containing length, message, and random padding."""
    message_bytes = message.encode("utf-8")
    if len(message_bytes) > MAX_MESSAGE_SIZE:
        raise ValueError(
            f"Message must be at most {MAX_MESSAGE_SIZE} UTF-8 bytes; "
            f"found {len(message_bytes)}."
        )

    length_bytes = len(message_bytes).to_bytes(LENGTH_SIZE, byteorder="big")
    padding_size = BLOCK_SIZE - LENGTH_SIZE - len(message_bytes)
    return length_bytes + message_bytes + secrets.token_bytes(padding_size)

def encrypt_message(message: str, key_bytes: bytes) -> str:
    """Pads and encrypts a message using one 100-byte key line."""
    message_block = pad_message(message)
    ciphertext_bytes = process_otp(message_block, key_bytes)
    return ciphertext_bytes.hex()

def decrypt_message(ciphertext_hex: str, key_bytes: bytes) -> str:
    """Decrypts a padded 100-byte ciphertext block."""
    ciphertext_bytes = bytes.fromhex(ciphertext_hex)
    if len(ciphertext_bytes) != BLOCK_SIZE:
        raise ValueError(f"Ciphertext must decode to exactly {BLOCK_SIZE} bytes.")

    message_bytes = process_otp(ciphertext_bytes, key_bytes)
    message_length = int.from_bytes(message_bytes[:LENGTH_SIZE], byteorder="big")
    if message_length > MAX_MESSAGE_SIZE:
        raise ValueError("Ciphertext contains an invalid message length.")

    message_start = LENGTH_SIZE
    message_end = message_start + message_length
    return message_bytes[message_start:message_end].decode("utf-8")

def write_ciphertext_file(ciphertext_file_path: str, key_line: int, ciphertext_hex: str) -> None:
    """Writes a small header and the ciphertext to a file."""
    Path(ciphertext_file_path).write_text(
        f"key-line: {key_line}\n"
        f"ciphertext: {ciphertext_hex}\n",
        encoding="utf-8",
    )

def read_ciphertext_file(ciphertext_file_path: str) -> tuple[int, str]:
    """Reads the key line and ciphertext hex from a ciphertext file."""
    key_line = None
    ciphertext_hex = None

    for raw_line in Path(ciphertext_file_path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.lower().startswith("key-line:"):
            key_line = int(line.split(":", 1)[1].strip())
        elif line.lower().startswith("ciphertext:"):
            ciphertext_hex = line.split(":", 1)[1].strip()

    if key_line is None:
        raise ValueError("Ciphertext file is missing a key-line header.")
    if ciphertext_hex is None:
        raise ValueError("Ciphertext file is missing ciphertext hex.")

    return key_line, ciphertext_hex

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt and decrypt a message with a key file.")
    parser.add_argument("message", nargs="?", help="Plaintext message to encrypt")
    parser.add_argument("-o", "--ciphertext-file", help="Optional file path to write the ciphertext hex to")
    parser.add_argument("-d", "--decrypt-file", help="Path to a ciphertext file to decrypt")
    args = parser.parse_args()

    if (args.message is None) == (args.decrypt_file is None):
        parser.error("provide either a message to encrypt or --decrypt-file, but not both")
    if args.decrypt_file and args.ciphertext_file:
        parser.error("--ciphertext-file can only be used when encrypting a message")
    if args.message is not None and not args.ciphertext_file:
        parser.error("-o/--ciphertext-file is required when encrypting a message")

    try:
        if args.decrypt_file:
            key_line, ciphertext_hex = read_ciphertext_file(args.decrypt_file)
            key_bytes = read_key_line(str(DEFAULT_KEY_PATH), key_line)
            decrypted_text = decrypt_message(ciphertext_hex, key_bytes)
            print(f"Decrypted: {decrypted_text}")
        else:
            # Validate the message before consuming a key line.
            pad_message(args.message)
            key_line, key_bytes = reserve_next_key_line(
                str(DEFAULT_KEY_PATH),
                str(DEFAULT_STATE_PATH),
            )
            encrypted_hex = encrypt_message(args.message, key_bytes)
            print(f"Ciphertext: {encrypted_hex}")

            if args.ciphertext_file:
                write_ciphertext_file(args.ciphertext_file, key_line, encrypted_hex)
                print(f"Ciphertext saved to: {args.ciphertext_file}")
    except FileNotFoundError:
        print(
            "Please make sure the key and state files exist at: "
            f"{DEFAULT_KEY_PATH} and {DEFAULT_STATE_PATH}"
        )
    except (UnicodeDecodeError, ValueError) as error:
        print(f"Error: {error}")