"""Setup for test_module."""
from setuptools import setup

setup(
    name="tests",
    version='1.0.0',
    zip_safe=False,
    packages=['test_module'],
    entry_points={
        "invenio_search.mappings": [
            "test = test_module.mappings"
        ],
        "invenio_records.validate":[
            "tests = test_module.jsonschemas"
        ],
        'invenio_base.apps': [
            #'document = oarepo_document.DocumentRecord',
            'oarepo_actions = oarepo_actions:Actions'
        ],
    },
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
)