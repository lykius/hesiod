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

To use Hesiod in your program you need to wrap your main with the ``hmain`` decorator. There are two
args that you need to pass to the decorator:

1. ``base_cfg_dir``, with the path of the directory with base configs (see
   :ref:`here <base-mechanism>`).
2. Either ``run_cfg_file`` or ``template_cfg_file``, with the path to the **run** file or to the
   **template** file (see :ref:`here <run_vs_template>`).

You must pass only one between ``run_cfg_file`` and ``template_cfg_file``, since this will determine
Hesiod behavior: if you pass a run file, Hesiod will just load the config (expecting it to be completely
specified); otherwise, if you pass a template file, Hesiod will present you a TUI to specify the
values to fill your template config. Here's a code snippet to show you how to use ``hmain``:

.. code-block:: python

    # main.py

    from hesiod import hmain

    # using a run file
    @hmain(base_cfg_dir="./cfg/bases", run_cfg_file="./run.yaml")
    def main():
        # do some fancy stuff

    # using a template file
    @hmain(base_cfg_dir="./cfg/bases", template_cfg_file="./template.yaml")
    def main():
        # do some fancy stuff

    if __name__ == "__main__":
        main()

Hesiod needs a name for each run. There are two options to name a run:

1. Enter a name in the field ``run_name`` of the config (this must be done manually when using
   run files or in the TUI when using template files).
2. Leave the ``run_name`` field empty and Hesiod will name the run according to a default strategy
   (the strategy can be changed with one of ``hmain`` arguments).

In any case, when you run ``main.py``, Hesiod will load the config (either showing the TUI or not)
and will save it in a new directory created by Hesiod itself for the current run. The directory is
created inside a parent directory and is named as the run (the default parent directory is ``logs``
but can be changed with one of ``hmain`` arguments). The creation of an output directory for
each run and the saving of the config in it is enabled by default but can be disabled with one of
``hmain`` arguments.

One final thing to consider when using Hesiod is that, when you run ``main.py``, command line
arguments will be parsed to add new config values or to override existing ones. This is particularly
useful when you need to make quick tests without changing a run file every time or when you use an
automatic system to run your program with many different configs combinations (e.g. 
`Weights & Biases sweeps <https://docs.wandb.ai/sweeps>`_).

Configs passed on the command line must be in the format ``{prefix}{key}{sep}{value}``:

* ``{prefix}`` is optional and can be any amount of the char "-".
* ``{sep}`` is mandatory and can be one of "=", ":".
* ``{key}`` cannot contain the chars "-", "=" and ":".
* ``{value}`` can contain everything.

For instance, let's consider the following run file:

.. code-block:: yaml

    # run.yaml

    a: 1
    b: 2
    c: False

And the following main:

.. code-block:: python

    # main.py

    from hesiod import hmain

    # using a run file
    @hmain(base_cfg_dir="./cfg/bases", run_cfg_file="./run.yaml")
    def main():
        # do some fancy stuff

If you run the main above with the command::

    python3 main.py --a=1.2345 --d=[1, 2, 3]

You will get a config like this:

.. code-block:: yaml

    a: 1.2345
    b: 2
    c: False
    d: [1, 2, 3]

As usual, if you need to disable the parsing of command line arguments, you can do it
with one of ``hmain`` arguments.

More details on ``hmain`` can be found :ref:`here <api>`.

*****************
The hcfg function
*****************

So far, we have discussed how to connect Hesiod with your program, in order to allow it to load
properly the config. But how it is possibile to access the config loaded by Hesiod? The answer is the
function ``hcfg``, which allows you to get a value from your config **anywhere** in the code, without
passing around the whole config to every function and object.

Let's see how the ``hcfg`` function works with an example. Imagine that you prepared a run file like
this:

.. code-block:: yaml

    # run.yaml

    a: 1
    b: 2
    c: False
    d:
      e:
        f: [1, 2, 3]
        g: 1e-10

If you wrap your main with ``@hmain(base_cfg_dir="cfg/bases", run_cfg_file="run.yaml")``, Hesiod will
load ``run.yaml`` to create your config. Then, you can use the ``hcfg`` function **everywhere** in
your code as follows:

.. code-block:: python

    # anyfile.py

    from hesiod import hcfg

    a = hcfg("a")  # a = 1
    c = hcfg("c")  # c = False
    d = hcfg("d")  # d = {e: {f: [1, 2, 3], g: 1e-10}}
    g = hcfg("d.e.g")  # g = 1e-10

As you may see, you just need to call ``hcfg`` by passing it the key that identifies the config that
you need, and that's it. The key can be a composition of keys and subkeys separated by dots (e.g.
``"d.e.g"`` in the example).

Optionally, you can pass a ``Type`` to ``hcfg``, enabling two things:

1. Hesiod will check that the required config is of the required type and will raise an error if
   that's not the case.
2. The code linter will know the type of the returned config and you will be able to exploit code
   completion and similar stuff.

Reusing the above example, we can do something like this:

.. code-block:: python

    # anyfile.py

    from typing import Dict
    from hesiod import hcfg

    a = hcfg("a", int)  # a = 1
    c = hcfg("c", float)  # ValueError
    d = hcfg("d", Dict)  # d = {e: {f: [1, 2, 3], g: 1e-10}}
    g = hcfg("d.e.g", float)  # g = 1e-10

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
