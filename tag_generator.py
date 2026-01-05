#!/usr/bin/env python

'''
tag_generator.py
Optimized for ai360trading (2026)
'''

import glob
import os

post_dir = '_posts/'
tag_dir = 'tag/'

# Support both .md and .html posts
filenames = glob.glob(post_dir + '*.*')

total_tags = []
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
                    # Handles both "tags: tag1 tag2" and "tags: [tag1, tag2]"
                    parts = line.replace('[', '').replace(']', '').replace(',', '').strip().split()
                    total_tags.extend(parts[1:])

total_tags = set(total_tags)

# Clean up old tags safely
if not os.path.exists(tag_dir):
    os.makedirs(tag_dir)
else:
    old_tags = glob.glob(tag_dir + '*.md')
    for tag in old_tags:
        os.remove(tag)

for tag in total_tags:
    tag_filename = tag_dir + tag + '.md'
    with open(tag_filename, 'w') as f:
        # Professional Front Matter Generation
        write_str = (
            '---\n'
            'layout: tagpage\n'
            'title: "' + tag.replace('-', ' ').title() + '"\n'
            'tag: ' + tag + '\n'
            'excerpt: "Latest ' + tag.replace('-', ' ') + ' signals and analysis from ai360trading."\n'
            '---\n'
        )
        f.write(write_str)

print("✅ Success: {} tags generated in /tag/ folder.".format(len(total_tags)))
