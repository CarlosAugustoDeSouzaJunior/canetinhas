#!/usr/bin/env python3
"""Minimal but well-formatted Markdown -> .docx converter (stdlib only).

Targeted at the constructs used in the team docs: H1-H3, paragraphs,
blockquotes, fenced code blocks, GFM tables (with alignment + inline marks),
bullet lists, and inline **bold** / `code` / [text](url).
"""
import sys, re, zipfile, html


def xesc(s):
    return html.escape(s, quote=False)


# ---------- inline parsing ----------
INLINE_RE = re.compile(
    r'(\*\*(?P<b>.+?)\*\*)'      # bold
    r'|(`(?P<c>[^`]+?)`)'        # code
    r'|(\[(?P<lt>[^\]]+?)\]\((?P<lu>[^)]+?)\))'  # link
)


def runs_xml(text):
    """Return run XML for a span of inline markdown."""
    out = []
    pos = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            out.append(run(text[pos:m.start()]))
        if m.group('b') is not None:
            out.append(run(m.group('b'), bold=True))
        elif m.group('c') is not None:
            out.append(run(m.group('c'), code=True))
        elif m.group('lt') is not None:
            out.append(run(m.group('lt') + ' (' + m.group('lu') + ')',
                           color='0563C1', underline=True))
        pos = m.end()
    if pos < len(text):
        out.append(run(text[pos:]))
    return ''.join(out) or run('')


def run(text, bold=False, code=False, color=None, underline=False, italic=False):
    rpr = []
    if bold:
        rpr.append('<w:b/>')
    if italic:
        rpr.append('<w:i/>')
    if underline:
        rpr.append('<w:u w:val="single"/>')
    if color:
        rpr.append(f'<w:color w:val="{color}"/>')
    if code:
        rpr.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>')
        rpr.append('<w:sz w:val="18"/>')
        rpr.append('<w:shd w:val="clear" w:fill="F2F2F2"/>')
    rprx = f'<w:rPr>{"".join(rpr)}</w:rPr>' if rpr else ''
    # preserve spaces
    return (f'<w:r>{rprx}<w:t xml:space="preserve">{xesc(text)}</w:t></w:r>')


def para(inner, style=None, spacing_after=120, ppr_extra=''):
    ppr = '<w:pPr>'
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    ppr += ppr_extra
    ppr += f'<w:spacing w:after="{spacing_after}"/>'
    ppr += '</w:pPr>'
    return f'<w:p>{ppr}{inner}</w:p>'


def heading(text, level):
    return para(runs_xml(text), style=f'Heading{level}', spacing_after=120)


def bullet(text):
    return para(runs_xml(text), spacing_after=60,
                ppr_extra='<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>')


def blockquote(text):
    ind = '<w:ind w:left="360"/><w:pBdr><w:left w:val="single" w:sz="18" w:space="8" w:color="8064A2"/></w:pBdr>'
    return para(runs_xml(text), spacing_after=120, ppr_extra=ind)


def code_block(lines):
    body = []
    for ln in lines:
        body.append(
            '<w:p><w:pPr><w:spacing w:after="0"/>'
            '<w:shd w:val="clear" w:fill="F2F2F2"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
            f'<w:sz w:val="18"/></w:rPr>'
            f'<w:t xml:space="preserve">{xesc(ln)}</w:t></w:r></w:p>')
    return ''.join(body)


def split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in line.split('|')]


def table_xml(rows, aligns):
    ncol = len(rows[0])
    grid = ''.join('<w:gridCol/>' for _ in range(ncol))
    tbl = [
        '<w:tbl><w:tblPr>'
        '<w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="5000" w:type="pct"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:left w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:right w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '</w:tblBorders>'
        '<w:tblLook w:firstRow="1" w:val="0420"/>'
        f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid>'
    ]
    for ri, row in enumerate(rows):
        is_header = (ri == 0)
        tbl.append('<w:tr>')
        if is_header:
            tbl[-1] = '<w:tr><w:trPr><w:tblHeader/></w:trPr>'
        for ci in range(ncol):
            cell = row[ci] if ci < len(row) else ''
            jc = {'center': 'center', 'right': 'right'}.get(
                aligns[ci] if ci < len(aligns) else 'left', 'left')
            shd = '<w:shd w:val="clear" w:fill="4472C4"/>' if is_header else ''
            tcpr = f'<w:tcPr>{shd}<w:tcMar><w:top w:w="40"/><w:bottom w:w="40"/>' \
                   f'<w:left w:w="80"/><w:right w:w="80"/></w:tcMar></w:tcPr>'
            ppr = f'<w:pPr><w:spacing w:after="0"/><w:jc w:val="{jc}"/></w:pPr>'
            if is_header:
                # force white bold text
                inner = bold_white(cell)
            else:
                inner = runs_xml(cell)
            tbl.append(f'<w:tc>{tcpr}<w:p>{ppr}{inner}</w:p></w:tc>')
        tbl.append('</w:tr>')
    tbl.append('</w:tbl>')
    # blank para after table (Word requirement-ish for spacing)
    tbl.append('<w:p><w:pPr><w:spacing w:after="120"/></w:pPr></w:p>')
    return ''.join(tbl)


