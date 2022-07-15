from typing import Any

class RustDecl():

    def __init__(self, tokens, trait=None) -> None:
        self.tokens = tokens
        self.trait = trait
    

class NameToken():

    def __init__(self, name, generic=None):
        self.name = name
        self.generic = generic

class Trait():

    def __init__(self, impl_trait, impl_class=None) -> None:
        self.impl_trait = impl_trait
        self.impl_class = impl_class


class GenericParams():

    def __init__(self, T_list, a_list):
        self.T_list = T_list
        self.a_list = a_list

    def dict(self):
        return {
            'Generic Params': self.a_list + self.T_list
        }
