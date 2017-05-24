from setuptools import setup, find_packages
setup(
    name='brunch',
    version="0.1",
    packages=find_packages(),
    
    entry_points = {
        'console_scripts': [
            'brunch = brunch.main:main'
        ]
    },
    
    # metadata for upload to PyPI
    author="Arie Gurfinkel",
    author_email="arie.gurfinkel@uwaterloo.ca",
    description="Brunch: benchmakr runner",
    license="MIT",
    keywords="benchmarking",
    url="https://ece.uwaterloo.ca/~agurfink",   # project home page, if any
)
