from setuptools import setup, find_packages

with open('README.md') as f:
   long_description = f.read()

setup(
    name  = 'oanda-backtest',
    version = '0.1.0',
    description = 'oanda-backtest is a python library for backtest with oanda rest api on Python 3.5 and above.',
    long_description = long_description,
    long_description_content_type="text/markdown",
    license = 'MIT',
    author = '10mohi6',
    author_email = '10.mohi.6.y@gmail.com',
    url='https://github.com/10mohi6/oanda-backtest-python',
    keywords = 'oanda backtest api python',
    packages = find_packages(),
    install_requires = ['requests','numpy','pandas','matplotlib'],
    python_requires=">=3.5.0",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License'
    ]
)