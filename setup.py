from setuptools import setup, find_packages

setup(
    name="utapis-sintaksis-flask-server",
    version="1.3.0",
    install_requires=[
        "flask",
        "anyascii",
        "nltk",
        "python-crfsuite",
        "pytz",
        "beautifulsoup4",
        "sastrawi",
        "pandas",
        "openpyxl",
    ],
    include_package_data=True,
    packages=find_packages(),
    # package_dir={"": "utapis_sintaksis_flask_server"},
)

"""NOTE:
- Use python -m build to create the module's distribution ('tar.gz' and '.whl' file in 
'dist' directory).
"""
