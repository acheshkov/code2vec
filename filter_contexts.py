import random
from argparse import ArgumentParser
import pickle
from typing import List, Tuple, Dict, Optional, Any


MethodNameCode2Vec = str
MethodContext = str
MethodBodyBagOfContexts = List[MethodContext]
MethodCode2Vec = Tuple[MethodNameCode2Vec, MethodBodyBagOfContexts]
MethodBody = str
CodeVector = List[float]
JavaClassPath = str
MethodName = str

'''
Filter extracted contexts and format output for future steps. 
'''

def load_dictionaries(dict_path: str):
    with open(dict_path, 'rb') as file:
        word_to_count = pickle.load(file)
        path_to_count = pickle.load(file)

    return word_to_count, path_to_count


def read_contexts_from_file(filename: str) -> List[MethodCode2Vec]:
    methods = []
    with open(args.input_name, 'r') as file:
        for line in file:
            parts = line.rstrip('\n').split(' ')
            methods.append((parts[0], parts[1: ]))
    return methods

def write_contexts_to_file(methods: List[MethodCode2Vec], filename: str) -> None:
    lines = [' '.join([method_name] + contexts) + '\n' for method_name, contexts in methods]
    with open(args.output_name, 'w') as f:
        for l in lines:
            f.write(l)

def main(args):
    word_to_count, path_to_count = load_dictionaries(args.dict_path)
    methods = read_contexts_from_file(args.input_name)
    methods_filtered = filter_context(methods, word_to_count, path_to_count, args.max_contexts)
    write_contexts_to_file(methods_filtered, args.output_name)
    

def filter_context(
    methods: List[MethodCode2Vec], 
    word_to_count: Dict[Any, int], 
    path_to_count: Dict[Any, int], 
    max_contexts=200
) -> List[MethodCode2Vec]:
    result = []
    for method_name, contexts in methods:
        if len(contexts) > max_contexts:
            context_parts = [c.split(',') for c in contexts]
            full_found_contexts, partial_found_contexts = get_c
            full_found_contexts = [
                c for i, c in enumerate(contexts)
                if context_full_found(context_parts[i], word_to_count, path_to_count)
            ]
            partial_found_contexts = [
                c for i, c in enumerate(contexts)
                if context_partial_found(context_parts[i], word_to_count, path_to_count)
                and not context_full_found(context_parts[i], word_to_count, path_to_count)
            ]
            contexts = sample_full_and_partial_context(full_found_contexts, partial_found_contexts, max_contexts)
            
        if len(contexts) == 0:
            result.append((method_name, []))
            continue

        csv_padding = [''] * (max_contexts - len(contexts))
        result.append((method_name, contexts + csv_padding))
    return result

def sample_full_and_partial_context(full_found_contexts, partial_found_contexts, max_contexts):
    contexts = []
    if len(full_found_contexts) > max_contexts:
        contexts = random.sample(full_found_contexts, max_contexts)
    elif len(full_found_contexts) <= max_contexts \
            and len(full_found_contexts) + len(partial_found_contexts) > max_contexts:
        contexts = full_found_contexts + \
                    random.sample(partial_found_contexts, max_contexts - len(full_found_contexts))
    else:
        contexts = full_found_contexts + partial_found_contexts
    return contexts

# def only_full_contexts(
#     contexts: MethodBodyBagOfContexts, 
#     word_to_count: Dict[Any, int], 
#     path_to_count: Dict[Any, int]
# ) -> MethodBodyBagOfContexts:
#     def _predicate(parts, word_to_count: Dict[Any, int], path_to_count: Dict[Any, int]) -> bool:
#         return parts[0] in word_to_count and parts[1] in path_to_count and parts[2] in word_to_count

#     context_parts = [c.split(',') for c in contexts]
#     return  [
#         c for i, c in enumerate(contexts)
#         if _predicate(context_parts[i], word_to_count, path_to_count)
#     ]


def context_full_found(context_parts, word_to_count: Dict[Any, int], path_to_count: Dict[Any, int]) -> bool:
    return context_parts[0] in word_to_count \
           and context_parts[1] in path_to_count and context_parts[2] in word_to_count


def context_partial_found(context_parts, word_to_count, path_to_count) -> bool:
    return context_parts[0] in word_to_count \
           or context_parts[1] in path_to_count or context_parts[2] in word_to_count


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-mc", "--max_contexts", dest="max_contexts", default=200,
        help="number of max contexts to keep", required=False)
    parser.add_argument(
        "-dp", "--dict_path", dest="dict_path",
        help="dump file with dictionaries", metavar="FILE",
        required=True
    )
    parser.add_argument(
        "-i", "--input_name", dest="input_name",
        help="output name - the base name for the created dataset",
        metavar="FILE",
        required=True,
    )
    parser.add_argument(
        "-o", "--output_name", dest="output_name",
        help="output name - the base name for the created dataset", metavar="FILE",
        required=True,
        default='data'
    )
    args = parser.parse_args()
    main(args)
