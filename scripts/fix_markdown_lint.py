#!/usr/bin/env python3
import os
import re
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent / "vault"

def fix_double_frontmatter(content):
    # Matches the malformed start with double frontmatter
    pattern = re.compile(r'^---\s*\n\s*\n---\s*\n')
    if pattern.match(content):
        return pattern.sub('---\n', content), True
    return content, False

def parse_frontmatter(content: str):
    """Split file into (frontmatter_str, body_str). Returns (None, content) if no frontmatter."""
    if not content.startswith("---"):
        return None, content
    end = content.find("---", 3)
    if end == -1:
        return None, content
    fm = content[:end + 3]
    body = content[end + 3:]
    return fm, body

def fix_md028(body):
    lines = body.splitlines()
    modified = False
    in_code_block = False
    
    for i in range(len(lines) - 2):
        if lines[i].strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
            
        line = lines[i].strip()
        next_line = lines[i+1].strip()
        next_next_line = lines[i+2].strip()
        
        # Check if line is blockquote and next_next_line starts a callout
        if line.startswith('>') and next_next_line.startswith('> [!'):
            # Check if next_line is a blank/empty blockquote line
            if next_line == '' or next_line == '>':
                lines[i+1] = '<!-- -->'
                modified = True
    return '\n'.join(lines) + '\n', modified

def fix_md009(body):
    lines = body.splitlines()
    modified = False
    in_code_block = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
            
        # If line has trailing spaces, strip them (unless it's a double space line break)
        if line.endswith(' ') and not line.endswith('  '):
            lines[i] = line.rstrip()
            modified = True
    return '\n'.join(lines) + '\n', modified

def parse_and_format_table(lines, d):
    header_idx = d - 1
    
    # Find all data rows
    data_indices = []
    curr = d + 1
    while curr < len(lines):
        # Must start with pipe, optionally with blockquote prefix
        if re.match(r'^\s*(?:>\s*)?\|', lines[curr]):
            data_indices.append(curr)
            curr += 1
        else:
            break
            
    table_indices = [header_idx, d] + data_indices
    
    # Check if there is blockquote prefix
    is_blockquote = False
    bq_prefix = ""
    bq_match = re.match(r'^\s*(>\s*)', lines[header_idx])
    if bq_match:
        is_blockquote = True
        bq_prefix = bq_match.group(1)
        
    # Helper to parse cells (respecting escaped pipes)
    def get_cells(line):
        l = line.strip()
        if l.startswith('>'):
            l = l[len(bq_prefix):].strip()
        if l.startswith('|'):
            l = l[1:]
        if l.endswith('|'):
            l = l[:-1]
        # Split by non-escaped pipes
        parts = re.split(r'(?<!\\)\|', l)
        return [p.strip() for p in parts]
        
    header_cells = get_cells(lines[header_idx])
    delim_cells = get_cells(lines[d])
    rows_cells = [get_cells(lines[idx]) for idx in data_indices]
    
    num_cols = len(header_cells)
    
    # Determine alignments
    alignments = []
    for cell in delim_cells:
        has_left_colon = cell.startswith(':')
        has_right_colon = cell.endswith(':')
        if has_left_colon and has_right_colon:
            alignments.append('center')
        elif has_right_colon:
            alignments.append('right')
        else:
            alignments.append('left')
            
    # Calculate max widths (minimum 5)
    widths = [len(cell) for cell in header_cells]
    for row in rows_cells:
        for col_idx in range(min(len(row), num_cols)):
            widths[col_idx] = max(widths[col_idx], len(row[col_idx]))
            
    widths = [max(w, 5) for w in widths]
    
    # Reconstruct rows
    new_rows = []
    
    # Header
    header_str = bq_prefix + "| " + " | ".join(
        header_cells[i].ljust(widths[i]) for i in range(num_cols)
    ) + " |"
    new_rows.append(header_str)
    
    # Delimiter
    delim_parts = []
    for i in range(num_cols):
        align = alignments[i]
        w = widths[i]
        if align == 'center':
            delim_parts.append(":" + "-" * (w - 2) + ":")
        elif align == 'right':
            delim_parts.append("-" * (w - 1) + ":")
        else:
            delim_parts.append("-" * w)
    delim_str = bq_prefix + "| " + " | ".join(delim_parts) + " |"
    new_rows.append(delim_str)
    
    # Data rows
    for row in rows_cells:
        row_parts = []
        for i in range(num_cols):
            cell_val = row[i] if i < len(row) else ""
            align = alignments[i]
            w = widths[i]
            if align == 'center':
                row_parts.append(cell_val.center(w))
            elif align == 'right':
                row_parts.append(cell_val.rjust(w))
            else:
                row_parts.append(cell_val.ljust(w))
        row_str = bq_prefix + "| " + " | ".join(row_parts) + " |"
        new_rows.append(row_str)
        
    return table_indices, new_rows

