from setuptools import setup, find_packages

setup(
    name='mypkgs',  # Replace with your project name
    version='0.1.0',  # Make sure this matches your pyproject.toml version
    description='Simple util to view manually installed packages on Debian',  # Your description
    author='Alexandr Negrya',  # Your name
    author_email='alexandr.negrya@gmail.com',  # Your email
    packages=find_packages(where='src'),  # Automatically find your package directories
    # Alternatively, if you have specific packages:
    # packages=['mypackage', 'mypackage.cli'],
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'mypkgs=mypkgs.core:main', # To run from command line
        ],
    },
    install_requires=[],  # List any dependencies here
    classifiers=[  # Optional: Classifiers from https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # Or your license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Operating System :: POSIX :: Linux',
    ],
    long_description=open('README.md').read(),  # Load from README.md
    long_description_content_type='text/markdown',  # If README is Markdown
)
