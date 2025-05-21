from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_msg91_integration/__init__.py
from frappe_msg91_integration import __version__ as version

setup(
    name="frappe_msg91_integration",
    version=version,
    description="This app provides integration with the MSG91 SMS gateway for Frappe Framework. It allows you to configure and use MSG91 for sending SMS messages and handling OTP functionality, overriding the default SMS settings.",
    author="Dhwani RIS",
    author_email="bhushan.barbuddhe@dhwaniris.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
) 