import json
import os
import math

from urllib.parse import quote
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked



def make_slug(book_path):
    name = os.path.splitext(os.path.basename(book_path))[0]
    return name.split('-', 1)[0]


def split_columns(books):
    half = (len(books) + 1) // 2
    return books[:half], books[half:]


def render_books_page(books_file='meta_data.json', template_name='base.html', books_per_page=10):
    with open(books_file, 'r', encoding='utf-8') as file:
        books = json.load(file)

    for book in books:
        book['read_url'] = '/' + quote(book['book_path'], safe='/')
        book['img_url'] = '/' + quote(book['img_src'], safe='/')
        book['slug'] = make_slug(book['book_path'])

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    total_pages = math.ceil(len(books) / books_per_page)
    chunks = list(chunked(books, books_per_page))

    if not os.path.exists('pages'):
        os.makedirs('pages')

    template = env.get_template(template_name)

    page_numbers = range(1, total_pages + 1)

    for i, page_books in enumerate(chunks):
        page_number = i + 1
        left_column, right_column = split_columns(page_books)

        rendered_page = template.render(
            left_column=left_column,
            right_column=right_column,
            current_page=page_number,
            total_pages=total_pages,
            page_numbers=page_numbers,
            prev_page=page_number - 1 if page_number > 1 else None,
            next_page=page_number + 1 if page_number < total_pages else None
        )

        filename = f'pages/index{page_number}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(rendered_page)

    return rendered_page


def main():
    render_books_page()

    server = Server()

    server.watch('base.html')

    def on_reload():
        render_books_page()

    server.watch('base.html', on_reload)

    try:
        server.serve(port=5500, root='.')
    except KeyboardInterrupt:
        server.server_close()


if __name__ == '__main__':
    main()