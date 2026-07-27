import getopt
import sys


def main(argv):
    print(argv)
    opts, args = getopt.getopt(argv, "edmt:l:", ["key-path="])

    one_opt_sel = False
    auto_decode = True
    encrypt_arg = True
    text_in = ''
    key_path = "key.txt"
    line_number = 1  # CHANGE TO -1 after debugging
    for opt, arg in opts:
        if opt == "-e":
            one_opt_sel = True
            encrypt_arg = True
        elif opt == "-d":
            one_opt_sel = True
            encrypt_arg = False
        elif opt == "--key-path":
            key_path = arg
        elif opt == "-t":
            text_in = arg
        elif opt == "-l":
            line_number = arg
        elif opt == "-m":
            auto_decode = False

    if not one_opt_sel:
        raise ValueError("must add -e or -d")
    if text_in == '':
        raise ValueError("use -t to specify text")
    if line_number < 0 and encrypt:
        raise ValueError("use -l to specify line number")
 
    key = read_key(key_path, line_number)

    if encrypt_arg:
       print(f"encrypting {text_in}")
       print(f"{key_path.split('/')[-1]}_{line_number}_", end='')
       print(encrypt(text_in, key))
    else:
       if auto_decode:
           [key_path, line_number, cypher_text] = text_in.split('_')
       else:
           cypher_text = text_in

       print(f"decrypting {cypher_text}")
       print(decrypt(cypher_text, key))


def read_key(filename: str, line_num: int):
    with open(filename, 'r') as fp:
        lines = fp.readlines()
        line = lines[line_num - 1]
    return line.strip()


def decrypt(cypher_text: str, key: str):
    if len(cypher_text) != len(key):
        raise ValueError("string len do not match")
    
    key_list = str_to_list(key)
    ct_list = str_to_list(cypher_text)

    pt_list = []
    for i, num in enumerate(key_list):
        pt_char = (ct_list[i] - num) % 38
        pt_list.append(pt_char)

    return list_to_str(pt_list)


def encrypt(plain_text: str, key: str):
    key_len = len(key)
    text_len = len(plain_text)
    if text_len > key_len:
        raise ValueError("unable to encrypt str too long")

    key_list = str_to_list(key)
    pt_list = str_to_list(plain_text)

    ct_list = []
    for i, num in enumerate(key_list):
        if i < text_len:
            ct_int = (num + pt_list[i]) % 38
        else:
            ct_int = (num + 10) % 38
        ct_list.append(ct_int)

    return list_to_str(ct_list)
    

def str_to_list(str_in: str):
    list_out = []
    for letter in str_in:
        int_out = char_to_int(letter)
        list_out.append(int_out)

    return list_out


def list_to_str(list_in: list):
    str_out = ''
    for num in list_in:
        letter = int_to_char(num)
        str_out += letter

    return str_out


def char_to_int(char_in: chr):
    ascii_val = ord(char_in)
    int_out = 0
    if ascii_val < 0x20:
        raise ValueError(f"unsupported char {char_in}")
    elif ascii_val == 0x20:
        int_out = 10
    elif ascii_val == 0x2e:
        int_out = 11
    elif ascii_val < 0x30:
        raise ValueError(f"unsupported char {char_in}")
    elif ascii_val < 0x3A:
        int_out = ascii_val - 0x30
    elif ascii_val < 0x61:
        raise ValueError(f"unsupported char {char_in}")
    elif ascii_val <= 0x7A:
        int_out = ascii_val - 85
    else:
        raise ValueError(f"unsupported char {char_in}")
   
    if int_out < 0 or int_out > 37:
        raise ValueError("something has gone wrong")

    return int_out


def int_to_char(int_in: int):

    if int_in < 0 or int_in > 37:
        raise ValueError(f"unsupported int {int_in}")
    elif int_in < 10:
        ascii_val = int_in + 0x30
    elif int_in == 10:
        ascii_val = 0x20
    elif int_in == 11:
        ascii_val = 0x2e
    else:
        ascii_val = int_in + 85

    return chr(ascii_val)


if __name__ == "__main__":
    main(sys.argv[1:])
