from setuptools import setup, find_packages
setup(
    name = "vizard",
    version = "0.1",
    packages = find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['basemap>=1.0.7',
                        'Bottleneck>=0.7.0',
                        'Cartopy>=0.9.0',
                        'matplotlib>=1.3.1',
                        'netCDF4>=1.0.7',
                        'networkx>=1.8.1',
                        'numexpr>=2.2.2',
                        'numpy>=1.8.0',
                        'pandas>=0.13.0',
                        'Pillow>=2.3.0',
                        'pip>=1.5',
                        'pycairo>=1.10.0',
                        'pyparsing>=2.0.1',
                        'PyQt>=4.9.6',
                        'PySide>=1.2.1',
                        'dateutil>=2.2',
                        'pytz>=0',
                        'rpy2>=2.3.8',
                        'scipy>=0.13.2',
                        'setuptools>=2.0.2',
                        'six>=1.5.2',
                        'statsmodels>=0.5.0',
                        'tables>=3.0.0',
                        'tornado>=3.1.1',
                        'wxPython>=2.8.12.1',
                        'wxPython>=common-2.8.12.1'],

    # metadata for upload to PyPI
    author = "Evin Ozer",
    author_email = "evin.ozer@gmail.com",
    description = "Vizard",
    license = "MIT",
    keywords = "matplotlib basemap networkx plot plots",
    url = "https://github.com/Aphotus/vizard",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)