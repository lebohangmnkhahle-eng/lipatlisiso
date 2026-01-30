import json
import os
from typing import List, Optional
import dataclasses
from mafisa_insights.data_models import MSME, Financials

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'msme_data.json')

class DataStore:
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.ensure_data_file()

    def ensure_data_file(self):
        directory = os.path.dirname(self.data_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)

    def save_msme(self, msme: MSME):
        msmes = self.load_msmes()
        # check if exists, update or append
        existing_idx = next((i for i, m in enumerate(msmes) if m.id == msme.id), None)
        if existing_idx is not None:
            msmes[existing_idx] = msme
        else:
            msmes.append(msme)

        with open(self.data_file, 'w') as f:
            json.dump([dataclasses.asdict(m) for m in msmes], f, indent=4)

    def load_msmes(self) -> List[MSME]:
        if not os.path.exists(self.data_file):
            return []

        with open(self.data_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return []

        msmes = []
        for item in data:
            if 'financials' in item:
                fin_data = item.pop('financials')
                financials = Financials(**fin_data)
                msme = MSME(financials=financials, **item)
                msmes.append(msme)
        return msmes

    def get_msme(self, msme_id: str) -> Optional[MSME]:
        msmes = self.load_msmes()
        return next((m for m in msmes if m.id == msme_id), None)
