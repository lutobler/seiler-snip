#!/usr/bin/env python3

import json
import argparse
import sys
import subprocess
import pyautogui

class Snippet():
    """A text snippet."""

    def __init__(self, keyword, cmd):
        self.keyword = keyword
        self.cmd = cmd

    def to_json(self):
        """Convert to json string."""
        return { 'keyword': self.keyword, 'cmd': self.cmd } 

class SnippetCollection:
    """A collection of text snippets."""

    def __init__(self):
        self.snippets = []

    @staticmethod
    def from_json(json_string):
        """Build a SnippetCollection class from a JSON string."""
        j = json.loads(json_string)
        sc = SnippetCollection()
        sc.snippets = [ Snippet(x['keyword'], x['cmd']) for x in j ]
        return sc

    def to_json(self):
        """Convert to json string."""
        return json.dumps([
            x for x in map(lambda x: x.to_json, self.snippets)
            ])

    def __has_snippet(self, keyword):
        """Check if a snippet with the given keyword is in the collection."""
        return keyword in map(lambda x: x.keyword, self.snippets)

    def add_snippet(self, snippet):
        """Add a snippet to the collection."""
        if not self.__has_snippet(snippet.keyword):
            self.snippets.append(snippet)

    def to_shell_list(self):
        """Build a newline-separated list of snippet keywords."""
        return '\n'.join(map(lambda x: x.keyword, self.snippets))

    def get_snippet(self, keyword):
        """Get a snippet for a given keyword."""
        try:
            return next(x for x in self.snippets if x.keyword == keyword)
        except:
            return None


def main():
    snippets_file = 'snippet_collection.json' #default

    parser = argparse.ArgumentParser()
    parser.add_argument('--snippets', dest='snippets_file')
    args = parser.parse_args()

    if args.snippets_file:
        snippets_file = args.snippets_file

    sc = None
    with open(snippets_file, 'r') as f:
        sc = SnippetCollection.from_json(f.read())

    if not sc:
        print('failed to read snippet collection file')
        sys.exit(1)

    snippet_keywords = sc.to_shell_list()
    selection = subprocess.run(
            ['sh', '-c', f'printf "{snippet_keywords}" | rofi -dmenu'],
            stdout=subprocess.PIPE)

    sel_keyword = selection.stdout.decode('utf-8').strip()

    snip = sc.get_snippet(sel_keyword)
    if not snip:
        sys.exit(0)

    cmd = snip.cmd
    pyautogui.typewrite(cmd, interval=0.01)


if __name__ == '__main__':
    main()

