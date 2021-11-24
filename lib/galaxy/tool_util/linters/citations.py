"""This module contains a citation lint function.

Citations describe references that should be used when consumers
of the tool publish results.
"""


def lint_citations(tool_xml, lint_ctx):
    """Ensure tool contains at least one valid citation."""
    root = tool_xml.getroot()
    citations = root.findall("citations")
    if len(citations) > 1:
        lint_ctx.error("More than one citation section found, behavior undefined.", line=citations[1].sourceline)
        return

    if len(citations) == 0:
        lint_ctx.warn("No citations found, consider adding citations to your tool.", line=root.sourceline)
        return

    valid_citations = 0
    for citation in citations[0]:
        if citation.tag != "citation":
            lint_ctx.warn(f"Unknown tag discovered in citations block [{citation.tag}], will be ignored.", line=citation.sourceline)
            continue
        citation_type = citation.attrib.get("type")
        if citation_type not in ('bibtex', 'doi'):
            lint_ctx.warn(f"Unknown citation type discovered [{citation_type}], will be ignored.", line=citation.sourceline)
            continue
        if citation.text is None or not citation.text.strip():
            lint_ctx.error(f'Empty {citation_type} citation.', line=citation.sourceline)
            continue
        valid_citations += 1

    if valid_citations > 0:
        lint_ctx.valid(f"Found {valid_citations} likely valid citations.", line=root.sourceline)
