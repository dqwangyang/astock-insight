from setuptools import setup, find_packages

setup(
    name="astock-insight",
    version="0.1.0",
    description="A股市场全景分析工具 — 一键获取大盘指数、行业板块、龙虎榜、个股行情",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="astock-insight",
    url="https://github.com/astock-insight/astock-insight",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "astock-insight=astock_insight.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)
