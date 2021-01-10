from setuptools import setup


setup(
    name="instantiate",
    version="0.1.3",
    py_modules=["instantiate"],
    install_requires=["jinja2", "pyyaml"],
    entry_points={"console_scripts": ["instantiate = instantiate:cli"]},
)
