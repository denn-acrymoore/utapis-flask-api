from setuptools import setup, find_packages

setup(
    name="utapis_sintaksis_flask_server",
    version="1.0.0",
    install_requires=["flask", "anyascii", "nltk", "python-crfsuite", "waitress"],
    include_package_data=True,
    packages=find_packages(where="utapis_sintaksis_flask_server"),
    package_dir={"": "utapis_sintaksis_flask_server"},
)

"""NOTE:
- Use python -m build to create the module's distribution ('tar.gz' and '.whl' file in 
'dist' directory).
"""
