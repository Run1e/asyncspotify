import setuptools

with open('README.rst', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="asyncspotify",
    version="0.12.1",
    author="RUNIE",
    author_email="runar-borge@hotmail.com",
    description="Spotify Web API implementation that is fully asynchronous and object-oriented.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    keywords='spotify async aio asyncio api webapi',
    install_requires=install_requires,
    url="https://github.com/Run1e/asyncspotify",
    project_urls={
        'Documentation': 'https://asyncspotify.rtfd.io/'
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5.2"  # first version to support async class generator iterators
)