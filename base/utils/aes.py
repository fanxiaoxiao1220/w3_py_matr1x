from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


"""
示例代码：

plaintext = "0123456789"
key = "0123456789abcdef" # 16 bytes
ciphertext = aes_encrypt(plaintext, key)
print(ciphertext)
decrypted_plaintext = aes_decrypt(ciphertext, key)
print(decrypted_plaintext)

"""


def aes_encrypt(plaintext, key):
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    padded_plaintext = pad(plaintext.encode(), AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    return base64.b64encode(ciphertext).decode()


def aes_decrypt(ciphertext, key):
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    decoded_ciphertext = base64.b64decode(ciphertext)
    padded_plaintext = cipher.decrypt(decoded_ciphertext)
    return unpad(padded_plaintext, AES.block_size).decode()
