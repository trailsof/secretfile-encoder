# secretfile_encoder.py

Small Python script that encrypts and decrypts a message with a one-time-pad style XOR using a key file.

## How to use

1. Make sure you have a key file ready.
2. Run:

```bash
python3 secretfile_encoder.py "hello" --ciphertext-file ciphertext.txt
```

## What it does

- Reads bytes from the default key file at `example/key.txt`.
- XORs the key with the message.
- Prints the encrypted message as hex.
- Optionally saves the ciphertext to a file with a header that includes the start line.
- Reads the start line back from the ciphertext file when decrypting.

## Notes

- The key file must be at least as long as the message.
- The default key file is `example/key.txt`.
- Use `--ciphertext-file` if you want the ciphertext written to disk.
- The ciphertext file stores `start-line` in its header so the script can decrypt it later.
- If the default key file is missing, you will get a `FileNotFoundError`.