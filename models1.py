from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Sepatu(Base):
    __tablename__ = "tbl_sepatu"
    no = Column(Integer, primary_key=True)
    nama_sepatu = Column(String(255))
    merek = Column(String(255))
    berat = Column(String(255))
    bahan = Column(String(255))
    tampilan = Column(String(255))
    harga = Column(String(255))

    def __init__(self, nama_sepatu, merek, berat, bahan, tampilan, harga):
        self.nama_sepatu = nama_sepatu
        self.merek = merek
        self.berat = berat
        self.bahan = bahan
        self.tampilan = tampilan
        self.harga = harga

    def calculate_score(self, dev_scale):
        score = 0
        score += self.merek * dev_scale['merek']
        score += self.berat * dev_scale['berat']
        score += self.bahan * dev_scale['bahan']
        score += self.tampilan * dev_scale['tampilan']
        score -= self.harga * dev_scale['harga']
        return score

    def __repr__(self):
        return f"Sepatu(nama_sepatu={self.nama_sepatu!r}, merek={self.merek!r}, berat={self.berat!r}, bahan={self.bahan!r}, tampilan={self.tampilan!r}, harga={self.harga!r})"