def fix_tables(body):
    lines = body.splitlines()
    modified = False
    
    # Find delimiter rows
    delim_indices = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('```'):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
            
        if re.match(r'^\s*(?:>\s*)?\|(?:\s*[:-]+\s*\|)+\s*$', line):
            if i > 0 and '|' in lines[i-1]:
                delim_indices.append(i)
        i += 1
        
    for d in reversed(delim_indices):
        table_indices, new_rows = parse_and_format_table(lines, d)
        header_idx = table_indices[0]
        last_idx = table_indices[-1]
        
        bq_match = re.match(r'^\s*(>\s*)', lines[header_idx])
        bq_prefix = bq_match.group(1).rstrip() + " " if bq_match else ""
        blank_line_val = bq_prefix.rstrip()
        
        # Check if blank line before table is needed
        insert_before = False
        if header_idx > 0:
            prev_line = lines[header_idx - 1].strip()
            if prev_line != "" and prev_line != blank_line_val.strip() and not prev_line.startswith('---'):
                insert_before = True
                
        # Check if blank line after table is needed
        insert_after = False
        if last_idx < len(lines) - 1:
            next_line = lines[last_idx + 1].strip()
            if next_line != "" and next_line != blank_line_val.strip() and not next_line.startswith('---'):
                insert_after = True
                
        table_content_changed = lines[header_idx:last_idx+1] != new_rows
        
        if table_content_changed or insert_before or insert_after:
            modified = True
            table_block = []
            if insert_before:
                table_block.append(blank_line_val)
            table_block.extend(new_rows)
            if insert_after:
                table_block.append(blank_line_val)
                
            lines[header_idx:last_idx+1] = table_block
            
    return '\n'.join(lines) + '\n', modified

def fix_md032(body):
    lines = body.splitlines()
    modified = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('```'):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
            
        # Matches list items (ordered or unordered, optionally with blockquote prefix)
        is_list_item = bool(re.match(r'^\s*(?:>\s*)?(?:[-*+]|\d+\.)\s', line))
        
        if is_list_item:
            start_idx = i
            end_idx = i
            while end_idx + 1 < len(lines):
                next_line = lines[end_idx + 1]
                if re.match(r'^\s*(?:>\s*)?(?:[-*+]|\d+\.)\s', next_line):
                    end_idx += 1
                else:
                    break
                    
            bq_match = re.match(r'^\s*(>\s*)', lines[start_idx])
            bq_prefix = bq_match.group(1).rstrip() + " " if bq_match else ""
            blank_line_val = bq_prefix.rstrip()
            
            # Check before
            insert_before = False
            if start_idx > 0:
                prev_line = lines[start_idx - 1].strip()
                if (prev_line != "" and 
                    prev_line != blank_line_val.strip() and 
                    not prev_line.startswith('---') and
                    not prev_line.startswith('<!-- -->')):
                    insert_before = True
                    
            # Check after
            insert_after = False
            if end_idx < len(lines) - 1:
                next_line = lines[end_idx + 1].strip()
                if (next_line != "" and 
                    next_line != blank_line_val.strip() and 
                    not next_line.startswith('---') and
                    not next_line.startswith('<!-- -->')):
                    insert_after = True
                    
            if insert_before or insert_after:
                modified = True
                new_block = []
                if insert_before:
                    new_block.append(blank_line_val)
                new_block.extend(lines[start_idx:end_idx+1])
                if insert_after:
                    new_block.append(blank_line_val)
                    
                lines[start_idx:end_idx+1] = new_block
                
                inserted_count = (1 if insert_before else 0) + (1 if insert_after else 0)
                i = end_idx + 1 + inserted_count
                continue
                
            i = end_idx + 1
        else:
            i += 1
            
    return '\n'.join(lines) + '\n', modified

def process_file(filepath: Path):
    content = filepath.read_text(encoding="utf-8")
    original = content
    
    # 1. Fix double frontmatter first
    content, d_fm = fix_double_frontmatter(content)
    
    # 2. Parse frontmatter to isolate the body
    fm, body = parse_frontmatter(content)
    
    if fm is not None:
        # Run diagnostics only on the body
        body, d_028 = fix_md028(body)
        body, d_009 = fix_md009(body)
        body, d_tbl = fix_tables(body)
        body, d_032 = fix_md032(body)
        content = fm + body
    else:
        content, d_028 = fix_md028(content)
        content, d_009 = fix_md009(content)
        content, d_tbl = fix_tables(content)
        content, d_032 = fix_md032(content)
        
    if content != original:
        filepath.write_text(content, encoding="utf-8")
        changes = []
        if d_fm: changes.append("double_frontmatter")
        if d_028: changes.append("MD028")
        if d_009: changes.append("MD009")
        if d_tbl: changes.append("tables(MD060/MD058)")
        if d_032: changes.append("lists(MD032)")
        print(f"Fixed {filepath.name}: {', '.join(changes)}")
        return True
    return False

def main():
    if not VAULT_DIR.exists():
        print(f"Error: vault dir not found at {VAULT_DIR}")
        return
        
    print(f"Scanning markdown files in {VAULT_DIR}...")
    files = list(VAULT_DIR.rglob("*.md"))
    modified_count = 0
    for f in files:
        if process_file(f):
            modified_count += 1
            
    print(f"\nDone. Modified {modified_count} out of {len(files)} files.")

if __name__ == "__main__":
    main()
