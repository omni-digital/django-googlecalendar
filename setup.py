from setuptools import setup, find_packages
from setuptools.dist import Distribution
import pkg_resources


add_django_dependency = True
# See issues #50, #57 and #58 for why this is necessary
try:
    pkg_resources.get_distribution('Django')
    add_django_dependency = False
except pkg_resources.DistributionNotFound:
    try:
        import django
        if django.VERSION[0] >= 1 and django.VERSION[1] >= 1 and django.VERSION[2] >= 1:
            add_django_dependency = False
    except ImportError:
        pass

Distribution({
    "setup_requires": add_django_dependency and  ['Django >=1.1.1'] or []
})

setup(
    name = "googlecalendar",
    packages = find_packages(),
    install_requires=[
        "gdata",
        "feincms",
    ],
    version = "0.1",
    description = "This project implements Google Calendar API as django objects.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
    include_package_data=True,
)
