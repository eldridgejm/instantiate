from setuptools import setup


setup(
    name="instantiate",
    version="0.1.0",
    py_modules=["instantiate"],
    install_requires=["jinja2", "pyyaml"],
    entry_points={"console_scripts": ["instantiate = instantiate:cli"]},
)
