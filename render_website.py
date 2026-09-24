import json
import math
import os
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def load_books(books_file='meta_data.json'):
    with open(books_file, 'r', encoding='utf-8') as file:
        return json.load(file)


def make_slug(book_path):
    name = os.path.splitext(os.path.basename(book_path))[0]
    return name.split('-', 1)[0]


def encode_book(book):
    book['read_url'] = '/' + quote(book['book_path'], safe='/')
    book['img_url'] = '/' + quote(book['img_src'], safe='/')
    book['slug'] = make_slug(book['book_path'])
    book['genres'] = [g.strip('.') for g in book['genres'].split(',')]
    return book


def make_env():
    return Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )


def split_columns(books):
    half = (len(books) + 1) // 2
    return books[:half], books[half:]


def render_book_page(template, book):
    with open(book['book_path'], 'r', encoding='utf-8') as file:
        book_text = file.read()

    return template.render(
        book=book,
        book_text=book_text,
        current_page=book.get('page', 1),
    )


def render_books_page(template, page_books, page_number, total_pages):
    page_numbers = range(1, total_pages + 1)
    left_column, right_column = split_columns(page_books)
    
    return template.render(
        left_column=left_column,
        right_column=right_column,
        current_page=page_number,
        total_pages=total_pages,
        page_numbers=page_numbers,
        prev_page=page_number - 1 if page_number > 1 else None,
        next_page=page_number + 1 if page_number < total_pages else None,
    )


def save_page(html, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(html)


def build_site(books_file='meta_data.json', books_per_page=8):
    books = [encode_book(book) for book in load_books(books_file)]

    env = make_env()
    books_template = env.get_template('base.html')
    book_template = env.get_template('book.html')

    total_pages = math.ceil(len(books) / books_per_page)
    chunks = list(chunked(books, books_per_page))

    for i, page_books in enumerate(chunks):
        page_number = i + 1
        for book in page_books:
            book['page'] = page_number

        html = render_books_page(books_template, page_books, page_number, total_pages)
        save_page(html, f'pages/index{page_number}.html')

    for book in books:
        html = render_book_page(book_template, book)
        save_page(html, f"pages/{book['slug']}.html")


def main():
    build_site()

    server = Server()

    def on_reload():
        build_site()

    server.watch('base.html', on_reload)
    server.watch('book.html', on_reload)

    try:
        server.serve(port=5500, root='.')
    except KeyboardInterrupt:
        server.server_close()


if __name__ == '__main__':
    main()