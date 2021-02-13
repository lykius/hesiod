############
Config Files
############

Hesiod relies on config files, allowing you to create the config for your program with two simple
concepts:

1. You should define the configs for each **entity** of your program in a separate file.
2. You can combine configs hierarchically to compose the global config of your program.

********************
Config files content
********************

Each config file represents a key-value dictionary. For the time being, Hesiod supports ``.yaml``
files and you can write anything that is compliant with the `YAML <https://yaml.org/>`_ format:

.. code-block:: yaml

    p1: 1  # integer
    p2: 1.2  # float
    p3: 1e-4  # another float
    p4: true  # boolean
    p5: "test"  # string
    p6: [1, 2, 3]  # list
    p7: !!python/tuple [1, 2, 3]  # tuple
    p8: !!set {1: null, 2: null, 3: null}  # set
    p9: 2021-01-01  # date
    p10:  # dictionary that contains...
      p11:  # ...another dictionary that contains...
        p12: 10  # ...an integer and...
        p13: "11"  # ...a string and...
        p14: 12.0  # ...a float


******************
The base mechanism
******************
.. _base-mechanism:

One of the key elements in Hesiod is the **base mechanism**, triggered by the use of
the special keyword ``base``. The first step to use the base mechanism consists in defining base
configs in a directory of your choice. This directory could be something like this ("scenario1",
"case1", "case2", "scenario2", etc are just examples, they can be whatever you like)::

    cfg/bases
    |
    |____ scenario1
    |    |
    |    |____ case1
    |    |    |____ params1.yaml
    |    |    |____ params2.yaml
    |    |
    |    |____ case2
    |         |____ params1.yaml
    |         |____ params2.yaml
    |
    |____ scenario2
         |
         |____ ...

You tell Hesiod where it can find your base configs by specifying the path to the
bases directory in the ``hmain`` decorator (i.e. ``@hmain(base_cfg_dir="cfg/bases", ...)``).

Then, you can use the keyword ``base`` to load in the current file the config dictionary defined in
some base file. For instance, if we have:

.. code-block:: yaml

    # cfg/bases/scenario1/case2/params2.yaml

    p1: 1
    p2: 2.0
    p3: "3"

You can load the base ``scenario1.case2.params2`` by doing:

.. code-block:: yaml

    # config.yaml

    base: "scenario1.case2.params2"
    p3: 3.456

Hesiod will solve the ``base`` keyword in ``config.yaml`` by loading in it the content from
``cfg/bases/scenario1/case2/params2.yaml``, without touching the parameters that are overriden in
``config.yaml``. The result is a config defined as:

.. code-block:: yaml

    p1: 1
    p2: 2.0
    p3: 3.456

***************************
Run files vs Template files
***************************

In Hesiod you have two options:

1. You can define a **run** file with the specific configs for each run of your program.
2. You can define a **template** file with the abstract structure of the config, without
    specifying any actual value.

Run files
=========

Run files are normal config files, where you can compose configs with the base mechanism and/or
specify additional parameters. Using the bases dir defined above, a valid run file could be:

.. code-block:: yaml

    # run.yaml

    first_scenario:
      base: "scenario1.case2.params1"
    second_scenario:
      base: "scenario2.case1.params2"
    some_param: 1e-5
    another_param: "test"
    a_group_of_params:
      p1: 1
      p2: true
      p3: ["a", "b", "c"]

    run_name: "very_cool_run"

Note that every run file must contain a valid ``run_name``, that will be used by Hesiod to create
an output directory for the run (named accordingly).

Template files
==============

**Template** files can contain all the options available for normal config files. In addition,
there are some special placeholders:

.. list-table::
    :widths: 20 80
    :header-rows: 1

    * - Placeholder
      - Description
      - The user will select one of the base configs (i.e. ``.yaml`` files) 
    * - ``@BASE(key)``
      
        available in the path specified by ``key``. The key can represent a
        
        complete path with the notation ``dir.subdir.subsubdir`` etc.
    * - ``@OPTIONS(opt1;opt2;opt3;...)``
      - The user will select one of the given options.
    * - ``@BOOL(true)``
    
        ``@BOOL(false)``
      - The user will select between `TRUE` and `FALSE`,
      
        with the default set as specified.
    * - ``@FILE``
    
        ``@FILE(path/to/default)``
      - The user will select a file starting either from
      
        the current directory or from a default path.
    * - ``@DATE``
        
        ``@DATE(today)``
        
        ``@DATE(YYYY-MM-DD)``
      - The user will select a date, starting from today or from a default date.
