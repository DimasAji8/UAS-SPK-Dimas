import sys
from colorama import Fore, Style
from models import Base, Sepatu
from engine import engine
from tabulate import tabulate

from sqlalchemy import select
from sqlalchemy.orm import Session
from settings import DEV_SCALE

session = Session(engine)


def create_table():
    Base.metadata.create_all(engine)
    print(f'{Fore.GREEN}[Success]: {Style.RESET_ALL}Database has created!')


def review_data():
    query = select(Sepatu)
    for phone in session.scalars(query):
        print(Sepatu)


class BaseMethod():

    def __init__(self):
        # 1-5
        self.raw_weight = {'merek': 8, 'berat': 5,
                            'bahan': 6, 'tampilan': 4, 'harga': 9}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(Sepatu.no, Sepatu.nama_sepatu, Sepatu.merek, Sepatu.berat,
                       Sepatu.bahan, Sepatu.tampilan, Sepatu.harga)
        result = session.execute(query).fetchall()
        return [{'no': Sepatu.no, 'nama_sepatu': Sepatu.nama_sepatu, 'merek': Sepatu.merek, 'berat': Sepatu.berat,
                 'bahan': Sepatu.bahan, 'tampilan': Sepatu.tampilan, 'harga': Sepatu.harga} for Sepatu in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        merek_values = []  # max
        berat_values = []  # max
        bahan_values = []  # max
        tampilan_values = []  # max
        harga_values = []  # min

        for data in self.data:
            # merek
            merek_spec = data['merek']
            numeric_values = [int(value.split()[0]) for value in merek_spec.split(
                ',') if value.split()[0].isdigit()]
            max_merek_value = max(numeric_values) if numeric_values else 1
            merek_values.append(max_merek_value)

            # Berat
            berat_spec = data['berat']
            berat_numeric_values = [int(
                value.split()[0]) for value in berat_spec.split() if value.split()[0].isdigit()]
            max_berat_value = max(
                berat_numeric_values) if berat_numeric_values else 1
            berat_values.append(max_berat_value)

            # RAM
            bahan_spec = data['bahan']
            bahan_numeric_values = [
                int(value) for value in bahan_spec.split() if value.isdigit()]
            max_bahan_value = max(
                bahan_numeric_values) if bahan_numeric_values else 1
            bahan_values.append(max_berat_value)

            # Memori
            tampilan_value = DEV_SCALE['tampilan'].get(data['tampilan'], 1)
            tampilan_values.append(tampilan_value)

            # Harga
            harga_cleaned = ''.join(
                char for char in data['harga'] if char.isdigit())
            harga_values.append(float(harga_cleaned)
                                if harga_cleaned else 0)  # Convert to float

        return [
            {'no': data['no'],
             'merek': merek_value / max(merek_values),
             'berat': berat_value / max(berat_values),
             'bahan': bahan_value / max(bahan_values),
             'tampilan': tampilan_value / max(tampilan_values),
             # To avoid division by zero
             'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0
             }
            for data, merek_value, berat_value, bahan_value, tampilan_value, harga_value
            in zip(self.data, merek_values, berat_values, bahan_values, tampilan_values, harga_values)
        ]


class WeightedProduct(BaseMethod):
    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['merek']**self.weight['merek'] *
                row['berat']**self.weight['berat'] *
                row['bahan']**self.weight['bahan'] *
                row['tampilan']**self.weight['tampilan'] *
                row['harga']**self.weight['harga']
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'no': product['no'],
                'merek': product['produk'] / self.weight['merek'],
                'berat': product['produk'] / self.weight['berat'],
                'bahan': product['produk'] / self.weight['bahan'],
                'tampilan': product['produk'] / self.weight['tampilan'],
                'harga': product['produk'] / self.weight['harga'],
                'score': product['produk']  # Nilai skor akhir
            }
            for product in sorted_produk
        ]
        return sorted_data


class SimpleAdditiveWeighting(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = {row['no']:
                  round(row['merek'] * weight['merek'] +
                        row['berat'] * weight['berat'] +
                        row['bahan'] * weight['bahan'] +
                        row['tampilan'] * weight['tampilan'] +
                        row['harga'] * weight['harga'], 2)
                  for row in self.normalized_data
                  }
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1], reverse=True))
        return sorted_result


def run_saw():
    saw = SimpleAdditiveWeighting()
    result = saw.calculate
    print(tabulate(result.items(), headers=['No', 'Score'], tablefmt='pretty'))


def run_wp():
    wp = WeightedProduct()
    result = wp.calculate
    headers = result[0].keys()
    rows = [
        {k: round(v, 4) if isinstance(v, float) else v for k, v in val.items()}
        for val in result
    ]
    print(tabulate(rows, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == 'create_table':
            create_table()
        elif arg == 'saw':
            run_saw()
        elif arg == 'wp':
            run_wp()
        else:
            print('command not found')
