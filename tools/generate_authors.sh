#!/bin/sh

git log --pretty=format:"%an <%ae>" | sort -u > AUTHORS
