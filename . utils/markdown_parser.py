# utils/markdown_parser.py
import re
from typing import Dict, List, Any

class MarkdownParser:
    def __init__(self, parse_tables=True, parse_code=True, parse_lists=True):
        self.parse_tables = parse_tables
        self.parse_code = parse_code
        self.parse_lists = parse_lists
        
    def parse(self, markdown_text: str) -> Dict[str, Any]:
        """Parse markdown text and return structured data"""
        lines = markdown_text.split('\n')
        structure = []
        stats = {
            'headers': 0,
            'tables': 0,
            'code_blocks': 0,
            'lists': 0,
            'blockquotes': 0,
            'paragraphs': 0
        }
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Parse headers
            if line.startswith('#'):
                header_data = self._parse_header(line)
                if header_data:
                    structure.append(header_data)
                    stats['headers'] += 1
                i += 1
                
            # Parse code blocks
            elif line.startswith('```') and self.parse_code:
                code_data, lines_consumed = self._parse_code_block(lines[i:])
                if code_data:
                    structure.append(code_data)
                    stats['code_blocks'] += 1
                i += lines_consumed
                
            # Parse tables
            elif '|' in line and self.parse_tables:
                table_data, lines_consumed = self._parse_table(lines[i:])
                if table_data:
                    structure.append(table_data)
                    stats['tables'] += 1
                    i += lines_consumed
                else:
                    i += 1
                    
            # Parse lists
            elif (line.strip().startswith(('-', '*', '+')) or 
                  re.match(r'^\d+\.', line.strip())) and self.parse_lists:
                list_data, lines_consumed = self._parse_list(lines[i:])
                if list_data:
                    structure.append(list_data)
                    stats['lists'] += 1
                i += lines_consumed
                
            # Parse blockquotes
            elif line.startswith('>'):
                quote_data = self._parse_blockquote(line)
                if quote_data:
                    structure.append(quote_data)
                    stats['blockquotes'] += 1
                i += 1
                
            # Parse paragraphs
            elif line.strip():
                para_data = self._parse_paragraph(line)
                if para_data:
                    structure.append(para_data)
                    stats['paragraphs'] += 1
                i += 1
            else:
                i += 1
        
        return {
            'structure': structure,
            'stats': stats,
            'metadata': {
                'total_elements': len(structure),
                'has_tables': stats['tables'] > 0,
                'has_code': stats['code_blocks'] > 0,
                'has_lists': stats['lists'] > 0
            }
        }
    
    def _parse_header(self, line: str) -> Dict[str, Any]:
        """Parse header line"""
        match = re.match(r'^(#+)\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            content = match.group(2)
            return {
                'type': 'header',
                'level': level,
                'content': content,
                'raw': line
            }
        return None
    
    def _parse_code_block(self, lines: List[str]) -> tuple:
        """Parse code block"""
        if not lines[0].startswith('```'):
            return None, 1
            
        language = lines[0][3:].strip()
        code_lines = []
        
        for i in range(1, len(lines)):
            if lines[i].startswith('```'):
                return {
                    'type': 'code',
                    'language': language or 'plaintext',
                    'content': '\n'.join(code_lines),
                    'raw': '\n'.join(lines[:i+1])
                }, i + 1
            code_lines.append(lines[i])
        
        return None, 1
    
    def _parse_table(self, lines: List[str]) -> tuple:
        """Parse markdown table"""
        if '|' not in lines[0]:
            return None, 1
            
        table_lines = []
        for i, line in enumerate(lines):
            if '|' in line:
                table_lines.append(line)
            else:
                break
        
        if len(table_lines) < 2:
            return None, 1
        
        # Parse table structure
        headers = [cell.strip() for cell in table_lines[0].split('|') if cell.strip()]
        rows = []
        
        for line in table_lines[2:]:  # Skip separator line
            if '|' in line:
                row = [cell.strip() for cell in line.split('|') if cell.strip()]
                if row:
                    rows.append(row)
        
        if headers:
            return {
                'type': 'table',
                'headers': headers,
                'rows': rows,
                'content': f"Table with {len(headers)} columns and {len(rows)} rows",
                'raw': '\n'.join(table_lines)
            }, len(table_lines)
        
        return None, 1
    
    def _parse_list(self, lines: List[str]) -> tuple:
        """Parse list items"""
        list_items = []
        i = 0
        
        for line in lines:
            if re.match(r'^[\s]*[-*+]\s+', line) or re.match(r'^[\s]*\d+\.\s+', line):
                # Extract list item content
                content = re.sub(r'^[\s]*[-*+]\s+', '', line)
                content = re.sub(r'^[\s]*\d+\.\s+', '', content)
                list_items.append(content.strip())
                i += 1
            elif not line.strip():
                break
            else:
                break
        
        if list_items:
            return {
                'type': 'list',
                'items': list_items,
                'content': f"List with {len(list_items)} items",
                'raw': '\n'.join(lines[:i])
            }, i
        
        return None, 1
    
    def _parse_blockquote(self, line: str) -> Dict[str, Any]:
        """Parse blockquote"""
        if line.startswith('>'):
            content = line[1:].strip()
            return {
                'type': 'blockquote',
                'content': content,
                'raw': line
            }
        return None
    
    def _parse_paragraph(self, line: str) -> Dict[str, Any]:
        """Parse regular paragraph"""
        if line.strip():
            return {
                'type': 'paragraph',
                'content': line.strip(),
                'raw': line
            }
        return None