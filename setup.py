from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="decadetools20",
    version="0.1.0",
    author="Brant",
    author_email="",  # Add your email if you want
    description="Useful, miscellaneous django stuff for the 2020's",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Brant/decadetools20",
    packages=find_packages(),
    include_package_data=True,  # This is important for including non-Python files
    package_data={
        'decadetools20': [
            'static/decadetools20/css/*',
            'static/decadetools20/js/*',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
    ],
) 