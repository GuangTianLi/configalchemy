"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = []

setup_requirements = []

test_requirements = ["requests"]


setup(
    author="GuangTian Li",
    author_email="guangtian_li@qq.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="The Settings and Configuration on ideal practices for app development.",
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="configalchemy",
    name="configalchemy",
    packages=find_packages(include=["configalchemy*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/GuangTianLi/configalchemy",
    python_requires=">=3.6.0",
    version="0.2.5",
    zip_safe=False,
    extras_require={"apollo": ["requests"]},
)
