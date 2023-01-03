import pandas as pd

from .. import constants
from .strings import remove_extra_whitespaces

if constants.ENV == 'LOCAL':
    SERVICE_NAME_TO_NPHIES_CODE_MAPPING = pd.read_excel(
        'auxiliary_files/Маппинг_название_услуги_к_нфис_коду.xlsx',
    )
else:
    from app.pipiline.utils.base import get_cached_mapping
    SERVICE_NAME_TO_NPHIES_CODE_MAPPING = get_cached_mapping('service_name_to_nphies_code_mapping')


def get_service_name_to_nphies_code_mapping() -> dict:
    """
    Возвращает маппинг 'SERVICE_NAME' - 'NPHIES_CODE' из файла Ксюши.

    К 'SERVICE_NAME' применяет методы strip() и lower(), а также заменяет много пробелов между словами на один.
    К 'NPHIES_CODE' применяет только метод strip().
    """
    mapping_as_dict_with_lowered_service_names = SERVICE_NAME_TO_NPHIES_CODE_MAPPING.set_index(
        'SERVICE_NAME',
    ).to_dict()['NPHIES_CODE']
    mapping_as_dict_with_lowered_service_names = {
        str(service_name).strip().lower(): str(nphies_code).strip()
        for service_name, nphies_code in mapping_as_dict_with_lowered_service_names.items()
    }
    return {
        remove_extra_whitespaces(service_name): nphies_code
        for service_name, nphies_code in mapping_as_dict_with_lowered_service_names.items()
    }
