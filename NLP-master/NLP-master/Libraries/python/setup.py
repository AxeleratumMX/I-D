import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='vili-ia',
    version='0.0.1',
    author='Uriel Corona',
    author_email='uriel@axeleratum.com',
    description='Vili\'s microservices auto-authorization',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/axeleratum/NLP/Libraries/",
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ],
)