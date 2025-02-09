"""

utility for developers to automatically write namespaces python files automatically

This module should not be called during normal operation. It is only for developers who want to
update the namespace files.

"""
import datetime
import json
import pathlib
import warnings
from typing import Iterable, Dict, Union, Optional

import requests
from rdflib import Graph, BNode
from rdflib import OWL, RDF, RDFS

from ontolutils import __version__

__this_dir__ = pathlib.Path(__file__).parent
__package_dir__ = __this_dir__.parent / 'namespacelib'

FORCE_DOWNLOAD = True

FORBIDDEN_PROPERTIES = ["and", "or", "type", "yield", "True", "False", "in", "not", "is", "as", "if", "else", "elif",]
def generate_namespace_file_from_ttl(namespace: str,
                                     source: str,
                                     ns: str,
                                     is_owl: bool = False,
                                     target_dir: Optional[Union[str, pathlib.Path]] = None,
                                     fail=True):
    """Generate M4I_NAMESPACE.py file from m4i_context.jsonld
    """
    cls_type = RDFS.Class if not is_owl else OWL.Class
    prop_type = RDF.Property if not is_owl else OWL.ObjectProperty
    if is_owl:
        data_prop = OWL.DatatypeProperty
        named_individual = OWL.NamedIndividual
    else:
        named_individual = None
        data_prop = None


    g = Graph()
    g.parse(source)
    g.namespace_manager.bind(namespace, ns)
    if target_dir is None:
        target_dir = __this_dir__
    else:
        target_dir = pathlib.Path(target_dir)

    with open(target_dir / f'{namespace}.py', 'w',
              encoding='UTF8') as f:
        f.write('from rdflib.namespace import DefinedNamespace, Namespace\n')
        f.write('from rdflib.term import URIRef\n\n\n')
        f.write(f'class {namespace.upper()}(DefinedNamespace):')
        f.write(f'\n    # Generated with ontolutils version {__version__}')
        f.write(f'\n    _fail = {fail}')

        for cls in g.subjects(RDF.type, cls_type):
            # u = str(s).rsplit('/', 1)[-1].replace('-', '_')
            if not isinstance(cls, BNode):
                class_split = str(cls).split(ns)
                if len(class_split) == 2:
                    _key = class_split[-1]
                    if _key[0].isdigit():
                        _key = f'_{_key}'
                    f.write(f'\n    {_key}: URIRef')
        for prop in g.subjects(RDF.type, prop_type):
            if not isinstance(prop, BNode):
                prop_split =str(prop).split(ns)
                if len(prop_split) == 2:
                    if prop_split[-1] not in FORBIDDEN_PROPERTIES:
                        _key = prop_split[-1]
                        if _key[0].isdigit():
                            _key = f'_{_key}'
                        f.write(f'\n    {_key}: URIRef')

        if data_prop:
            for prop in g.subjects(RDF.type, data_prop):
                if not isinstance(prop, BNode):
                    prop_split =str(prop).split(ns)
                    if len(prop_split) == 2:
                        if prop_split[-1] not in FORBIDDEN_PROPERTIES:
                            f.write(f'\n    {prop_split[-1]}: URIRef')

        if named_individual:
            for prop in g.subjects(RDF.type, named_individual):
                if not isinstance(prop, BNode):
                    prop_split =str(prop).split(ns)
                    if len(prop_split) == 2:
                        if prop_split[-1] not in FORBIDDEN_PROPERTIES:
                            f.write(f'\n    {prop_split[-1]}: URIRef')


        f.write(f'\n\n    _NS = Namespace("{ns}")')


