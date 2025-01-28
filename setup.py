from setuptools import setup, find_packages

setup(
    name="powerschool_adapter",                             # Package name
    version="1.0.0",                        # Version
    author="TONYLABS TECH CO., LTD.",       # Author name
    author_email="tony.wang@tonyalbs.com",  # Author email
    description="A python adapter of PowerSchool API",
    long_description=open("README.md").read(),  # Full description
    long_description_content_type="text/markdown",  # Content type
    url="https://github.com/tonylabs/python-powerschool-adapter",  # Project URL
    packages=find_packages(),               # Automatically find sub-packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",                # Minimum Python version
    install_requires=[                      # Dependencies
        "requests>=2.20.0",
        "python-dotenv>=1.0.1",
        "faker>=35.0.0",
        "diskcache>=5.6.0"
    ],
)