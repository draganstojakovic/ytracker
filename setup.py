from setuptools import setup, find_packages


setup(
    name='ytracker',
    version='2023.10.06',
    description='YouTube feed downloader',
    author='Dragan Stojaković',
    url='https://github.com/draganstojakovic/ytracker',
    packages=find_packages(),
    install_requires=[
        'mutagen',
        'pycryptodomex',
        'websockets',
        'yt-dlp'
    ],
    entry_points={
        'console_scripts': [
            'ytracker = ytracker.__main__:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Environment :: No Input/Output (Daemon)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)