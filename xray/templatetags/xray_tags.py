from string import ascii_lowercase

from django import template
register = template.Library()

letters = [l.upper() for l in ascii_lowercase]

def alphabet(index):
   return letters[index]

register.filter('alphabet', alphabet)
