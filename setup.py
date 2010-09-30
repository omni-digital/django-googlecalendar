from distutils.core import setup
setup(
    name = "google",
    packages = ["google", ],
    install_requires=[
        "gdata",
    ],
    version = "0.1",
    description = "This project currently implements Google Calendar API as django objects. More APIs are likely to appear in the future.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
)
