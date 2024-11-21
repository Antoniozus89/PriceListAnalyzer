import os
import pandas as pd
import json

class PriceMachine:
    def __init__(self):
        self.data = []

    def load_prices(self, directory='.'):
        '''
        Сканирует указанный каталог. Ищет файлы со словом "price" в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        Допустимые названия для столбца с товаром:
            товар
            название
            наименование
            продукт

        Допустимые названия для столбца с ценой:
            розница
            цена

        Допустимые названия для столбца с весом (в кг.):
            вес
            масса
            фасовка
        '''
        for filename in os.listdir(directory):
            if 'price' in filename and filename.endswith('.csv'):
                try:
                    # Загружаем файл в DataFrame
                    df = pd.read_csv(os.path.join(directory, filename), sep=',', encoding='utf-8')
                    print(f"Загружен файл: {filename}")
                    print(df.head())  # Вывод первых строк файла для проверки

                    # Ищем нужные колонки
                    product_col, price_col, weight_col = self._search_product_price_weight(df.columns)

                    if product_col is not None and price_col is not None and weight_col is not None:
                        for _, row in df.iterrows():
                            # Убираем лишние пробелы и добавляем данные в список
                            self.data.append({
                                'name': row[product_col].strip(),
                                'price': row[price_col],
                                'weight': row[weight_col],
                                'file': filename,
                                'price_per_kg': row[price_col] / row[weight_col] if row[weight_col] > 0 else 0
                            })
                    else:
                        print(f"Не найдены необходимые столбцы в файле {filename}.")
                except Exception as e:
                    print(f"Ошибка при обработке файла {filename}: {e}")

    def _search_product_price_weight(self, headers):
        '''
        Возвращает названия столбцов для названия товара, цены и веса.
        '''
        product_col = next((col for col in headers if col.lower() in ['товар', 'название', 'наименование', 'продукт']), None)
        price_col = next((col for col in headers if col.lower() in ['цена', 'розница']), None)
        weight_col = next((col for col in headers if col.lower() in ['вес', 'масса', 'фасовка']), None)

        return product_col, price_col, weight_col

    def export_to_html(self, fname='output.html'):
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
            <h1>Список товаров</h1>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''

        for idx, item in enumerate(self.data, start=1):
            result += f'''
                <tr>
                    <td>{idx}</td>
                    <td>{item['name']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file']}</td>
                    <td>{item['price_per_kg']:.2f}</td>
                </tr>
            '''

        result += '''
            </table>
        </body>
        </html>
        '''

        with open(fname, 'w', encoding='utf-8') as f:
            f.write(result)

    def find_text(self, text):
        '''
        Ищет товары по фрагменту названия.
        '''
        return [item for item in self.data if text.lower() in item['name'].lower()]

def main():
    pm = PriceMachine()
    pm.load_prices()

    while True:
        search_text = input("Введите текст для поиска (или 'exit' для выхода): ")
        if search_text.lower() == 'exit':
            print("Работа завершена.")
            break

        results = pm.find_text(search_text)

        if results:
            print(f"{'№':<3} {'Наименование':<30} {'Цена':<10} {'Вес':<5} {'Файл':<15} {'Цена за кг.':<10}")
            for idx, item in enumerate(sorted(results, key=lambda x: x['price_per_kg']), start=1):
                print(f"{idx:<3} {item['name']:<30} {item['price']:<10} {item['weight']:<5} {item['file']:<15} {item['price_per_kg']:.2f}")
        else:
            print("Товары не найдены.")

    # Экспорт данных в HTML
    pm.export_to_html()
    print("Данные экспортированы в output.html")

if __name__ == "__main__":
    main()