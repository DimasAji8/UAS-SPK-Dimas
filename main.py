from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api
from models import Sepatu as SepatuModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from tabulate import tabulate

session = Session(engine)

app = Flask(__name__)
api = Api(app)


class BaseMethod():

    def __init__(self):
        self.raw_weight = {'merek': 8, 'berat': 5,
                            'bahan': 6, 'tampilan': 4, 'harga': 9}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(SepatuModel.no, SepatuModel.nama_sepatu, SepatuModel.merek, SepatuModel.berat,
                       SepatuModel.bahan, SepatuModel.tampilan, SepatuModel.harga)
        result = session.execute(query).fetchall()
        print(result)
        return [{'no': Sepatu.no, 'nama_sepatu': Sepatu.nama_sepatu, 'merek': Sepatu.merek, 'berat': Sepatu.berat,
                 'bahan': Sepatu.bahan, 'tampilan': Sepatu.tampilan, 'harga': Sepatu.harga} for Sepatu in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        nama_sepatu_values = [] # max
        merek_values = []  # max
        berat_values = []  # max
        bahan_values = []  # max
        tampilan_values = []  # max
        harga_values = []  # min

        for data in self.data:
            # Nama_Sepatu
            nama_sepatu_spec = data['nama_sepatu']
            numeric_values = [int(value.split()[0]) for value in nama_sepatu_spec.split(
                ',') if value.split()[0].isdigit()]
            max_nama_sepatu_value = max(numeric_values) if numeric_values else 1
            nama_sepatu_values.append(max_nama_sepatu_value)
            
            # Merek
            merek_spec = data['merek']
            merek_numeric_values = [int(
                value.split()[0]) for value in merek_spec.split() if value.split()[0].isdigit()]
            max_merek_value = max(
                merek_numeric_values) if merek_numeric_values else 1
            merek_values.append(max_merek_value)

            # Double_Visor
            berat_spec = data['berat']
            berat_numeric_values = [float(value.split()[0]) for value in berat_spec.split(
            ) if value.replace('.', '').isdigit()]
            max_berat_value = max(
                berat_numeric_values) if berat_numeric_values else 1
            berat_values.append(max_berat_value)

            # Sertifikasi
            bahan_spec = data['bahan']
            bahan_numeric_values = [
                int(value) for value in bahan_spec.split() if value.isdigit()]
            max_bahan_value = max(
                bahan_numeric_values) if bahan_numeric_values else 1
            bahan_values.append(max_bahan_value)

            # Garansi
            tampilan_spec = data['tampilan']
            tampilan_numeric_values = [
                int(value) for value in tampilan_spec.split() if value.isdigit()]
            max_tampilan_value = max(
                tampilan_numeric_values) if tampilan_numeric_values else 1
            tampilan_values.append(max_tampilan_value)

            # Harga
            harga_cleaned = ''.join(
                char for char in str(data['harga']) if char.isdigit())
            harga_values .append(float(harga_cleaned) if harga_cleaned else 0)  # Convert to float

        return [
    {
        'no': data['no'],
        'nama_sepatu': nama_sepatu_value / max(nama_sepatu_values),
        'merek': merek_value / max(merek_values),
        'berat': berat_value / max(berat_values),
        'bahan': bahan_value / max(bahan_values),
        'tampilan': tampilan_value / max(tampilan_values),
        'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0
    }
    for data, nama_sepatu_value, merek_value, berat_value, bahan_value, tampilan_value, harga_value
    in zip(self.data, nama_sepatu_values, merek_values, berat_values, bahan_values, tampilan_values, harga_values)
]


    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

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
                'ID': product['no'],
                'score': round(product['produk'], 3)
            }
            for product in sorted_produk
        ]
        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'sepatu': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value


class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'ID': row['no'],
                'Score': round(row['merek'] * weight['merek'] +
                        row['berat'] * weight['berat'] +
                        row['bahan'] * weight['bahan'] +
                        row['tampilan'] * weight['tampilan'] +
                        row['harga'] * weight['harga'], 2)
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x['Score'], reverse=True)
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'sepatu': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value


class Sepatu(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Data Tidak Ditemukan.')
        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = session.query(SepatuModel).order_by(SepatuModel.no)
        result_set = query.all()
        data = [{'no': row.no, 'nama_sepatu': row.nama_sepatu, 'merek': row.merek,
                 'berat': row.berat, 'bahan': row.bahan, 'tampilan': row.tampilan, 'harga': row.harga}
                for row in result_set]
        return self.get_paginated_result('sepatu/', data, request.args), 200


api.add_resource(Sepatu, '/sepatu')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005',debug=True)