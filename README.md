# Модуль предобработки данных

## Версия **0.1.0**

### Пошаговый алгоритм

- **Удаляет полностью пустые строки и колонки без наименования из data frame'а**

- **Делает копию оригинального дата фрейма, в который добавляет колонку RECORD_ID с уникальными значениями**

- **Проверяет, что колонки из `маппинга наименования колонок` присутствуют в data frame'е**

    Если проверка не пройдена, то модуль возвращает этот же файл, в котором в первые строчки вставлен текст ошибки. К этим строчкам также применяется эксель стиль

- **Удаляет колонки, которых нет в `маппинге наименования колонок`**

- **Переименовывает колонки согласно `маппингу наименования колонок`**

- **Проводит `валидацию` всех строк**

    Если в строке есть хотя бы одна ошибка, то такая строка отделяется в df_with_incomplete_data, а все ошибки записываются в новую колонку "ERRORS"

- **Устанавливает в data frame'е такой же порядок столбцов, как и в `маппинге наименования колонок`**

- **Делает значения в столбце RECORD_ID уникальными, если в изначальном файле они таковыми не являлись**

- **Приводит к строке колонки:**
    1. 'MKB_CODE'
    2. 'SECOND_MKB_CODE'
    3. 'DISCHARGE_MKB_CODE'
    4. 'OTHER_MKB_CODE'
    5. 'INSURED_ID'
    6. 'NPHIES_CODE'
    7. 'SERVICE_NAME'

- **Меняет запятые на точки в колонках с форматом float, а именно**
    1. 'LPU_ID'
    2. 'SERVICE_AMOUNT'
    3. 'POLICY_NUMBER'

- **Приводит к одному формату дат колонки с датами, а именно**
    1. 'INSURED_AGE_WHEN_SERVICED'
    2. 'SERVICE_DATE'

- **Удаляет нули с левой стороны НФИС кодов ('NPHIES_CODE')**

    0002281488 -> 2281488

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
    'df_with_services': df,
    'df_with_medical_devices': df_with_medical_devices,
    'df_with_drugs': df_with_drugs,
    'df_with_incomplete_data': df_with_incomplete_data,
    'primary_df_but_with_added_record_id_column': primary_df_but_with_added_record_id_column,
}
```

, где **df** - основной дата фрейм, над которым проводились все вышеописанные манипуляции, и в котором нет лекарств и медицинского оборудования,

**df_with_medical_devices** - дата фрейм с *medical_devices*,

**df_with_drugs** - дата фрейм с лекарствами (*drugs*),

**df_with_incomplete_data** - дата фрейм со строками, у которых есть пустые значения в обязательных колонках,

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

### `Колонки с датами`

1. 'INSURED_AGE_WHEN_SERVICED'
2. 'SERVICE_DATE'

### `Валидация`

1. В строке не пустые значения в колонках: 'INSURED_ID', 'INSURED_AGE_WHEN_SERVICED', 'INSURED_IS_MALE', 'SERVICE_DATE', 'POLICY_NUMBER'
2. В строке одновременно не пустые значения в: 'SERVICE_NAME', 'NPHIES_CODE'
3. Дата может быть распознана в `колонках с датами`
4. Дата не может быть в будущем в `колонках с датами`
5. Дата рождения ('INSURED_AGE_WHEN_SERVICED') не может быть больше даты оказания услуги ('SERVICE_DATE')
