from setuptools import setup, find_packages

setup(
    name='thePerfectlyJustSociety',
    version='1.0.0',
    description='An experiment in equality and equity',
    author='Ryan Lague',
    author_email='ryanlague@hotmail.com',
    packages=find_packages(),
    package_data={
    },
    install_requires=[
        'dash',
        'diskcache',
        'numpy',
        'pandas',
        'tqdm',
        'matplotlib',
        'fire',
        'dash[diskcache]'
    ]
)
