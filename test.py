# def application(env, start_response):
#     start_response('200 OK', [('Content-Type','text/html')])
#     return [b"Hello World"] # python3
#     #return ["Hello World"] # python2


import time
import hashlib
from django.contrib.auth.hashers import make_password, check_password
start = time.time()

lorem = '''Lorem ipsum dolor sit amet, consectetur adipisicing
elit, sed do eiusmod tempor incididunt ut labore et dolore magna
aliqua. Ut enim ad minim veniam, quis nostrud exercitation
ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis
aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur. Excepteur sint occaecat
cupidatat non proident, sunt in culpa qui officia deserunt
mollit anim id est laborum.'''

psw = make_password(lorem)
print(psw)

for i in range(1000000):
    check_password(lorem,psw)

end = time.time()

print ('Time Consumed : %f s' % (end-start))

from django.contrib.auth.hashers import PBKDF2PasswordHasher
print(PBKDF2PasswordHasher.iterations)