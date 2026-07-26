# secretfile_encoder.py

Small Python script that encrypts and decrypts fixed-size, 100-byte messages with a one-time-pad style XOR key file.

## How to use

Make sure the key file exists at `example/key.txt`. Each usable line must contain exactly 100 bytes. Line 1 is reserved for a header.

### Encrypt a message

```bash
python3 secretfile_encoder.py "hello" -o ciphertext.txt
```

### Decrypt a ciphertext file

```bash
python3 secretfile_encoder.py -d ciphertext.txt
```

The script automatically tracks the next unused key line in `example/next_line.txt`. The decrypt command reads the required key line from the ciphertext file header.

## What it does

- Pads each message to a fixed 100-byte block.
- Stores the real UTF-8 message length inside the encrypted block.
- Uses one complete 100-byte key line per message.
- Advances `example/next_line.txt` so that key lines are not reused.
- Saves the ciphertext with the key line number in its header.
- Decrypts using the key line stored in the ciphertext header.

## Notes

- The default key file is `example/key.txt`.
- Messages may contain at most 98 UTF-8 bytes; emoji and some other characters use multiple bytes.
- `-o` is required when encrypting so the ciphertext and its key-line header are saved together.
- Use `-d` to decrypt a previously created ciphertext file.
- Never decrease or delete `example/next_line.txt` after using a real key, because that could reuse key material.
- Do not run two encryption commands simultaneously.
- The included example key is predictable and is only for testing. A real key must contain cryptographically secure random bytes, remain private, and never be committed to Git.
- Plain XOR does not detect ciphertext tampering.