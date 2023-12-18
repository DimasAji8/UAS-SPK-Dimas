from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Sepatu(Base): 
    __tablename__ = "tbl_sepatu"
    no = Column(Integer, primary_key=True)
    nama_sepatu = Column(String)
    merek = Column(String)
    berat = Column(String)
    bahan = Column(String)
    tampilan = Column(String)
    harga = Column(String)

    def __repr__(self):
        return f"Sepatu(nama_sepatu={self.nama_sepatu!r}, merek={self.merek!r}, berat={self.berat!r}, bahan={self.bahan!r}, tampilan={self.tampilan!r}, harga={self.harga!r})"
