from setuptools import setup, find_packages

setup(
    name = "googlecalendar",
    packages = find_packages(),
    install_requires=[
        "gdata",
    ],
    version = "0.1",
    description = "This project implements Google Calendar API as django objects.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
)
