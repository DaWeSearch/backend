"""Instantiate an array containing all available wrapper classes."""
from .elsevier_wrapper import ElsevierWrapper
from .springer_wrapper import SpringerWrapper

ALL_WRAPPERS = [ElsevierWrapper, SpringerWrapper]
