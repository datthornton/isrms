from setuptools import setup, find_packages

setup(
    name="isrms-core",
    version="1.0.0",
    description="ISRMS Core Calculation Engine",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "openpyxl>=3.1.0",  # For Excel reading
    ],
    python_requires=">=3.10",
)