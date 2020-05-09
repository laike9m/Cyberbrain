from hamcrest import *

from cyberbrain import Creation


def test_import(tracer):
    tracer.init()

    import os  # IMPORT_NAME
    from os import path  # IMPORT_FROM, loads module
    from sys import settrace  # IMPORT_FROM, loads function

    tracer.register()

    print(os, path)  # Prevent PyCharm from removing unused imports.

    assert_that(
        tracer.events,
        has_entries(
            {
                "os": contains_exactly(
                    all_of(
                        instance_of(Creation),
                        has_properties(
                            {
                                "target": "os",
                                "value": starts_with("<module 'os'"),
                                "sources": set(),
                            }
                        ),
                    )
                ),
                "path": contains_exactly(
                    all_of(
                        instance_of(Creation),
                        has_properties(
                            {
                                "target": "path",
                                "value": all_of(
                                    starts_with("<module"), contains_string("path")
                                ),
                                "sources": set(),
                            }
                        ),
                    )
                ),
                "settrace": contains_exactly(
                    all_of(
                        instance_of(Creation),
                        has_properties(
                            {"target": "settrace", "value": settrace, "sources": set()}
                        ),
                    )
                ),
            },
        ),
    )