def generate_namespace_file_from_context(namespace: str,
                                         context_ld: str,
                                         languages: Optional[Dict[str, Iterable[str]]] = None,
                                         target_dir: Optional[Union[str, pathlib.Path]] = None,
                                         fail: bool = True,
                                         filename: Optional[Union[str, pathlib.Path]] = None):
    """Generate M4I_NAMESPACE.py file from m4i_context.jsonld"""
    languages = languages or {}
    assert isinstance(languages, dict)
    context_file = __this_dir__ / f'{namespace}.jsonld'

    if not context_file.exists() or FORCE_DOWNLOAD:
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(requests.get(context_ld).text, )

    # read context file:
    with open(context_file, encoding='utf-8') as f:
        context = json.load(f)

    url = context['@context'][namespace]

    iris = {}
    for k, v in context['@context'].items():
        if k not in ('type', 'id'):
            if '@id' in v:
                if namespace in v['@id']:
                    name = v["@id"].rsplit(":", 1)[-1]

                    if '#' in name:
                        warnings.warn(f'Skipping {name} ({v}) because it has a "#" in it.')
                    elif name[0].isdigit():
                        warnings.warn(f'Skipping {name} ({v}) because it starts with a digit.')
                    elif name in ('True', 'False', 'yield'):
                        warnings.warn(f'Skipping {name} ({v}) because it starts with "yield".')
                    else:
                        if name not in iris:
                            iris[name] = {'url': f'{url}{name}', 'keys': [k, ]}
                        else:
                            iris[name]['keys'].append(k)
    if target_dir is None:
        target_dir = __this_dir__
    else:
        target_dir = pathlib.Path(target_dir)

    fields = []

    if filename is None:
        filename = target_dir / f'{namespace}.py'
    else:
        filename = pathlib.Path(filename)
    with open(filename, 'w',
              encoding='UTF8') as f:
        f.write('from rdflib.namespace import DefinedNamespace, Namespace\n')
        f.write('from rdflib.term import URIRef\n')
        f.write('\n\nclass LanguageExtension:\n    pass')
        f.write(f'\n\nclass {namespace.upper()}(DefinedNamespace):')
        f.write(f'\n    # uri = "{url}"')
        f.write(f'\n    # Generated with ontolutils version {__version__}')
        f.write(f'\n    # Date: {datetime.datetime.now()}')
        f.write(f'\n    _fail = {fail}')
        for k, v in iris.items():
            if k not in fields:
                fields.append(k)
                if '-' in k:
                    f.write(f'\n    {k.replace("-", "_")} = URIRef("{url}{k}")  # {v["keys"]}')
                else:
                    f.write(f'\n    {k}: URIRef  # {v["keys"]}')

        f.write(f'\n\n    _NS = Namespace("{url}")')

        for lang in languages:
            f.write(f'\n\n{lang} = LanguageExtension()')

        f.write('\n')

        for k, v in iris.items():
            for kk in v["keys"]:
                found_language_key = False
                key = kk.replace(' ', '_')
                for lang_key, lang_values in languages.items():
                    if key in lang_values:
                        f.write(f'\nsetattr({lang_key}, "{key}", {namespace.upper()}.{k.replace("-", "_")})')
                        found_language_key = True
                if not found_language_key:
                    f.write(f'\nsetattr({namespace.upper()}, "{key}", {namespace.upper()}.{k.replace("-", "_")})')

        for lang in languages:
            f.write(f'\n\nsetattr({namespace.upper()}, "{lang}", {lang})')
    context_file.unlink(missing_ok=True)


def m4i():
    """generates namespace for metadata4Ing ontology (M4I)"""
    generate_namespace_file_from_context(
        'm4i',
        context_ld='http://w3id.org/nfdi4ing/metadata4ing/m4i_context.jsonld',
        languages={'de': [
            'Methode',
            'numersiche_Zuweisung',
            'numerische_Variable',
            'Arbeitsschritt',
            'textbasierte_Variable',
            'Werkzeug',
            'Unsicherheitsdeklaration',
            'hat_als_zulässige_Einheit',
            'hat_als_zulässigen_Wert',
            'hat_zugewiesenen_Wert',
            'hat_Überdeckungsintervall',
            'hat_eingesetztes_Werkzeug',
            'hat_erweiterte_Unsicherheit',
            'hat_Größenart',
            'hat_Parameter',
            'hat_Laufzeitzuweisung',
            'hat_Unsicherheitsdeklaration',
            'hat_Einheit',
            'hat_Variable',
            'gehört_zu_Projekt',
            'untersucht',
            'untersucht_Eigenschaft',
            'ist_eingesetztes_Werkzeug',
            'hat_Projektmitglied',
            'realisiert_Methode',
            'Verwendungshinweis',
            'Projektenddatum',
            'hat_Zuweisungszeitstempel',
            'hat_Datumszuweisung_erzeugt',
            'hat_Datumszuweisung_gelöscht',
            'hat_Datumszuweisung_bearbeitet',
            'hat_Datumszuweisung_gültig_ab',
            'hat_Datumszuweisung_gültig_bis',
            'hat_Maximalwert',
            'hat_Minimalwert',
            'hat_Zahlenwert',
            'hat_Schrittweite',
            'hat_Zeichenwert',
            'hat_Symbol',
            'hat_Wert',
            'hat_Variablenbeschreibung',
            'hat_Identifikator',
            'hat_ORCID_ID',
            'hat_Projekt-ID',
            'Projektstartdatum',
            'Kontaktperson',
            'Datenerfasser*in',
            'Datenkurator*in',
            'Datenkurator*in',
            'Datenverwalter*in',
            'Anbieter*in',
            'Herausgeber*in',
            'bereitstellende_Institution',
            'weitere_Person',
            'Produzent*in',
            'Projektleiter*in',
            'Projektmanager*in',
            'Projektmitglied',
            'Registrierungsstelle',
            'Registrierungsbehörde',
            'zugehörige_Person',
            'Forschungsgruppe',
            'Rechercheur*in',
            'Rechteinhaber*in',
            'Sponsor*in',
            'Betreuer*in',
            'Arbeitspaketleiter*in',
        ]}
    )


