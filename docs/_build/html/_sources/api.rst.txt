API
===

.. autosummary::
    :toctree: generated

Functions to interact with config files
---------------------------------------

.. autofunction:: econf.read_file

.. autofunction:: econf.new_key_file

.. autofunction:: econf.new_ini_file

.. autofunction:: econf.merge_files

.. autofunction:: econf.read_dirs

.. autofunction:: econf.read_dirs_history

.. autofunction:: econf.write_file

Functions for getting values
----------------------------

.. autofunction:: econf.get_groups

.. autofunction:: econf.get_keys

.. autofunction:: econf.get_int_value

.. autofunction:: econf.get_uint_value

.. autofunction:: econf.get_float_value

.. autofunction:: econf.get_string_value

.. autofunction:: econf.get_bool_value

Functions for getting values with defaults
------------------------------------------

.. autofunction:: econf.get_int_value_def

.. autofunction:: econf.get_uint_value_def

.. autofunction:: econf.get_float_value_def

.. autofunction:: econf.get_string_value_def

.. autofunction:: econf.get_bool_value_def

Functions for setting values
----------------------------

.. autofunction:: econf.set_int_value

.. autofunction:: econf.set_uint_value

.. autofunction:: econf.set_float_value

.. autofunction:: econf.set_string_value

.. autofunction:: econf.set_bool_value

Functions for memory management
-------------------------------

.. autofunction:: econf.free_file

Functions for handling error codes
----------------------------------

.. autofunction:: econf.err_string

.. autofunction:: econf.err_location