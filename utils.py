import re
from typing import List, Tuple, Dict, Optional

SourceCode = str

class Range:
  ''' Line range from a to b includes a and b and start from zero'''
  def __init__(self, start: int, end: int = None):
    self._start = start
    self._end = end or start
    assert self._start <= self._end

  @property
  def start(self) -> int:
    return self._start

  @property
  def end(self) -> int:
    return self._end

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return f'[{self._start},{self._end}]'

  def __eq__(self, other: 'Range'):
    return self._start == other._start and self._end == other._end

  def contains(self, range: 'Range') -> bool:
    return self._start <= range.start and self._end >= range.end

def remove_comments(string: SourceCode) -> SourceCode:
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
    def _replacer(match):
        if match.group(2) is not None:
            return ""
        else:
            return match.group(1)
    return regex.sub(_replacer, string)

def extract_lines_range_to_file(filename_in: str, filename_out: str, range: Range) -> None:
  lines = extract_lines_range_from_file(filename_in, range)
  write_lines_to_file(lines, filename_out)

def extract_lines_range_from_file(filename: str, range: Range) -> List[str]:
  source_code = get_source_code(filename)
  return extract_lines_range_from_source_code(source_code, range)

def extract_lines_range_from_source_code(code: SourceCode, range: Range) -> List[str]:
  ''' Line Range from a to b includes a and b and start indexing from zero'''
  return code.split('\n')[range.start: range.end + 1]

def complement_range(class_source: SourceCode, line_range: Range) -> Range:
  open_brackets   = 0
  closed_brackets = 0
  n_line = 0
  has_semicolon = False
  source_code_lines = class_source.split('\n')
  # assert remove_comments(source_code_lines[line_range.start]).count('}') == 0

  for n_line, line in enumerate(source_code_lines[line_range.start: ]):
    line_without_comments = remove_comments(line)
    has_semicolon = line_without_comments.count(';') > 0
    open_brackets += line_without_comments.count('{')
    closed_brackets += line_without_comments.count('}')
 
    if line_range.start + n_line < line_range.end: 
      if open_brackets - closed_brackets == 0:
        open_brackets   = 0
        closed_brackets = 0
      continue
    if closed_brackets == 0 and open_brackets == 0 and not has_semicolon: 
      continue
    if open_brackets - closed_brackets == 0:
      break
  
  result = Range(line_range.start, line_range.start + n_line)
  #assert result.contains(line_range)
  return result

def extract_method(class_source: SourceCode, method_name: str, method_start_line: int) -> SourceCode:
  assert method_name in class_source.split('\n')[method_start_line - 1]
  if '{' in class_source.split('\n')[method_start_line - 1]:
    range = complement_range(class_source, Range(method_start_line - 1))
  else:
     range = complement_range(class_source, Range(method_start_line - 1, method_start_line + 1))
  method_lines = extract_lines_range_from_source_code(class_source, range)
  return '\n'.join(method_lines)


def get_source_code(filename: str) -> SourceCode:
  with open(filename, 'r') as file:
    data = file.read()
  return data

def gen_emo_filename(java_file_name: str, method_name: str, range: Range) -> str:
  file_name = re.sub('\.java', '',  java_file_name)
  return f'{file_name}_{method_name.lower()}_{range.start}_{range.end}.java'


def write_lines_to_file(lines: List[str], filename: str) -> None:
  with open(filename, 'w') as f:
    for l in lines:
      f.write(l + '\n')
