import json
import re

input_file = 'data/only_review_data.json'
save_file = 'data/fooddotcom_review_sub_data.json'

with open(input_file, 'r') as f:
    comment_data = json.load(f)

bad_templates = [
    r'not\ssubstitute[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'not\sreplace[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'not\ssub[bed]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'not\ssubstitute[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'not\sreplace[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'not\ssub[bed]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'n\'t\ssubstitute[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'n\'t\sreplace[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'n\'t\ssub[bed]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'n\'t\ssubstitute[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'n\'t\sreplace[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'n\'t\ssub[bed]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
]

sub_templates = [
    r'substitute[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'replace[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'sub[bed]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'substitute[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'replace[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'sub[bed]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
]

sub_iterators = [re.compile(regex) for regex in sub_templates]
bad_iterators = [re.compile(regex) for regex in bad_templates]

results = []

for raw_comment in comment_data:
    comment = raw_comment.lower()
    candidates = []
    candidate_str = []
    bad_candidate_str = []

    for iterator in sub_iterators:
        for match in iterator.finditer(comment):
            candidate_str.append(match.group())
            candidates.append(match.groupdict())

    if not candidates:
        continue

    for iterator in bad_iterators:
        for match in iterator.finditer(comment):
            bad_candidate_str.append(match.group())

    for ind, comment_str in enumerate(candidate_str):
        if not any(comment_str in bad_str for bad_str in bad_candidate_str):
            source = candidates[ind]['source'].strip()
            sub = candidates[ind]['sub'].strip()
            if source and sub:
                results.append({
                    "fromIng": source,
                    "toIng": sub
                })

# deduplicate
results = [dict(t) for t in {tuple(sorted(d.items())) for d in results}]

print('number of substitutions found:', len(results))

with open(save_file, 'w') as f:
    json.dump(results, f, indent=2)