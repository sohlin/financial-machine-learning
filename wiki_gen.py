from conf import PROJECT_ROOT_DIR
import os
import pandas as pd
import numpy as np
import re

from git_status import get_repo_list


def get_wiki_status_color(input_text):
    if input_text is None or input_text == 'inactive':
        result_text = ":heavy_multiplication_x:"
    else:
        result_text = ":heavy_check_mark:"
    return '<sub>{}</sub>'.format(result_text)


def get_wiki_rating(input_rating):
    result_text = ''
    if input_rating is not None and not np.isnan(input_rating):
        rating = int(input_rating)
        result_text = ':star:x{}'.format(rating)
    return '<sub>{}</sub>'.format(result_text)


def generate_wiki_per_category(output_path, update_readme: bool = True):
    """

    :param update_readme:
    :param output_path:
    """
    repo_df = get_repo_list()
    for category in repo_df['category'].unique():
        category_df = repo_df[repo_df['category'] == category].copy()
        url_md_list = []
        for idx, irow in category_df[['name', 'url']].iterrows():
            url_md_list.append('<sub>[{}]({})</sub>'.format(irow['name'], irow['url']))

        formatted_df = pd.DataFrame({
            'repo': url_md_list,
            'comment': category_df['comment'].apply(lambda x: '<sub>{}</sub>'.format(x)),
            'created_at': category_df['created_at'].apply(lambda x: '<sub>{}</sub>'.format(x)),
            'last_commit': category_df['last_commit'].apply(lambda x: '<sub>{}</sub>'.format(x)),
            'star_count': category_df['star_count'].apply(lambda x: '<sub>{}</sub>'.format(x)),
            'repo_status': category_df['repo_status'],
            'rating': category_df['rating']
        })
        # add color for the status
        formatted_df = formatted_df.sort_values(by=['rating', 'star_count'], ascending=False).reset_index(drop=True)
        formatted_df['repo_status'] = formatted_df['repo_status'].apply(lambda x: get_wiki_status_color(x))
        formatted_df['rating'] = formatted_df['rating'].apply(lambda x: get_wiki_rating(x))
        formatted_df.columns = ['<sub>{}</sub>'.format(x) for x in formatted_df.columns]

        clean_category_name = category.lower().replace(' ', '_')
        output_path_full = os.path.join(output_path, '{}.md'.format(clean_category_name))
        with open(output_path_full, 'w') as f:
            f.write(formatted_df.to_markdown(index=False))
        print('wiki generated in [{}]'.format(output_path_full))

        if update_readme:
            check_str = '[PLACEHOLDER_START:{}]'.format(clean_category_name)
            with open(os.path.join(PROJECT_ROOT_DIR, 'README.md')) as f:
                all_read_me = f.read()
                if check_str not in all_read_me:
                    print(f'section {check_str} not found')
                    continue

            # only display top 5, then expandable for extra 5
            with open(os.path.join(PROJECT_ROOT_DIR, 'README.md'), 'w') as f:

                table_str = formatted_df.iloc[:15].to_markdown(index=False)
                new_str = f"<!-- [PLACEHOLDER_START:{clean_category_name}] --> \n"
                new_str += table_str
                new_str += f"<!-- [PLACEHOLDER_END:{clean_category_name}] -->"

                search_start = re.escape('<!-- [PLACEHOLDER_START:{}] -->'.format(clean_category_name))
                search_end = re.escape('<!-- [PLACEHOLDER_END:{}] -->'.format(clean_category_name))
                pattern_s = re.compile(r'{}.*?{}'.format(search_start, search_end), re.DOTALL)
                write_str = re.sub(pattern_s, new_str, all_read_me)
                f.write(write_str)


if __name__ == '__main__':
    local_path = os.path.join(PROJECT_ROOT_DIR, 'generated_wiki')
    generate_wiki_per_category(local_path)
