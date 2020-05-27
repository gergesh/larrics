import setuptools

with open('README', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='larrics',
    version='1.0',
    author='Yoav Shai',
    author_email='gergesh@gmail.com',
    description='a pirate lyrics fetcher',
    long_description=long_description,
    long_description_content_type='text/plain',
    url='https://github.com/gergesh/larrics',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['pytaglib', 'requests'],
    entry_points={'console_scripts': ['larrics=larrics.__main__:main'],},
)
