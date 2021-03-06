############
Introduction
############

***************
What is Hesiod?
***************

Hesiod is a simple python library which helps you keeping your configs clean.

There are four main concepts used in Hesiod:

1. Configs are defined hierarchically in files separated from the main code.
2. Each run of your program is associated with a single **run** file.
3. Users can either:

   - Create manually the run file for a specific run.
   - Define a generic **template** file and actual values will be defined interactively before each run.
4. Configs can be accessed anywhere in the code with several modalities.

************
Installation
************

Hesiod is on PyPI, thus you can install it simply by running::

    pip install hesiod

*************
Compatibility
*************

Hesiod is thourougly tested with Python 3.6, 3.7 and 3.8.
