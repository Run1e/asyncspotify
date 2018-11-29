import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spoofy",
    version="0.1",
    author="RUNIE",
    author_email="runar-borge@hotmail.com",
    description="spoofy is an asynchronous, object-oriented python wrapper for the Spotify Web API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Run1e/spoofy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)