INSERT INTO execution_info (id_zip_code,id_commercial_premise_type)
SELECT id, 1
FROM zip_code_info
WHERE zip_code like '2804%'