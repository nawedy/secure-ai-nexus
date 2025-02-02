from setuptools import setup, find_packages

setup(
    name="secureai-nexus",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'prometheus-client',
        'aiohttp',
        'pydantic',
        'python-jose[cryptography]',
        'python-multipart',
        'psutil',
        'kubernetes'
    ],
    python_requires='>=3.9',
)
