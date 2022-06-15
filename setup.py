from setuptools import setup, find_packages

setup(
    name='thePerfectlyJustSociety',
    version='1.0.2',
    license='MIT',
    author='Ryan Lague',
    author_email='ryanlague@hotmail.com',
    packages=find_packages(),
    package_data={},
    url='https://github.com/ryanlague/thePerfectlyJustSociety',
    install_requires=[
        'dash',
        'diskcache',
        'numpy',
        'pandas',
        'tqdm',
        'matplotlib',
        'fire',
        'dash[diskcache]',
        'fire'
    ]
)
