from distutils.core import setup
setup(
    name = "googlecalendar",
    packages = ["googlecalendar", ],
    install_requires=[
        "gdata",
    ],
    version = "0.1",
    description = "This project implements Google Calendar API as django objects.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
)
