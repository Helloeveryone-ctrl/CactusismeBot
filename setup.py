from setuptools import setup, find_packages

setup(
    name="CactusismeBot",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "mwparserfromhell",
        "pywikibot",
        "requests",
        "urllib3",
    ],
    python_requires=">=3.7",
)
