from cryptography.fernet import Fernet


##Encryption framework
key = Fernet.generate_key()
fernet = Fernet(key)

def encrypt(message):
    encMessage = fernet.encrypt(message.encode())
    return encMessage    

def decMessage(encrypted):
    decrypt = fernet.decrypt(encrypted).decode()
    return decrypt