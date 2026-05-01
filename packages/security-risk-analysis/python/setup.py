from setuptools import setup, find_packages

setup(
    name="isrms-security-risk-analysis",
    version="1.0.0",
    description="ISRMS Security Risk Analysis Module",
    packages=find_packages(),
    install_requires=[
        "isrms-core>=1.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "openpyxl>=3.1.0",
    ],
    python_requires=">=3.10",
)