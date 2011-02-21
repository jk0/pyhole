#!/bin/sh

echo "Running PEP8..."
pep8 -r .

echo "Running pylint..."
pylint pyhole.py -rno
pylint pyhole -rno
pylint plugins -rno

echo "Running pyflakes..."
pyflakes .

echo "Running unit tests..."
# Coming soon
