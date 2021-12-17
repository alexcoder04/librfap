from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='librfap',
    version='0.2.0',
    description='client library for rfap',
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/alexcoder04/librfap',
    license="GNU GPLv3",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    package_dir={'': 'librfap'},
    packages=find_packages(where='src'),  # Required
    python_requires='>=3.6, <4',
    install_requires=['pyyaml'],
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/alexcoder04/librfap/issues',
        'Source': 'https://github.com/alexcoder04/librfap/',
    },
)

