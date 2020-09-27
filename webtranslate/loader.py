"""
Helper functions for loading an Xml tree.
"""
import logging

from xml.dom import minidom
from xml.dom.minidom import Node

log = logging.getLogger(__name__)


def load_dom(fname):
    """
    Load the XML file as DOM into memory.

    @param fname: File to load.
    @type  fname: C{str}

    @todo: XXX Implement some safe guards for loading too big files.
    """
    dom = minidom.parse(fname)
    return dom


def get_opt_DOMattr(node, name, default):
    """
    Get an optional value from the DOM node.

    @param node: DOM node being read.
    @type  node: L{xml.dom.minidom.ElementNode}

    @param name: Name of the value.
    @type  name: C{str}

    @param default: Default value as string.
    @type  default: C{unicode}

    @return: The requested value.
    @rtype:  C{unicode}
    """
    if node.hasAttribute(name):
        return node.getAttribute(name)
    return default


def collect_text_DOM(node):
    """
    Collect all text of this node.

    @param node: DOM node being read.
    @type  node: L{xml.dom.minidom.ElementNode}

    @return: The collected text.
    @rtype:  C{unicode}
    """
    return "".join(n.data for n in node.childNodes if n.nodeType == Node.TEXT_NODE)


def get_child_nodes(node, name):
    """
    Get all direct child nodes with a given name.

    @param node: DOM node being read.
    @type  node: L{xml.dom.minidom.ElementNode}

    @param name: Name of the child node.
    @type  name: C{unicode}

    @return: All direct child nodes with the given name.
    @rtype:  C{list} of L{xml.dom.minidom.Node}
    """
    if not node.hasChildNodes():
        return []
    result = []
    for n in node.childNodes:
        if n.nodeType != Node.ELEMENT_NODE:
            continue
        if n.tagName == name:
            result.append(n)
    return result


def get_single_child_node(node, name, optional=False):
    """
    Get the child node with the given name (there should be exactly one).

    @param node: DOM node being read.
    @type  node: L{xml.dom.minidom.ElementNode}

    @param name: Name of the child node.
    @type  name: C{unicode}

    @param optional: Child node may be optional.
    @type  optional: C{bool}

    @return: The unique child node with the given name (or C{None}).
    @rtype:  L{xml.dom.minidom.Node} or C{None}
    """
    result = get_child_nodes(node, name)
    if len(result) == 1:
        return result[0]
    if optional and len(result) == 0:
        return None

    log.error('Failed to find precisely one child node named "%s"', name)
    return None
