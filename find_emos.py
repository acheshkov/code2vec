from pathlib import Path
from typing import List, Tuple, Union
from utils import get_source_code, Range, complement_range

from veniq.baselines.semi.extract_semantic import extract_method_statements_semantic
from veniq.baselines.semi.filter_extraction_opportunities import filter_extraction_opportunities
from veniq.baselines.semi.alternatives.all_opportunities.create_all_opportunities import (
            create_extraction_opportunities,
)
from veniq.ast_framework import AST, ASTNodeType
from veniq.ast_framework.block_statement_graph import Block, Statement, build_block_statement_graph
from veniq.baselines.semi._common_types import (
            ExtractionOpportunity,
                Statement as ExtractionStatement,
                    StatementSemantic,
                    )
from veniq.utils.ast_builder import build_ast

def get_method_ast(filename: str, class_name: str, method_name: str, method_decl_line: int) -> AST:
    ast = AST.build_from_javalang(build_ast(str(filename)))

    try:
        class_declaration = next(
            node
            for node in ast.get_root().types
            if node.node_type == ASTNodeType.CLASS_DECLARATION and node.name == class_name
        )
        method_declaration = next(node for node in class_declaration.methods if node.name == method_name and node.line == method_decl_line)
    except StopIteration:
        raise RuntimeError(f"Failed to find method {method_name} in class {class_name} in file {filepath}")

    return ast.get_subtree(method_declaration)


def count_all_class_declarations(filename: str) -> int:
  ast = AST.build_from_javalang(build_ast(str(filename)))
  return len(list(ast.get_proxy_nodes(ASTNodeType.CLASS_DECLARATION)))


def find_emos(filename: str, class_name: str, method_name: str, method_decl_line: int) -> List[Range]:
  ast_method = get_method_ast(filename, class_name, method_name, method_decl_line)
  statements_semantic = extract_method_statements_semantic(ast_method)
  possible_extraction_opportunities = create_extraction_opportunities(statements_semantic)
  filtered_extraction_opportunities = filter_extraction_opportunities(
      possible_extraction_opportunities, statements_semantic, ast_method
  )

  source_code = get_source_code(filename)
  results = []
  for index, extraction_opportunity in enumerate(filtered_extraction_opportunities):
      first_statement = extraction_opportunity[0]
      last_statement = extraction_opportunity[-1]
      range = complement_range(source_code, Range(first_statement.line-1, last_statement.line-1))
      results.append(range)

  return results