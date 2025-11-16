from Src.Core.abstract_dto import abstract_dto
from Src.Dtos.filter_dto import filter_dto
from Src.Core.validator import validator

class complex_filter_dto(abstract_dto):
    __filters: list[filter_dto] = []
    __model_type: str = ""

    @property
    def filters(self) -> list[filter_dto]:
        return self.__filters
    
    @filters.setter
    def filters(self, value: list[filter_dto]):
        validator.validate(value, list)
        self.__filters = value

    @property
    def model_type(self) -> str:
        return self.__model_type
    
    @model_type.setter
    def model_type(self, value: str):
        self.__model_type = value

    def create(self, data) -> "complex_filter_dto":
        super().create(data)
        
        if "filters" in data and isinstance(data["filters"], list):
            self.filters = []
            for filter_data in data["filters"]:
                filter_item = filter_dto().create(filter_data)
                self.filters.append(filter_item)
                
        return self