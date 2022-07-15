import json
import logging

from lark import Lark,  Transformer, logger, tree

from general_utils.name import *


class NameParser():

    def __init__(self):
        self.parser = Lark(r"""
            decl: (("<" trait_decl ">") | outer_token ) ("::" outer_token)*
            trait_decl: (class " as " trait) | (trait " for " class)
            outer_token: ("<impl " impl_block ">") | ("<" annotation ("," annotation)* ">") | NAME
            impl_block: class | trait_decl
            annotation: class | GENERIC | LIFETIME
            trait: token ("::" token)*
            NAME: /[a-zA-z][a-zA-z0-9_]*/
            class: token ("::" token)*
            GENERIC: /&?[A-Z][0-9]*/ 
            LIFETIME: /&?\'[a-z_]/
            token: NAME ("<" annotation ("," annotation)* ">")?

            %import common.WS
            %ignore WS
            """, start='decl'
                           )
        self.transformer = NameTransformer()

    def parse(self, s: str) -> RustDecl:
        return self.parser.parse(s)


        # return self.transformer.transform(self.parser.parse(s))


class NameTransformer(Transformer):
    def decl(self, items):
        if isinstance(items[0], NameToken):
            return RustDecl(tokens=items)
        return RustDecl(tokens=items[1:], trait=items[0])

    def trait(self, items):
        return list(items)

    def name(self, item):
        return item[0].value

    def token(self, items):
        return NameToken(items[0], generic=items[1] if len(items) > 1 else None)

    def generic(self, items):
        return list(items)

    def generic_param(self, items):
        d = {'T': [], 'a': []}
        for item in items:
            for k, v in item.items():
                d[k].append(v)
        return GenericParams(T_list=d['T'], a_list=d['a'])
    
    def a(self, item):
        print(type(item), item)
        return {item.type: item.value}
    
    def T(self, item):
        return {item.type: item.value}



logger.setLevel(logging.INFO)
parser = NameParser()

