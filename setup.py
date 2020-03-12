import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ff4ssemble",
    version="0.0.1",
    author="trustkim",
    author_email="trustkim90@gmail.com",
    description="마퓨파 도움주는 파이썬 프로그램",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trustkim/ff4ssemble",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
