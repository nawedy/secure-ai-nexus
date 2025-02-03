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

setup(
    name="secureai-restore-cli",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.0.0',
        'rich>=10.0.0',
        'asyncio>=3.4.3',
        'prometheus-client>=0.12.0',
    ],
    entry_points={
        'console_scripts': [
            'restore-cli=src.cli.restore_cli:main',
        ],
    },
)
