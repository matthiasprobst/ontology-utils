"""Strict JSON-LD encoding for IEEE values unsupported by JSON numbers."""
import json
import math

from rdflib import Literal, XSD, plugin
from rdflib.plugins.serializers.jsonld import from_rdf
from rdflib.plugins.shared.jsonld.context import Context
from rdflib.serializer import Serializer


_STRICT_FORMAT = '_ontolutils-jsonld'


def _number_to_jsonld(value):
    """Encode IEEE nonfinite floats as xsd:double literals, not JSON numbers."""
    if isinstance(value, float) and not math.isfinite(value):
        lexical = 'NaN' if math.isnan(value) else 'INF' if value > 0 else '-INF'
        return {'@value': lexical, '@type': str(XSD.double)}
    return value


def _strict_values(value, value_key, type_key):
    """Normalize native numbers before any JSON encoder can discard their value."""
    if isinstance(value, list):
        return [_strict_values(item, value_key, type_key) for item in value]
    if isinstance(value, dict):
        result = dict(value)
        literal = result.get(value_key)
        if isinstance(literal, float) and not math.isfinite(literal):
            replacement = _number_to_jsonld(literal)
            result[value_key] = replacement['@value']
            result.setdefault(type_key, replacement['@type'])
        return {key: _strict_values(item, value_key, type_key) for key, item in result.items()}
    return _number_to_jsonld(value)


class _StrictJsonLDSerializer(Serializer):
    """Use RDFLib conversion with strict encoding before native NaN/INF are lost."""

    def serialize(self, stream, base=None, encoding=None, **kwargs):
        context_data = kwargs.get('context')
        context = context_data if isinstance(context_data, Context) else Context(context_data, base=base)
        result = from_rdf(
            self.store, context_data=context if context_data is not None else None,
            base=base, use_native_types=kwargs.get('use_native_types', False),
            use_rdf_type=kwargs.get('use_rdf_type', False),
            auto_compact=kwargs.get('auto_compact', False))
        result = _strict_values(result, context.get_key('@value'), context.get_key('@type'))
        text = json.dumps(result, allow_nan=False, indent=kwargs.get('indent', 2),
                          separators=kwargs.get('separators', (',', ': ')),
                          sort_keys=kwargs.get('sort_keys', True),
                          ensure_ascii=kwargs.get('ensure_ascii', False))
        stream.write(text.encode(encoding or 'utf-8', 'replace'))


def _serialize_graph(graph, rdf_format, **kwargs):
    """Keep RDFLib's destinations/encodings; fix JSON-LD only for nonfinite graphs."""
    if rdf_format in ('json-ld', 'application/ld+json') and any(
            isinstance(obj, Literal) and isinstance(obj.value, float) and not math.isfinite(obj.value)
            for obj in graph.objects()):
        plugin.register(_STRICT_FORMAT, Serializer, __name__, '_StrictJsonLDSerializer')
        return graph.serialize(format=_STRICT_FORMAT, **kwargs)
    return graph.serialize(format=rdf_format, **kwargs)
