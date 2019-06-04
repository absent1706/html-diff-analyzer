"""
CLI tool for finding tags in sample files
  which are most similar to tag with given id in origin file.

Usage example:
    python html-diff-analyzer.py demo-files/sample-0-origin.html demo-files/sample-2-container-and-clone.html
"""
import argparse
import sys
import os
from bs4 import BeautifulSoup
from collections import OrderedDict


def _get_attibutes_to_match(origin_tag):
    """
    Form dict of {attribute: value} pairs
    Example: {'id': 'make-everything-ok-button',
            'class': 'btn btn-success',
            'href': '#ok',
            'title': 'Make-Button',
            'rel': 'next',
            'onclick': 'javascript:window.okDone(); return false;'}
    """
    attributes_to_match = {}
    for attr, value in origin_tag.attrs.items():
        # for 'class' attribute BeautifulSoup returns list,
        #   so convert it to string
        if type(value) == list:
            value = ' '.join(value)
        attributes_to_match[attr] = value
    return attributes_to_match


def _find_origin_tag(origin_html, origin_tag_id):
    """
    find origin tag by id
    """
    tags = origin_html.select('#'+origin_tag_id)
    # if element not found - raise exception
    if len(tags) == 0:
        raise ValueError(f'HTML doesnt contain tag with id = {origin_tag_id}')
    return tags[0]


def _find_tag_by_text(html, text):
    """
    Find tag containing given text

    In BeautifulSoup, 'text' propery holds text of all child elements,
      so all parents of actual element will be returned
      (beginning with <html> tag)
    That's why we take last element
    """
    tags = html.find_all(lambda tag: text in tag.text)

    # Return list just for simplicity of usage in current program.
    # In real world, its better to return None or just tag
    return [] if len(tags) == 0 else [tags[-1]]


def _get_matches_by_selector(sample_html, attributes_to_match, text_to_match):
    """
    Find tags from sample_html that match 'attributes_to_match' param

    Example of returned value:
        {
            'id="make-everything-ok-button"': [],
            'class="btn btn-success"': [<TAG1>],
            'href="#ok"': [<TAG1>, <TAG2>],
         }
    """
    matches_by_selector = {}
    for attr, value in attributes_to_match.items():
        # form CSS selectors like [title="Make=Button"] and match tags by them
        selector = f'{attr}="{value}"'
        matches_by_selector[selector] = sample_html.select(f'[{selector}]')

    # 'text="something"' is specific "CSS-selector" matched in a different way
    matches_by_selector[f'text="{text_to_match}"'] = \
        _find_tag_by_text(sample_html, text_to_match)
    return matches_by_selector


def _get_matches_by_tag(matches_by_selector):
    """
    'Inverts' the result of 'get_matches_by_selector' function:
      returns dict like {tag: [all, selectors, tag, matched, to]}

    Example output:
        {
            <TAG1>: ['href="#ok"', 'title="Make-Button"', 'rel="next"'],
            <TAG2>: ['title="Make-Button"', 'text="Make everything OK"']
        }
    """
    # Form set of unique tags matched in document.
    # There should be a better way to get it,
    #  but let it be as it is for the sake of time
    temp_all_matched_tags = []
    for v in matches_by_selector.values():
        temp_all_matched_tags.extend(v)
    all_matched_tags = set(temp_all_matched_tags)

    # For dict of needed form.
    matches_by_tag = {}
    for tag in all_matched_tags:
        matched_selectors = [s for s in matches_by_selector.keys()
                             if tag in matches_by_selector[s]]
        matches_by_tag[tag] = matched_selectors
    return matches_by_tag


def get_best_match(origin_file, sample_file, origin_tag_id):
    # TODO: validate that file exists
    # Step 1.
    # Load origin file, origin tag, extract attributes from it
    if not os.path.isfile(origin_file):
        raise ValueError('Origin file doesnt exist')
    if not os.path.isfile(sample_file):
        raise ValueError('Sample file doesnt exist')

    with open(origin_file) as f:
        origin_html = BeautifulSoup(f, 'html.parser')

    origin_tag = _find_origin_tag(origin_html, origin_tag_id)
    attributes_to_match = _get_attibutes_to_match(origin_tag)
    text_to_match = origin_tag.text.strip()  # get text inside of tag

    # Step 2.
    # Open sample file and match tags
    with open(sample_file) as f:
        sample_html = BeautifulSoup(f, 'html.parser')

    matches_by_selector = _get_matches_by_selector(
        sample_html, attributes_to_match, text_to_match)
    matches_by_tag = _get_matches_by_tag(matches_by_selector)

    # Step 3.
    # Find tag with maximum number of matched selectors
    best_tag = max(matches_by_tag, key=lambda tag: len(matches_by_tag[tag]))
    return best_tag, matches_by_tag


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('origin_file')
        parser.add_argument('sample_file')
        parser.add_argument('--id', help='ID of origin HTML tag',
                            default='make-everything-ok-button')
        args = parser.parse_args()

        origin_file = args.origin_file
        sample_file = args.sample_file
        origin_tag_id = args.id

        best_tag, matches_per_tag = get_best_match(origin_file, sample_file, origin_tag_id)
        print()
        print('The most similar tag in sample file is\n'
              f'\n{best_tag}\n\n'
              f'It has {len(matches_per_tag[best_tag])} attributes in common with origin tag.\n'
              'These attributes are: \n'
              f'{matches_per_tag[best_tag]}')

    except Exception as e:
        # TODO: maybe, exception should be somehow handled.
        # For now, don't handle it, just re-raise
        raise