def bold_white(text):
    # strip ** since header is already bold; keep code formatting
    text = text.replace('**', '')
    parts = []
    pos = 0
    for m in re.finditer(r'`([^`]+?)`', text):
        if m.start() > pos:
            parts.append(run(text[pos:m.start()], bold=True, color='FFFFFF'))
        parts.append(run(m.group(1), bold=True, color='FFFFFF', code=False))
        pos = m.end()
    if pos < len(text):
        parts.append(run(text[pos:], bold=True, color='FFFFFF'))
    return ''.join(parts) or run('', bold=True, color='FFFFFF')


# ---------- block parsing ----------
def parse(md):
    lines = md.split('\n')
    body = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # fenced code
        if stripped.startswith('```'):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            body.append(code_block(buf))
            continue

        # horizontal rule
        if re.fullmatch(r'-{3,}', stripped):
            body.append('<w:p><w:pPr><w:pBdr><w:bottom w:val="single" '
                        'w:sz="6" w:space="1" w:color="BFBFBF"/></w:pBdr>'
                        '<w:spacing w:after="120"/></w:pPr></w:p>')
            i += 1
            continue

        # headings
        m = re.match(r'(#{1,6})\s+(.*)', stripped)
        if m:
            lvl = min(len(m.group(1)), 3)
            body.append(heading(m.group(2), lvl))
            i += 1
            continue

        # table: current line has | and next line is separator
        if '|' in line and i + 1 < n and re.match(r'^\s*\|?[\s:|-]+\|?\s*$', lines[i+1]) and '-' in lines[i+1]:
            header = split_row(line)
            sep = split_row(lines[i+1])
            aligns = []
            for s in sep:
                s = s.strip()
                if s.startswith(':') and s.endswith(':'):
                    aligns.append('center')
                elif s.endswith(':'):
                    aligns.append('right')
                else:
                    aligns.append('left')
            rows = [header]
            i += 2
            while i < n and '|' in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            body.append(table_xml(rows, aligns))
            continue

        # blockquote
        if stripped.startswith('>'):
            qtext = re.sub(r'^>\s?', '', stripped)
            body.append(blockquote(qtext))
            i += 1
            continue

        # bullet
        if re.match(r'^\s*[-*]\s+', line):
            btext = re.sub(r'^\s*[-*]\s+', '', line)
            body.append(bullet(btext))
            i += 1
            continue

        # blank
        if not stripped:
            i += 1
            continue

        # paragraph (gather consecutive non-blank, non-special lines)
        buf = [stripped]
        i += 1
        while i < n and lines[i].strip() and not re.match(
                r'^(#{1,6}\s|>|\s*[-*]\s|```)', lines[i]) and '|' not in lines[i]:
            buf.append(lines[i].strip())
            i += 1
        body.append(para(runs_xml(' '.join(buf))))
    return ''.join(body)


# ---------- docx packaging ----------
STYLES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:asciiTheme="majorHAnsi" w:hAnsiTheme="majorHAnsi"/><w:b/><w:color w:val="1F3864"/><w:sz w:val="40"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="200" w:after="80"/><w:outlineLvl w:val="1"/><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="2" w:color="4472C4"/></w:pBdr></w:pPr><w:rPr><w:b/><w:color w:val="2F5496"/><w:sz w:val="30"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="160" w:after="60"/><w:outlineLvl w:val="2"/></w:pPr><w:rPr><w:b/><w:color w:val="2F5496"/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="BFBFBF"/><w:left w:val="single" w:sz="4" w:color="BFBFBF"/><w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/><w:right w:val="single" w:sz="4" w:color="BFBFBF"/><w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/><w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/></w:tblBorders></w:tblPr></w:style>
</w:styles>'''

NUMBERING = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="360" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol"/></w:rPr></w:lvl></w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>'''

CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>'''

RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>'''


def build(md_path, out_path):
    with open(md_path, encoding='utf-8') as f:
        md = f.read()
    body = parse(md)
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body>{body}'
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1080" w:bottom="1440" w:left="1080" '
        'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
        '</w:body></w:document>'
    )
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CONTENT_TYPES)
        z.writestr('_rels/.rels', RELS)
        z.writestr('word/document.xml', document)
        z.writestr('word/styles.xml', STYLES)
        z.writestr('word/numbering.xml', NUMBERING)
        z.writestr('word/_rels/document.xml.rels', DOC_RELS)
    print(f'wrote {out_path}')


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
