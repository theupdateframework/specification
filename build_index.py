#!/usr/bin/env python3

"""
<Program Name>
  build_index.py

<Author>
  Joshua Lock

<Started>
  Feb 1, 2021

<Copyright>
  See LICENSE-MIT for licensing information.

<Purpose>
  Quick and dirty script to generate an index of published specification
  versions.

  Style cribbed from the bikeshed W3C theme we are using in our bikeshed
  generated specification documents.
"""

import os
import sys

from subprocess import run

html_header = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>The Update Framework Specification</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <style data-fill-with="stylesheet">
  body {
    counter-reset: example figure issue;

    /* Layout */
    max-width: 50em;			  /* limit line length to 50em for readability   */
    margin: 0 auto;				/* center text within page                    */
    padding: 1.6em 1.5em 2em 50px; /* assume 16px font size for downlevel clients */
    padding: 1.6em 1.5em 2em calc(26px + 1.5em); /* leave space for status flag    */

    /* Typography */
    line-height: 1.5;
    font-family: sans-serif;
    widows: 2;
    orphans: 2;
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;

    color: black;
    color: var(--text);
    background: white top left fixed no-repeat;
    background: var(--bg) top left fixed no-repeat;
    background-size: 25px auto;
  }
  div.head { margin-bottom: 1em; }
  div.head h1 {
      font-weight: bold;
      margin: 0 0 .1em;
      font-size: 220%;
  }

  p {
      margin: 1em 0;
  }

  dd > p:first-child,
  li > p:first-child {
      margin-top: 0;
  }

  ul, ol {
      margin-left: 0;
      padding-left: 2em;
  }

  li {
      margin: 0.25em 0 0.5em;
      padding: 0;
  }

  a {
      color: #034575;
      color: var(--a-normal-text);
      text-decoration: none;
      border-bottom: 1px solid #707070;
      border-bottom: 1px solid var(--a-normal-underline);
      /* Need a bit of extending for it to look okay */
      padding: 0 1px 0;
      margin: 0 -1px 0;
  }
  a:visited {
      color: #034575;
      color: var(--a-visited-text);
      border-bottom-color: #bbb;
      border-bottom-color: var(--a-visited-underline);
  }

  a:focus,
  a:hover {
      background: #f8f8f8;
      background: rgba(75%, 75%, 75%, .25);
      background: var(--a-hover-bg);
      border-bottom-width: 3px;
      margin-bottom: -2px;
  }
  a:active {
      color: #c00;
      color: var(--a-active-text);
      border-color: #c00;
      border-color: var(--a-active-underline);
  }

  h1, h2, h3, h4, h5, h6, dt {
      page-break-after: avoid;
      page-break-inside: avoid;
      font: 100% sans-serif;   /* Reset all font styling to clear out UA styles */
      font-family: inherit;	/* Inherit the font family. */
      line-height: 1.2;		/* Keep wrapped headings compact */
      hyphens: manual;		/* Hyphenated headings look weird */
  }
  h2, h3, h4, h5, h6 {
      margin-top: 3rem;
  }
  h1, h2, h3 {
      color: #005A9C;
      color: var(--heading-text);
  }
  h1 { font-size: 170%; }
  h2 { font-size: 140%; }

  :root {
    color-scheme: light dark;

    --text: black;
    --bg: white;

    --heading-text: #005a9c;

    --a-normal-text: #034575;
    --a-normal-underline: #707070;
    --a-visited-text: var(--a-normal-text);
    --a-visited-underline: #bbb;
    --a-hover-bg: rgba(75%, 75%, 75%, .25);
    --a-active-text: #c00;
    --a-active-underline: #c00;
  }
  </style>
</head>
<body class="h-entry">
<div class="head">
  <h1 id="title" class="p-name no-ref">The Update Framework Specification</h1>
</div>
<div>
<ul>
"""

html_footer = """</ul>
</body>
</html>
"""

def build_index():
    html = html_header

    html_locations = ['latest', 'draft']
    dir_contents = sorted(os.listdir('.'), reverse=True)
    for path in dir_contents:
        if path.startswith('v'):
            if not os.path.exists(f'{path}/index.html'):
                continue
            html_locations.append(path)

    for loc in html_locations:
        link = f"  <li><a href='{loc}/index.html'>{loc}</a></li>\n"
        html = html + link

    html = html + html_footer

    return html

if __name__ == "__main__":
    html = build_index()
    with open('index.html', 'w') as index:
        index.write(html)