def obo():
    """Generate obo ontology namespace class"""
    generate_namespace_file_from_context(
        'obo',
        # context_ld='https://raw.githubusercontent.com/biopragmatics/bioregistry/main/exports/contexts/obo.context.jsonld',
        context_ld='http://w3id.org/nfdi4ing/metadata4ing/m4i_context.jsonld',
        languages={'de': ['Prozess',
                          'realisierbare_Entität',
                          'Teil_von',
                          'hat_Teil',
                          'realisiert_in',
                          'realisiert',
                          'ist_Voraussetzung_für_Schritt',
                          'ist_beteiligt_an',
                          'hat_Teilnehmer',
                          'ist_unmittelbare_Voraussetzung_für_Schritt',
                          'beginnt_mit',
                          'endet_mit',
                          'hat_Input',
                          'hat_Output',
                          'Input_von',
                          'Output_von',

                          ]
                   }
    )
    # # be careful, german lines must be manually uncommented
    # # generate_qudt_unit_namespace()  # write _qudt_namespace.py manually
    # generate_qudt_quantitykind_namespace()  # write _qudt_quantitykind_namespace.py manually
    # generate_codemeta_namespace()


def qudt_unit():
    generate_namespace_file_from_ttl(
        namespace='qudt_unit',
        source='http://qudt.org/vocab/unit/',
        ns='http://qudt.org/vocab/unit/',
    )


def hdf5():
    generate_namespace_file_from_ttl(
        namespace='hdf5',
        source='https://purl.allotrope.org/voc/adf/REC/2024/12/hdf.ttl',
        ns='http://purl.allotrope.org/ontologies/hdf5/1.8#',
        is_owl=True
    )


def qudt_quantitykind():
    generate_namespace_file_from_ttl(
        namespace='qudt_kind',
        source='http://qudt.org/vocab/quantitykind/',
        ns='http://qudt.org/vocab/quantitykind/',
    )


def schema():
    generate_namespace_file_from_ttl(
        namespace='schema',
        source='https://schema.org/version/latest/schemaorg-current-https.jsonld',
        ns='https://schema.org/',
    )


def codemeta():
    generate_namespace_file_from_context(
        namespace='codemeta',
        context_ld='https://raw.githubusercontent.com/codemeta/codemeta/2.0/codemeta.jsonld'
    )


def build_namespace_files():
    """Call this only if you are a developer and want to build the namespace files"""
    # with open(__package_dir__ / '__init__.py', 'w') as f:
    #     f.write('"""Auto-generated file. Do not edit!"""\n')
    # f.write('from ._version import __version__\n')

    m4i()
    #
    # obo()
    #
    # qudt_unit()
    #
    # qudt_quantitykind()
    #
    # codemeta()
    #
    schema()

    hdf5()

    # with open(__package_dir__ / '__init__.py', 'a') as f:
    # f.write('from .m4i import M4I\n')
    # f.write('from .obo import OBO\n')
    # f.write('from .pivmeta import PIVMETA\n')
    # f.write('from .codemeta import CODEMETA\n')
    # f.write('from .qudt_unit import QUDT_UNIT\n')
    # f.write('from .qudt_kind import QUDT_KIND\n')
    # f.write('from .schema import SCHEMA\n')
    # f.write('from .ssno import SSNO\n')
    # f.write('from ._iana_utils import IANA\n')

    for jld in __package_dir__.glob('*.jsonld'):
        jld.unlink()


if __name__ == '__main__':
    """Call this only if you are a developer and want to build the namespace files"""
    build_namespace_files()
