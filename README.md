# secretfile_encoder.py

Small Python script that encrypts and decrypts a message with a one-time-pad style XOR using a key file.

## How to use

Make sure the key file exists at `example/key.txt`.

### Encrypt a message

```bash
python3 secretfile_encoder.py "hello" -o ciphertext.txt
```

### Decrypt a ciphertext file

```bash
python3 secretfile_encoder.py -d ciphertext.txt
```

The decrypt command reads the starting key line from the ciphertext file header.

## What it does

- Reads bytes from the default key file at `example/key.txt`.
- XORs the key with the message.
- Prints the encrypted message as hex.
- Optionally saves the ciphertext to a file with a header that includes the start line.
- Decrypts a ciphertext file using the start line stored in its header.

## Notes

- The key file must be at least as long as the message.
- The default key file is `example/key.txt`.
- Use `-o` if you want the ciphertext written to disk.
- Use `-d` to decrypt a previously created ciphertext file.
- The ciphertext file stores `start-line` in its header so the script can decrypt it later.
- If the default key file is missing, you will get a `FileNotFoundError`.