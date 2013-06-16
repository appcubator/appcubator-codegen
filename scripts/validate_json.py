#!/usr/bin/python

from app_builder.analyzer import App
import sys

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print >> sys.stdout, "Give the path to a json file"
        sys.exit(1)

    app_state = simplejson.load(open(args[1], 'r'))
    app = App.create_from_dict(app_state)

