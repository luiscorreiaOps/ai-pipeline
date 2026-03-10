from setuptools import setup, find_packages
import os

setup(
    name="ai-pipeline-tool",
    version="0.1.6",
    packages=find_packages(),
    install_requires=[
        "typer",
        "pydantic",
        "pyyaml",
        "rich",
        "requests",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "ai-pipeline-tool=ai_pipeline.cli:app",
        ],
    },
    author="Correia",
    author_email="correia.ops@gmail.com",
    description="AI-powered CLI tool to automatically generate CI/CD pipelines.",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
