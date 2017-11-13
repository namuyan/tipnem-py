# how to build?
#
# C:\Users\user\Anaconda3\Lib\site-packages\Crypto
# copy and change to crypto_tmp
# add         => from crypto_tmp.Cipher import AES
# comment out => from Crypto.Cipher import AES
# add         => from python_sha3 import sha3_256, sha3_512
# comment out => from .python_sha3 import sha3_256, sha3_512

pyinstaller gox_tool.py --onefile --exclude-module PyQt5 --exclude-module numpy --icon=icon.ico
pause