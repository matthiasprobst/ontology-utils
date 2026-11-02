.. _configuration:

Configuration
=============

Use ``with set_config(...)`` for a temporary change. Leaving the block restores
the previous settings, including when an exception occurs. Calling
``set_config(...)`` without ``with`` changes the process-wide configuration.

.. testcode::

   from ontolutils import LangString, Thing, get_config, set_config

   original = get_config("show_lang_in_str")
   with set_config(show_lang_in_str=False):
       assert str(LangString(value="Velocity", lang="en")) == "Velocity"
   assert get_config("show_lang_in_str") == original

Available settings
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Key
     - Default
     - Meaning
   * - ``show_lang_in_str``
     - ``True``
     - Include ``@en`` etc. in a language string's display; RDF is unaffected.
   * - ``blank_id_generator``
     - ``None``
     - Use RDFLib's blank IDs, or supply a no-argument callable returning an ID.

For predictable IDs within a notebook or test:

.. testcode::

   from itertools import count

   counter = count()
   def next_id():
       return f"_:run{next(counter)}"

   with set_config(blank_id_generator=next_id):
       run = Thing(label="Run 0")
   assert run.id == "_:run0"

``blank_node_prefix_name`` is not a supported setting. Use an explicit ``id``
or the serialization ``base_uri`` parameter described in :doc:`serialization`.
