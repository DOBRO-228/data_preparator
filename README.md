# Модуль предобработки данных

## Версия **0.1.0**

### Пошаговый алгоритм

- **Делает копию оригинального дата фрейма, в который добавляет колонку RECORD_ID с уникальными значениями**

- **Удаляет колонки, которых нет в `маппинге наименования колонок`**

- **Переименовывает колонки согласно `маппингу наименования колонок`**

- **Делает значения в столбце RECORD_ID уникальными, если в изначальном файле они таковыми не являлись**

- **Приводит к одному формату дат колонки с датами, а именно**
    1. 'INSURED_AGE_WHEN_SERVICED'
    2. 'SERVICE_DATE'

    Если алгоритму не удалось распознать дату, то она затирается, и ячейка становится пустой

- **Отделяет в отдельный data frame строки с пустыми ячейками в обязательных колонках, а именно**
    1. 'INSURED_AGE_WHEN_SERVICED'
    2. 'INSURED_IS_MALE'
    3. 'SERVICE_DATE'
    4. 'POLICY_NUMBER'

    И также в колонках, которые должны быть одновременно пустыми:
    1. 'INSURED_AGE_WHEN_SERVICED'
    2. 'INSURED_IS_MALE'

- **Приводит к строке колонки с МКБ кодами, а именно**
    1. 'MKB_CODE'
    2. 'SECOND_MKB_CODE'
    3. 'DISCHARGE_MKB_CODE'
    4. 'OTHER_MKB_CODE'

- **Приводит к строке колонку с НФИС кодами ('NPHIES_CODE') и наименованием услуг ('SERVICE_NAME')**

- **Удаляет нули с левой стороны НФИС кодов ('NPHIES_CODE')**

    0002281488 -> 2281488

- **Меняет запятые на точки в колонках с форматом float, а именно**
    1. 'LPU_ID'
    2. 'INSURED_ID'
    3. 'SERVICE_AMOUNT'
    4. 'POLICY_NUMBER'

- **Приводит к булевому значению колонку с полом пациента ('INSURED_IS_MALE')**

    Значения 'M', 'm', 'Male', 'male' становятся True. Всё остальное - False

- **Заполняет цифрой "1" пустые ячейки или ячейки с отрицательным значением колонки количества услуг ('SERVICE_QUANTITY')**

- **Отделяет в отдельный data frame строки с *medical devices***
    1. В основном дата фрейме создаёт новую колонку с наименованием 'NPHIES_CODE_WITHOUT_DASHES' - копия колонки 'NPHIES_CODE'
    2. К колонке 'NPHIES_CODE_WITHOUT_DASHES' применяет функцию, которая удаляет в значениях все тире ('-')
    3. Создаёт новый дата фрейм - копию основного, но берёт только те строки, у которых длинна НФИС кода ('NPHIES_CODE') равна 5
    4. Удаляет из основного дата фрейма те строки, которые оказались в дата фрейме, полученном в 3-ем пункте

- **Отделяет в отдельный data frame строки с лекарствами (*drugs*)**
    1. Создаёт дополнительный дата фрейм из файла "auxiliary_files/Номенклатура_лекарств.xlsx"
    2. В дата фрейме, полученном из 1-ого пункта, к колонке 'CODE' применяет функцию, которая удаляет нули с левой стороны кода ('0002281488' -> '2281488')
    3. Создаёт отдельный список с кодами, полученных после выполнения 2-ого пункта
    4. После берём основной дата фрейм и смотрим: если в строке в колонке 'NPHIES_CODE' значение присутствует в списке кодов из 3-его пункта, значит эта строка с лекарствами (*drugs*). Такие строки отделяются и переносятся в отдельный дата фрейм

### Результат работы модуля

```python
{
    'prepared_df': df,
    'df_with_medical_devices': df_with_medical_devices,
    'df_with_drugs': df_with_drugs,
    'df_with_empty_values': df_with_empty_values,
    'primary_df_but_with_added_record_id_column': primary_df_but_with_added_record_id_column,
}
```

, где **df** - основной дата фрейм, над которым проводились все вышеописанные манипуляции, и в котором нет лекарств и медицинского оборудования,

**df_with_medical_devices** - дата фрейм с *medical_devices*,

**df_with_drugs** - дата фрейм с лекарствами (*drugs*),

**df_with_empty_values** - дата фрейм со строками, у которых есть пустые значения в обязательных колонках,

**primary_df_but_with_added_record_id_column** - изначальный (неизменённый) дата фрейм, но с добавленной колонкой 'RECORD_ID' с уникальными значениями внутри

---

### `Маппинг наименования колонок`

1. 'SN': 'RECORD_ID'
2. 'Provider Pin': 'LPU_ID'
3. 'Patient ID': 'INSURED_ID'
4. 'DOB[HCP]': 'INSURED_AGE_WHEN_SERVICED'
5. 'Gender[HCP]': 'INSURED_IS_MALE'
6. 'Nphies Standard Code': 'NPHIES_CODE'
7. 'Service Type': 'PRODUCT_TYPE'
8. 'Service Description': 'SERVICE_NAME'
9. 'Service Date': 'SERVICE_DATE'
10. 'Requested Quantity': 'SERVICE_QUANTITY'
11. 'Service Provider Code': 'SERVICE_PROVIDER_CODE'
12. 'Principal Diagnosis Code': 'MKB_CODE'
13. 'Secondary Diagnosis Code': 'SECOND_MKB_CODE'
14. 'Discharge Diagnosis Code': 'DISCHARGE_MKB_CODE'
15. 'Other Diagnosis Code': 'OTHER_MKB_CODE'
16. 'Policy Number': 'POLICY_NUMBER'
17. 'Speciality Description': 'SPECIALITY_DESCRIPTION'
18. 'Unit Price': 'SERVICE_AMOUNT'
