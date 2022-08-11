import types

import numpy as np

NAN_VALUES = (
    float('nan'), 'nan', 'Nan', 'NAN', 'NaN', 'None', 'Null', 'NULL', None, np.nan,
)

MKB_COLUMNS = (
    'MKB_CODE',
    'SECOND_MKB_CODE',
    'DISCHARGE_MKB_CODE',
    'OTHER_MKB_CODE',
)

FLOAT_COLUMNS = (
    'LPU_ID',
    'INSURED_ID',
    'SERVICE_AMOUNT',
    'POLICY_NUMBER',
)

NOT_EMPTY_REQUIRED_COLUMNS = (
    'INSURED_AGE_WHEN_SERVICED',
    'INSURED_IS_MALE',
    'SERVICE_DATE',
    'POLICY_NUMBER',
)

NOT_EMPTY_REQUIRED_COLUMNS_SIMULTANEOUSLY = (
    'SERVICE_NAME',
    'NPHIES_CODE',
)

COLUMNS_WITH_DATES = (
    'INSURED_AGE_WHEN_SERVICED',
    'SERVICE_DATE',
)

COLUMNS_MAPPING = types.MappingProxyType({
    'SN': 'RECORD_ID',
    'Provider Pin': 'LPU_ID',
    'Patient ID': 'INSURED_ID',
    'DOB[HCP]': 'INSURED_AGE_WHEN_SERVICED',
    'Gender[HCP]': 'INSURED_IS_MALE',
    'Nphies Standard Code': 'NPHIES_CODE',
    'Service Type': 'PRODUCT_TYPE',
    'Service Description': 'SERVICE_NAME',
    'Service Date': 'SERVICE_DATE',
    'Requested Quantity': 'SERVICE_QUANTITY',
    'Service Provider Code': 'SERVICE_PROVIDER_CODE',
    'Principal Diagnosis Code': 'MKB_CODE',
    'Secondary Diagnosis Code': 'SECOND_MKB_CODE',
    'Discharge Diagnosis Code': 'DISCHARGE_MKB_CODE',
    'Other Diagnosis Code': 'OTHER_MKB_CODE',
    'Policy Number': 'POLICY_NUMBER',
    'Speciality Description': 'SPECIALITY_DESCRIPTION',
    'Unit Price': 'SERVICE_AMOUNT',
})
