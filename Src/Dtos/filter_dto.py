from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.filter_types import filter_types

# Фильтрация
class filter_dto(abstract_dto):
    __field_name: str = ""
    __value: str = ""
    __filter_type: filter_types = filter_types.EQUALS

    @property
    def field_name(self) -> str:
        return self.__field_name
    
    @field_name.setter
    def field_name(self, value: str):
        self.__field_name = value

    @property
    def value(self) -> str:
        return self.__value
    
    @value.setter
    def value(self, value: str):
        self.__value = value

    @property
    def filter_type(self) -> filter_types:
        return self.__filter_type
    
    @filter_type.setter
    def filter_type(self, value: filter_types):
        validator.validate(value, filter_types)
        self.__filter_type = value

    def create(self, data) -> "filter_dto":
        super().create(data)
        
        if "filter_type" in data:
            filter_type_value = data["filter_type"]
            if hasattr(filter_types, filter_type_value):
                self.filter_type = getattr(filter_types, filter_type_value)
            else:
                self.filter_type = filter_types(filter_type_value)
                
        return self

