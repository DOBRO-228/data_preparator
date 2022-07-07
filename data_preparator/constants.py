import numpy as np

NAN_VALUES = ['nan', 'Nan', 'NAN', 'NaN', 'None', 'Null', 'NULL', None, np.nan]

FLOAT_COLUMNS = [
    'LPU_ID',
    'INSURED_ID',
    'SERVICE_AMOUNT',
    'POLICY_NUMBER',
    'SPECIALITY_CODE',
]

REQUIRED_NOT_EMPTY_COLUMNS = [
    'SERVICE_NAME',
    'INSURED_AGE_WHEN_SERVICED',
    'INSURED_IS_MALE',
    'SERVICE_DATE',
    'POLICY_NUMBER',
]

COLUMNS_MAPPING = {
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
    'Practioner ID': 'DOCTOR_ID',
    'Speciality Code': 'SPECIALITY_CODE',
    'Speciality Description': 'SPECIALITY_DESCRIPTION',
    'Unit Price': 'SERVICE_AMOUNT',
}

COLUMNS_WITH_DATES = [
    'INSURED_AGE_WHEN_SERVICED',
    'SERVICE_DATE',
]
