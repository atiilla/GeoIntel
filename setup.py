from setuptools import setup, find_packages

setup(
    name='geointel',
    version='0.1.10',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
    'console_scripts': [
        'geointel=geointel.cli:main',
    ],
},
    author='Atiilla',
    description='AI powered geo-location to uncover the location of photos.',
    url='https://github.com/atiilla/geointel',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
