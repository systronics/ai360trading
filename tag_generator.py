#!/usr/bin/env python

'''
tag_generator.py
Optimized for ai360trading (2026)
Purpose: Manually triggers the creation of professional tag archive pages.
'''

import glob
import os

post_dir = '_posts/'
tag_dir = 'tag/'

# 1. Identify all post files (.md and .html)
filenames = glob.glob(post_dir + '*.*')

total_tags = []

# 2. Extract tags from Front Matter
for filename in filenames:
    with open(filename, 'r', encoding='utf8') as f:
        crawl = False
        for line in f:
            if line.strip() == '---':
                if not crawl:
                    crawl = True
                    continue
                else:
                    break
            if crawl:
                # Look for the tags: line
                if line.startswith('tags:'):
                    # Clean the line: remove brackets, commas, and the 'tags:' prefix
                    tag_line = line.replace('tags:', '').replace('[', '').replace(']', '').replace(',', '').strip()
                    parts = tag_line.split()
                    total_tags.extend(parts)

# Remove duplicates
total_tags = set(total_tags)

# 3. Clean up old tags safely to ensure no dead pages
if not os.path.exists(tag_dir):
    os.makedirs(tag_dir)
else:
    old_tags = glob.glob(tag_dir + '*.md')
    for tag_file in old_tags:
        os.remove(tag_file)

# 4. Generate professional Tag Pages
for tag in total_tags:
    # Human-friendly formatting (e.g., price-action -> Price Action)
    display_name = tag.replace('-', ' ').replace('_', ' ').title()
    
    tag_filename = tag_dir + tag + '.md'
    with open(tag_filename, 'w', encoding='utf8') as f:
        write_str = (
            '---\n'
            'layout: tagpage\n'
            'title: "Archive: ' + display_name + '"\n'
            'tag: ' + tag + '\n'
            'robots: noindex\n'
            'excerpt: "Explore all manually curated research, signals, and insights related to ' + display_name + '."\n'
            'permalink: /tag/' + tag + '/\n'
            '---\n'
        )
        f.write(write_str)

print(f"✅ Success: {len(total_tags)} professional tag hubs generated in /{tag_dir}")
