import sys

import pandas as pd

sys.path.append('/home/dobro/Desktop/work/medgulf/data-preparator/')
from data_preparator.data_preparator import process_data_frame
from debug.script_for_test import excel_to_list_of_dicts


def main():
    """Запуск скрипта."""
    test_case_rows = excel_to_list_of_dicts('debug/debug_input/тест-кейс_структура.xlsx')
    df = pd.DataFrame(test_case_rows)
    data_frames = process_data_frame(df)

    services = data_frames.get('df_with_services')
    medical_devices = data_frames.get('df_with_medical_devices')
    drugs = data_frames.get('df_with_drugs')
    incomplete_data = data_frames.get('df_with_incomplete_data')

    services.to_excel('debug/debug_output/services.xlsx')
    medical_devices.to_excel('debug/debug_output/medical_devices.xlsx')
    drugs.to_excel('debug/debug_output/drugs.xlsx')
    incomplete_data.to_excel('debug/debug_output/incomplete_data.xlsx')

    print('!!!!!!!!!!!!!!!!!!!\n')


if __name__ == '__main__':
    main()
