from hamcrest import *  # IMPORT_STAR


def test_import(tracer):
    tracer.init()

    import os  # IMPORT_NAME
    from os import path  # IMPORT_FROM, loads module
    from sys import settrace  # IMPORT_FROM, loads function

    tracer.register()

    print(os, path)  # To disable PyCharm auto removing unused imports.

    assert_that(
        tracer.logger.changes,
        contains_exactly(
            has_properties(
                {"target": "os", "value": starts_with("<module 'os'"), "sources": set()}
            ),
            has_properties(
                {
                    "target": "path",
                    "value": all_of(starts_with("<module"), contains_string("path")),
                    "sources": set(),
                }
            ),
            has_properties({"target": "settrace", "value": settrace, "sources": set()}),
        ),
    )
