import random 
import string 

def create(k: int=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))