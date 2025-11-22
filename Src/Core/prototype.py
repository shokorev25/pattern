from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.complex_filter_dto import complex_filter_dto
from Src.Core.common import common
from Src.filter_types import filter_types

class prototype:
    __data = []

    @property
    def data(self):
        return self.__data

    def __init__(self, data: list):
        validator.validate(data, list)
        self.__data = data
        
    def clone(self, data: list = None) -> "prototype":
        inner_data = self.__data if data is None else data
        return prototype(inner_data)
    
    @staticmethod
    def filter(data: list, filter_obj: filter_dto) -> list:
        if len(data) == 0:
            return data
        
        result = []
        first_item = data[0]
        
        for item in data:
            field_value = prototype.__get_nested_field_value(item, filter_obj.field_name)
            if field_value is not None and prototype.__apply_filter(field_value, filter_obj):
                result.append(item)
                
        return result

    @staticmethod
    def complex_filter(data: list, complex_filter: complex_filter_dto) -> list:
        if len(data) == 0 or len(complex_filter.filters) == 0:
            return data
            
        filtered_data = data
        for filter_obj in complex_filter.filters:
            filtered_data = prototype.filter(filtered_data, filter_obj)
            
        return filtered_data

    @staticmethod
    def __get_nested_field_value(obj, field_path: str):
        try:
            if '.' in field_path:
                parts = field_path.split('.')
                current_value = obj
                for part in parts:
                    if hasattr(current_value, part):
                        current_value = getattr(current_value, part)
                    else:
                        return None
                return str(current_value) if current_value is not None else None
            else:
                if hasattr(obj, field_path):
                    value = getattr(obj, field_path)
                    return str(value) if value is not None else None
                return None
        except:
            return None

    @staticmethod
    def __apply_filter(field_value: str, filter_obj: filter_dto) -> bool:
        if field_value is None:
            return False
            
        search_value = str(filter_obj.value).lower()
        field_value_lower = field_value.lower()
        
        if filter_obj.filter_type == filter_types.EQUALS:
            return field_value_lower == search_value
        elif filter_obj.filter_type == filter_types.LIKE:
            return search_value in field_value_lower
            
        return False

    # Формирование ОСВ
    @staticmethod
    def generate_osv(data: list, complex_filter: complex_filter_dto = None) -> dict:

        filtered_data = data
        if complex_filter:
            filtered_data = prototype.complex_filter(data, complex_filter)
            
        osv_data = {}
        
        for item in filtered_data:
            if hasattr(item, 'nomenclature') and hasattr(item, 'value'):
                nom_id = item.nomenclature.unique_code if hasattr(item.nomenclature, 'unique_code') else str(item.nomenclature)
                nom_name = item.nomenclature.name if hasattr(item.nomenclature, 'name') else "Unknown"
                
                if nom_id not in osv_data:
                    osv_data[nom_id] = {
                        'nomenclature_id': nom_id,
                        'nomenclature_name': nom_name,
                        'start_balance': 0.0,
                        'income': 0.0,
                        'outcome': 0.0,
                        'end_balance': 0.0
                    }
                
                if item.value > 0:
                    osv_data[nom_id]['income'] += item.value
                else:
                    osv_data[nom_id]['outcome'] += abs(item.value)
                    
        for nom_id in osv_data:
            osv_data[nom_id]['end_balance'] = (
                osv_data[nom_id]['start_balance'] + 
                osv_data[nom_id]['income'] - 
                osv_data[nom_id]['outcome']
            )
            
        return list(osv_data.values())