import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_books_page(books_file='meta_data.json', template_name='base.html'):
    with open(books_file, 'r', encoding='utf-8') as file:
        books = json.load(file)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template(template_name)

    rendered_page = template.render(
        books=books,
    )

    return rendered_page


def main():
    page = render_books_page()

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(page)

    print('Сервер запущен и доступен по адресу: http://127.0.0.1:8000')
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Сервер остановлен.')
        server.server_close()


if __name__ == '__main__':
    main()