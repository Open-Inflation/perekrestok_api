Testing: Autotest Flow
======================

This project uses the integrated pytest addon from ``human_requests``.

Main idea:

* business endpoint methods are marked with ``@autotest``;
* pytest discovers these methods automatically;
* responses are validated with ``pytest-jsonschema-snapshot`` (fixture ``schemashot``);
* endpoint-specific test behavior is declared in registration modules under ``tests/endpoints``.


Configuration
-------------

``pyproject.toml`` already includes:

.. code-block:: ini

    [tool.pytest.ini_options]
    anyio_mode = "auto"
    autotest_start_class = "perekrestok_api.PerekrestokAPI"
    autotest_typecheck = "strict"

The plugin uses:

* ``api`` fixture (``PerekrestokAPI`` instance);
* ``schemashot`` fixture (from ``pytest-jsonschema-snapshot``).


Where test logic lives
----------------------

Business layer (``perekrestok_api/endpoints/*``):

* only ``@autotest`` markers on endpoint methods.

Test layer (``tests/endpoints/*_tests.py``):

* ``@autotest_params(target=...)`` for method arguments;
* ``@autotest_hook(target=...)`` for payload extraction/normalization/assertions;
* ``@autotest_depends_on(...)`` for data dependencies between cases.

Shared runtime state is passed via ``ctx.state``.

Because ``autotest_typecheck`` is strict, ``@autotest_params`` providers do not
need to duplicate endpoint argument typing in their return annotations. Runtime
validation is performed against endpoint method annotations.


Dependencies and ordering
-------------------------

Dependencies should be declared on params/hook callbacks.
If dependency target did not complete, dependent case is not executed.

Example:

.. code-block:: python

    @autotest_hook(target=ClassCatalog.feed)
    def _capture_product(_resp, data, ctx):
        ctx.state["product_id"] = data["content"]["items"][0]["id"]

    @autotest_depends_on(ClassCatalog.feed)
    @autotest_params(target=ProductService.similar)
    def _similar_params(ctx):
        return {"product_id": ctx.state["product_id"]}


Manual tests
------------

Manual tests should remain only for non-snapshot cases
(for example binary/image validation in ``General.download_image``).


Running tests
-------------

.. code-block:: bash

    pytest
