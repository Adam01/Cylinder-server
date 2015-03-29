from distutils.core import setup
import sys

install_requires = [
    "Twisted >= 14.0.2",
    "cffi >= 0.8.6",
    "characteristic >= 14.2.0",
    "cryptography >= 0.6.1",
    "cyclone >= 1.1",
    "pyOpenSSL >= 0.14",
    "pyasn1 >= 0.1.7",
    "pyasn1-modules >= 0.0.5",
    "pycparser >= 2.10",
    "service-identity >= 14.0.0",
    "six >= 1.8.0",
    "vboxapi >= 1.0",
    "zope.interface >= 4.1.1"
]

if "win" in sys.platform:
    install_requires.append("pywin >= 219")
elif "linux" in sys.platform:
    install_requires.append("python-pam >= 1.8.2")

setup(
    name='Cylinder-server',
    version='0.0.1',
    packages=[''],
    url='https://github.com/Adam01/Cylinder-server',
    license='MIT',
    author='Adam',
    author_email='adamguy93@gmail.com',
    description='',
    install_requires=install_requires
)
