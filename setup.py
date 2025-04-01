from setuptools import find_packages, setup

setup(
    name='rag_cmd',
    version='0.2.1',
    description='',
    url='https://github.com/DlieBG/rag_cmd',
    author='Benedikt Schwering',
    author_email='mail@bschwer.ing',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'google-genai',
        'pymongo[srv]',
        'pydantic',
        'uvicorn',
        'fastapi',
        'click',
        'neo4j',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'rag_cmd=src.main:cli',
        ],
    },
)
