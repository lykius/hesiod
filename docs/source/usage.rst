############
Hesiod usage
############

Once that you have understood how to define the configs for your program (see :ref:`here <configs>`),
you need to understand just three simple mechanisms:

1. How to connect your program with Hesiod.
2. How to get configs loaded by Hesiod in your program.
3. Which utilities are provided by Hesiod.

*******************
The hmain decorator
*******************

*****************
The hcfg function
*****************

*********
Utilities
*********

Hesiod provides some utility functions, summarized in the following table.

.. list-table::
    :widths: 20 80
    :header-rows: 1

    * - Function
      - Description
    * - ``get_cfg_copy()``
      - Returns a copy of the global config as a plain dictionary.

        Values can be accessed as ``cfg_copy["key"]["subkey"]["etc."]``.
    * - ``get_out_dir()``
      - Returns the path to the output directory created by Hesiod

        for the current run.
    * - ``get_run_name()``
      - Returns the name of the current run.

See :ref:`here <api>` for additional details.
