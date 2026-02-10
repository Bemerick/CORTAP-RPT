#!/usr/bin/env python3
"""
Clean Word XML from inside Jinja2 blocks - Version 2.

Handles cases where Word splits even the delimiters themselves.
Strategy: Find text runs and reassemble Jinja2 blocks from text content only.
"""

import zipfile
import shutil
import re
from pathlib import Path


def extract_all_text_runs(xml_content):
    """Extract all <w:t> text runs in order."""

    # Find all <w:t>...</w:t> tags and their positions
    text_runs = []

    for match in re.finditer(r'<w:t[^>]*>([^<]*)</w:t>', xml_content):
        text_runs.append({
            'start': match.start(),
            'end': match.end(),
            'text': match.group(1),
            'full': match.group(0)
        })

    return text_runs


def reassemble_jinja_blocks(xml_content):
    """Reassemble Jinja2 blocks by merging consecutive text runs within blocks."""

    # Strategy: Find jinja delimiters in text runs, then merge runs between them

    # First, get all text runs
    text_runs = extract_all_text_runs(xml_content)

    # Build a "text view" - what the template looks like as pure text
    text_view = ''.join(run['text'] for run in text_runs)

    print(f"Text runs: {len(text_runs)}")
    print(f"Text view: {len(text_view)} chars\n")

    # Find Jinja2 blocks in the text view
    expr_blocks = list(re.finditer(r'(\{\{)(.*?)(\}\})', text_view, re.DOTALL))
    stmt_blocks = list(re.finditer(r'(\{%)(.*?)(%\})', text_view, re.DOTALL))

    print(f"Jinja2 blocks in text view:")
    print(f"  Expressions {{ }}: {len(expr_blocks)}")
    print(f"  Statements {{% %}}: {len(stmt_blocks)}\n")

    # Now we need to map text positions back to XML positions and replace
    # This is complex, so let's use a simpler approach:
    # 1. Extract text runs
    # 2. Merge consecutive runs that are part of the same Jinja2 block
    # 3. Replace multi-run blocks with single-run blocks

    result = xml_content

    # Process each block type
    all_blocks = []
    for match in expr_blocks:
        all_blocks.append({
            'type': 'expr',
            'start': match.start(),
            'end': match.end(),
            'opening': '{{',
            'content': match.group(2).strip(),
            'closing': '}}'
        })

    for match in stmt_blocks:
        all_blocks.append({
            'type': 'stmt',
            'start': match.start(),
            'end': match.end(),
            'opening': '{%',
            'content': match.group(2).strip(),
            'closing': '%}'
        })

    # Sort by position
    all_blocks.sort(key=lambda b: b['start'])

    # Now we need to find these blocks in the XML and clean them
    # For each block in text view, find corresponding XML span and replace

    # Build position map: text_view position -> xml position
    text_to_xml_map = []
    text_pos = 0
    for run in text_runs:
        run_text = run['text']
        for i, char in enumerate(run_text):
            text_to_xml_map.append({
                'text_pos': text_pos + i,
                'xml_start': run['start'],
                'xml_end': run['end'],
                'run': run
            })
        text_pos += len(run_text)

    # For each Jinja block, find XML runs it spans
    replacements = []

    for block in all_blocks:
        # Find XML runs that contain this block
        block_start_text = block['start']
        block_end_text = block['end']

        # Find all runs that overlap with this text range
        runs_in_block = set()
        for mapping in text_to_xml_map[block_start_text:block_end_text]:
            runs_in_block.add((mapping['xml_start'], mapping['xml_end']))

        if len(runs_in_block) > 1:
            # Multiple runs - need to merge
            runs_in_block = sorted(runs_in_block)
            xml_start = runs_in_block[0][0]
            xml_end = runs_in_block[-1][1]

            # Build clean replacement
            if block['type'] == 'stmt':
                clean_block = f"{block['opening']} {block['content']} {block['closing']}"
            else:
                clean_block = f"{block['opening']} {block['content']} {block['closing']}"

            replacement_xml = f'<w:t>{clean_block}</w:t>'

            replacements.append({
                'start': xml_start,
                'end': xml_end,
                'replacement': replacement_xml,
                'block': block
            })

    print(f"Found {len(replacements)} multi-run blocks to merge\n")

    # Apply replacements in reverse order to maintain positions
    replacements.sort(key=lambda r: r['start'], reverse=True)

    for repl in replacements:
        result = result[:repl['start']] + repl['replacement'] + result[repl['end']:]

    size_reduction = len(xml_content) - len(result)
    print(f"Size reduction: {size_reduction:,} chars ({size_reduction/len(xml_content)*100:.1f}%)")

    return result


def clean_template(input_path, output_path=None):
    """Clean Jinja2 blocks in Word template."""

    input_path = Path(input_path)

    if output_path is None:
        # Create backup
        backup_path = input_path.with_stem(input_path.stem + '_before_v2_clean')
        shutil.copy2(input_path, backup_path)
        print(f"✅ Backup created: {backup_path}\n")
        output_path = input_path
    else:
        output_path = Path(output_path)

    temp_dir = Path('temp_clean_jinja_v2')
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract
        print(f"Extracting: {input_path}")
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Read document.xml
        doc_xml = temp_dir / 'word' / 'document.xml'
        with open(doc_xml, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        print(f"Original XML: {len(xml_content):,} characters\n")

        # Clean
        cleaned_xml = reassemble_jinja_blocks(xml_content)

        # Write back
        with open(doc_xml, 'w', encoding='utf-8') as f:
            f.write(cleaned_xml)

        print(f"\nFinal XML: {len(cleaned_xml):,} characters")

        # Repackage
        print(f"\nRepackaging to: {output_path}")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zip_out.write(file_path, arcname)

        print(f"\n✅ Cleaned template saved!")

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python clean_jinja_blocks_v2.py <template.docx> [output.docx]")
        print("\nReassembles fragmented Jinja2 blocks by merging text runs.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    clean_template(input_file, output_file)
