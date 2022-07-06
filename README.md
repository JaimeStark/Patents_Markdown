# U.S. Patents Markdown Note

Created by Jaime Stark on 1/30/2021

This script comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to
redistribute it under certain conditions.
See 'LICENSE.txt' for details.

## Description
This script generates a summary of a U.S. Patent or Patent Publication
in markdown format based only on the patent or publication number.
The script is intended for easy input into a markdown-based
notetaking program like [Obsidian](https://obsidian.md).

The resulting Patent Term Adjustment, Terminal Disclaimer, and
Prosecution History PDF fields have placeholders that are intended to 
be edited manually.

Requires installation of BeautifulSoup4 python package.  To install 
BeautifulSoup4 in python3, type:
`pip3 install BeautifulSoup4`

## Usage
`python3 uspatentmd PATENT_NUMBER > FILENAME.md`
