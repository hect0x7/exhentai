from setuptools import setup, find_packages

with open("README.md", encoding='utf-8') as f:
    long_description = f.read()

version = None
with open('src/exhentai/__init__.py', encoding='utf-8') as f:
    for line in f:
        if '__version__' in line:
            version = line[line.index("'") + 1: line.rindex("'")]
            break

if version is None:
    print('Set version first!')
    exit(1)

setup(
    name='exhentai',
    version=version,
    description='Python Wrapper For exhentai API',
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/hect0x7/exhentai',
    author='hect0x7',
    author_email='93357912+hect0x7@users.noreply.github.com',
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        'commonX',
        'Pillow',
        'beautifulsoup4',
        'lxml',
    ],
    keywords=['python', 'exhentai', 'NSFW'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
    }
)
