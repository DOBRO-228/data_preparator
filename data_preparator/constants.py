import types

import numpy as np

NAN_VALUES = (
    float('nan'), 'nan', 'Nan', 'NAN', 'NaN', 'None', 'Null', 'NULL', None, np.nan,
)

EXPECTED_SEPARATORS_IN_DATES = (' ', '/', '\\', '-')

MKB_COLUMNS = (
    'MKB_CODE',
    'SECOND_MKB_CODE',
)


# Column types

STR_COLUMNS = MKB_COLUMNS + (
    'LPU_ID',
    'INSURED_ID',
    'SERVICE_NAME',
    'PRODUCT_TYPE',
    'NPHIES_CODE',
    'TOOTH',
    'BENEFIT_TYPE',
    'DOCTOR_NAME',
)
INT_COLUMNS = ('SERVICE_QUANTITY', )

FLOAT_COLUMNS = ('SERVICE_AMOUNT', )

COLUMNS_WITH_DATES = (
    'INSURED_AGE_WHEN_SERVICED',
    'SERVICE_DATE',
)

NOT_EMPTY_REQUIRED_COLUMNS = (
    'LPU_ID',
    'INSURED_ID',
    'INSURED_AGE_WHEN_SERVICED',
    'INSURED_IS_MALE',
    'SERVICE_NAME',
    'SERVICE_DATE',
    'SERVICE_QUANTITY',
    'SERVICE_AMOUNT',
    'MKB_CODE',
    'BENEFIT_TYPE',
)

NOT_EMPTY_REQUIRED_COLUMNS_SIMULTANEOUSLY = (
    'PRODUCT_TYPE',
    'NPHIES_CODE',
)


COLUMNS_MAPPING = types.MappingProxyType({
    'provider_id': 'LPU_ID',
    'member_id': 'INSURED_ID',
    'dob': 'INSURED_AGE_WHEN_SERVICED',
    'gender': 'INSURED_IS_MALE',
    'service_name': 'SERVICE_NAME',
    'service_date': 'SERVICE_DATE',
    'service_type': 'PRODUCT_TYPE',
    'service_quantity': 'SERVICE_QUANTITY',
    'service_amount': 'SERVICE_AMOUNT',
    'nphies_code': 'NPHIES_CODE',
    'icd10_code': 'MKB_CODE',
    'icd10_code_secondary': 'SECOND_MKB_CODE',
    'tooth': 'TOOTH',
    'benefit_type': 'BENEFIT_TYPE',
    'doctor_name': 'DOCTOR_NAME',
})
