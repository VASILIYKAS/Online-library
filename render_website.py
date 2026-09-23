import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def render_books_page(books_file='meta_data.json', template_name='base.html'):
    with open(books_file, 'r', encoding='utf-8') as file:
        books = json.load(file)

    chunks = list(chunked(books, len(books) // 2))

    left_column = chunks[0]
    right_column = chunks[1]

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template(template_name)

    rendered_page = template.render(
        left_column=left_column,
        right_column=right_column,
    )

    return rendered_page


def main():
    page = render_books_page()

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(page)

    server = Server()

    server.watch('base.html')

    def on_reload():
        page = render_books_page()
        with open('index.html', 'w', encoding="utf8") as file:
            file.write(page)

    server.watch('base.html', on_reload)

    try:
        server.serve(port=5500, root='.')
    except KeyboardInterrupt:
        server.server_close()


if __name__ == '__main__':
    main()