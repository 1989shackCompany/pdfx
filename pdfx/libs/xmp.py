#!/usr/bin/env python
"""
xmp.py
~~~~~~

Parses XMP metadata from PDF files.

By Matt Swain. Released under the MIT license.

http://blog.matt-swain.com/post/25650072381/a-lightweight-xmp-parser-for-extracting-pdf
"""

from collections import defaultdict
from xml.etree import ElementTree as ET

RDF_NS = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
XML_NS = "{http://www.w3.org/XML/1998/namespace}"
NS_MAP = {
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
    "http://purl.org/dc/elements/1.1/": "dc",
    "http://ns.adobe.com/xap/1.0/": "xap",
    "http://ns.adobe.com/pdf/1.3/": "pdf",
    "http://ns.adobe.com/xap/1.0/mm/": "xapmm",
    "http://ns.adobe.com/pdfx/1.3/": "pdfx",
    "http://prismstandard.org/namespaces/basic/2.0/": "prism",
    "http://crossref.org/crossmark/1.0/": "crossmark",
    "http://ns.adobe.com/xap/1.0/rights/": "rights",
    "http://www.w3.org/XML/1998/namespace": "xml",
}


class XmpParser(object):
    """
    Parses an XMP string into a dictionary.

    Usage:

        parser = XmpParser(xmpstring)
        meta = parser.meta
    """

    def __init__(self, xmp):
        self.tree = ET.XML(xmp)
        self.rdftree = self.tree.find(f"{RDF_NS}RDF")

    @property
    def meta(self):
        """ A dictionary of all the parsed metadata. """
        meta = defaultdict(dict)
        for desc in self.rdftree.findall(f"{RDF_NS}Description"):
            for (
                el
            ) in (
                desc.iter()
            ):  # getchildren() is deprecated since python 2.7 and 3.2, fixed it
                ns, tag = self._parse_tag(el)
                value = self._parse_value(el)
                meta[ns][tag] = value
        return dict(meta)

    def _parse_tag(self, el):
        """ Extract the namespace and tag from an element. """
        ns = None
        tag = el.tag
        if tag[0] == "{":
            ns, tag = tag[1:].split("}", 1)
            if ns in NS_MAP:
                ns = NS_MAP[ns]
        return ns, tag

    def _parse_value(self, el):    # noqa: C901
        """ Extract the metadata value from an element. """
        if el.find(f"{RDF_NS}Bag") is not None:
            return [li.text for li in el.findall(f"{RDF_NS}Bag/{RDF_NS}li")]
        elif el.find(f"{RDF_NS}Seq") is not None:
            return [li.text for li in el.findall(f"{RDF_NS}Seq/{RDF_NS}li")]
        elif el.find(f"{RDF_NS}Alt") is not None:
            return {
                li.get(f"{XML_NS}lang"): li.text
                for li in el.findall(f"{RDF_NS}Alt/{RDF_NS}li")
            }

        else:
            return el.text


def xmp_to_dict(xmp):
    """Shorthand function for parsing an XMP string into a python
    dictionary."""
    return XmpParser(xmp).meta
