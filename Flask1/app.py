from flask import Flask, request

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        return f'Результаты поиска для: {query}'
    else:
        return 'Введите поисковый запрос'
@app.route('/calc')
def calc():
    a = request.args.get('a')
    b = request.args.get('b')
    op = request.args.get('op')
    if op == 'add':
        return f'сумма {a} и {b} = {int(a) + int(b)}'
    elif op == 'mul':
        return f'произведение {a} и {b} = {int(a) * int(b)}'
    elif op == 'dif':
        return f'разность {a} и {b} = {int(a) - int(b)}'
    elif op == 'sub':
        if int(b) != 0:
            return f'частное от деления {a} и {b} = {int(a) / int(b)}'
        else :
            return f'Делить на ноль нельзя!!!! '
if __name__ == '__main__':
    app.run(debug=True)