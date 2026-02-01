"""
Setup configuration for JSpect.
"""

from setuptools import setup, find_packages
import os

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='jspect',
    version='1.0.0',
    author='JSpect Contributors',
    author_email='',
    description='AI-Powered JavaScript Secret Scanner',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Chennadimohamedamine/JSpect',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'jspect=jspect.cli:cli',
        ],
    },
    include_package_data=True,
    package_data={
        'jspect': ['*.yaml'],
    },
)
