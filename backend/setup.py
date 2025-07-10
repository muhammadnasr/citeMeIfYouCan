from setuptools import setup, find_packages

setup(
    name="cite_me_if_you_can",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.23.2",
        "pinecone>=3.0.0",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
        "sentence-transformers>=2.2.2",
        "pytest>=7.3.1",
        "httpx>=0.24.1",
        "openai>=1.0.0"
    ],
)
