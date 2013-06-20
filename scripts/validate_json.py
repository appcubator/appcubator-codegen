#!/usr/bin/python

from test_runner import parse_app_state, create_app
import sys

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print "Usage: python validate_json.py <path_to_json>"
        sys.exit(1)
    app_state = parse_app_state(args[1])
    app = create_app(app_state)

    
