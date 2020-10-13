import os
from pathlib import Path

import pandas as pd

path = Path(os.path.abspath(__file__)).parent.parent / "data" / "index_symbol_map.csv"
_map_instrument_to_tushare = pd.read_csv(path).drop_duplicates("symbol_ricequant").set_index("symbol_ricequant")
_map_tushare_to_instrument = pd.read_csv(path).drop_duplicates("symbol_tushare").set_index("symbol_tushare")

_suffix_map = {
    "XSHE": "SZ",
    "XSHG": "SH",
    "SZ": "XSHE",
    "SH": "XSHG"
}

def ricequant_to_tushare(order_book_id):
    code, suffix = order_book_id.split(".")
    if suffix in ['XSHE', 'XSHG']:
        return ".".join([code, _suffix_map[suffix]])
    else:
        try:
            return _map_tushare_to_instrument['symbol_ricequant'].loc[order_book_id]
        except KeyError:
            raise RuntimeError("Unsupported order_book_id type.")


def tushare_to_ricequant(order_book_id):
    code, suffix = order_book_id.split(".")
    if suffix in ['SZ', 'SH']:
        return ".".join([code, _suffix_map[suffix]])
    else:
        try:
            return _map_instrument_to_tushare['symbol_ricequant'].loc[order_book_id]
        except KeyError:
            raise RuntimeError("Unsupported order_book_id type.")


if __name__ == "__main__":
    # ,399957.XSHE,399957.SZ
    # 700,000907.XSHG,000907.CSI
    #print(ricequant_to_tushare("399957.XSHE"))
    #print(tushare_to_ricequant("399957.SZ"))

    print(ricequant_to_tushare("000907.XSHG"))
    print(tushare_to_ricequant("399957.SZ"))


