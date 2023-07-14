import re

# eg_purchase = """
# USER INPUT: On 2023-01-22, the shop purchased 100kg banana from supplier 'ABC' (contact number: 67543, email: abc_sup@gmail.com) at 1.2 dollar/kg and planed sell at 1.8 dollar/kg. Banana's fruit type is berry and shelf life is 15 days.
# ANSWER:
# ```
# Step1: Insert supplier 'ABC' if not exists
# `INSERT INTO suppliers (supplier_name, contact_number, email)
# SELECT 'ABC', '67543', 'abc_sup@gmail.com'
# WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE supplier_name = 'ABC');`
#
# Step2: Insert fruit (set the selling price to NULL and stock quantity to 0) if not exists
# `INSERT INTO fruits (fruit_name, selling_price, stock_quantity, fruit_type, shelf_life)
# SELECT 'banana', NULL, 0, 'berry', 15
# WHERE NOT EXISTS (SELECT 1 FROM fruits WHERE fruit_name = 'banana');`
#
# Step3: Insert purchase
# `INSERT INTO purchases (supplier_id, purchase_date, total_cost)
# VALUES ((SELECT supplier_id FROM suppliers WHERE supplier_name = 'ABC'), '2023-01-22', 100 * 1.2);`
#
# Step4: Insert purchase item
# `INSERT INTO purchase_items (purchase_id, fruit_id, quantity_purchased, cost_per_item, item_total_cost)
# VALUES ((SELECT MAX(purchase_id) FROM purchases), (SELECT fruit_id FROM fruits WHERE fruit_name = 'banana'), 100, 1.2, 100 * 1.2);`
#
# Step5: Update the stock quantity of banana
# `UPDATE fruits
# SET stock_quantity = stock_quantity + 100
# WHERE fruit_name = 'banana';`
#
# Step6: Update the selling price of banana if given new selling price
# `UPDATE fruits
# SET selling_price = 1.8
# WHERE fruit_name = 'banana';`
# ```
# """
#
# eg_ask_sale = """
# USER INPUT: Who bought 100kg apple on 2010-03-27 and what is he/she name, detailed information and costumer id?
# ANSWER:
# ```
# Step1: Retrieve the customer information who made the purchase
# `SELECT c.customer_id, c.first_name, c.last_name, c.phone_number, c.email
# FROM customers c
# JOIN sales s ON c.customer_id = s.customer_id
# JOIN sale_items si ON s.sale_id = si.sale_id
# JOIN fruits f ON si.fruit_id = f.fruit_id
# WHERE f.fruit_name = 'apple' AND si.quantity_sold = 100 AND s.sale_date = '2010-03-27';`
# ```
# """
#
# eg_if_new_customer_sale = """
# USER INPUT: A customer named 'Chenzhuang Du' with a phone number as 120056 and e-mail as chenzhuang@gmail.com bought 10kg apple and 5kg pear on 2010-03-27.
# ANSWER:
# ```
# Step1: Insert customer 'Chenzhuang Du' if not exists
# `INSERT INTO customers (first_name, last_name, phone_number, email)
# SELECT 'Chenzhuang', 'Du', '120056', 'chenzhuang@gmail.com'
# WHERE NOT EXISTS (SELECT 1 FROM customers WHERE phone_number = '120056');`
#
# Step2: Insert sale
# `INSERT INTO sales (customer_id, sale_date, total_price)
# VALUES ((SELECT customer_id FROM customers WHERE phone_number = '120056'), '2010-03-27', (SELECT selling_price FROM fruits WHERE fruit_name = 'apple') * 10 + (SELECT selling_price FROM fruits WHERE fruit_name = 'pear') * 5);`
#
# Step3: Insert sale item
# `INSERT INTO sale_items (sale_id, fruit_id, quantity_sold, price_per_item, item_total_price)
# VALUES ((SELECT MAX(sale_id) FROM sales), (SELECT fruit_id FROM fruits WHERE fruit_name = 'apple'), 10, (SELECT selling_price FROM fruits WHERE fruit_name = 'apple'), (SELECT selling_price FROM fruits WHERE fruit_name = 'apple') * 10),
# ((SELECT MAX(sale_id) FROM sales), (SELECT fruit_id FROM fruits WHERE fruit_name = 'pear'), 5, (SELECT selling_price FROM fruits WHERE fruit_name = 'pear'), (SELECT selling_price FROM fruits WHERE fruit_name = 'pear') * 5);`
#
# Step4: Update the stock quantity of apple and pear
# `UPDATE fruits
# SET stock_quantity = CASE
#     WHEN fruit_name = 'apple' THEN stock_quantity - 10
#     WHEN fruit_name = 'pear' THEN stock_quantity - 5
#     ELSE stock_quantity
# END
# WHERE fruit_name IN ('apple', 'pear');`
# ```
# """
#
# eg_delete_pro = """
# USER INPUT: Because the customer returned the goods, roll back a sales record which is made by the customer with customer id as 8 on 2023-01-29.
# ANSWER:
# ```
# Step1: Find the sale_id for this customer on this date
# `SELECT sale_id FROM sales WHERE customer_id = 8 AND sale_date = '2023-01-29';`
#
# Step2: Get all the fruit_id and quantity_sold for this sale, replace <sale_id> with the results from the previous queries
# `SELECT fruit_id, quantity_sold FROM sale_items WHERE sale_id = <sale_id>;`
#
# Step3: Increase the stock_quantity for each fruit sold in this sale, replace <quantity_sold> <fruit_id> with the results from the previous queries
# `UPDATE fruits
# SET stock_quantity = stock_quantity + <quantity_sold>
# WHERE fruit_id = <fruit_id>;`
#
# Step4: Delete the sale items for this sale, replace <sale_id> with the results from the previous queries
# `DELETE FROM sale_items WHERE sale_id = <sale_id>;`
#
# Step5: Delete the sale record, replace <sale_id> with the results from the previous queries
# `DELETE FROM sales WHERE sale_id = <sale_id>;`
# ```
# """

eg_purchase = """
USER INPUT: On 2023-01-22, the shop purchased 100kg banana from supplier 'ABC' (contact number: 67543, email: abc_sup@gmail.com) at 1.2 dollar/kg and planed sell at 1.8 dollar/kg. Banana's fruit type is berry and shelf life is 15 days.
ANSWER:
[{
    "step_num":1,
    "description":"Insert supplier 'ABC' if not exists",
    "sql":"INSERT INTO suppliers (supplier_name, contact_number, email) SELECT 'ABC', '67543', 'abc_sup@gmail.com' WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE supplier_name = 'ABC');"
}, 
{
    "step_num":2,
    "description":"Insert fruit (set the selling price to NULL and stock quantity to 0) if not exists",
    "sql":"INSERT INTO fruits (fruit_name, selling_price, stock_quantity, fruit_type, shelf_life) SELECT 'banana', NULL, 0, 'berry', 15 WHERE NOT EXISTS (SELECT 1 FROM fruits WHERE fruit_name = 'banana');"
}, 
{
    "step_num":3,
    "description":"Insert purchase",
    "sql":"INSERT INTO purchases (supplier_id, purchase_date, total_cost) VALUES ((SELECT supplier_id FROM suppliers WHERE supplier_name = 'ABC'), '2023-01-22', 100 * 1.2);"
}, 
{
    "step_num":4,
    "description":"Insert purchase item",
    "sql":"INSERT INTO purchase_items (purchase_id, fruit_id, quantity_purchased, cost_per_item, item_total_cost) VALUES ((SELECT MAX(purchase_id) FROM purchases), (SELECT fruit_id FROM fruits WHERE fruit_name = 'banana'), 100, 1.2, 100 * 1.2);"
}, 
{
    "step_num":5,
    "description":"Update the stock quantity of banana",
    "sql":"UPDATE fruits SET stock_quantity = stock_quantity + 100 WHERE fruit_name = 'banana';"
}, 
{
    "step_num":6,
    "description":"Update the selling price of banana if given new selling price",
    "sql":"UPDATE fruits SET selling_price = 1.8 WHERE fruit_name = 'banana';"
}]
"""
eg_ask_sale = """
USER INPUT: Who bought 100kg apple on 2010-03-27 and what is he/she name, detailed information and costumer id?
ANSWER:
[{
    "step_num":1,
    "description":"Retrieve the customer information who made the purchase",
    "sql":"SELECT c.customer_id, c.first_name, c.last_name, c.phone_number, c.email FROM customers c JOIN sales s ON c.customer_id = s.customer_id JOIN sale_items si ON s.sale_id = si.sale_id JOIN fruits f ON si.fruit_id = f.fruit_id WHERE f.fruit_name = 'apple' AND si.quantity_sold = 100 AND s.sale_date = '2010-03-27';"
}]
"""
eg_if_new_customer_sale = """
USER INPUT: A customer named 'Chenzhuang Du' with a phone number as 120056 and e-mail as chenzhuang@gmail.com bought 10kg apple and 5kg pear on 2010-03-27.
ANSWER:
[{
    "step_num":1,
    "description":"Insert customer 'Chenzhuang Du' if not exists",
    "sql":"INSERT INTO customers (first_name, last_name, phone_number, email) SELECT 'Chenzhuang', 'Du', '120056', 'chenzhuang@gmail.com' WHERE NOT EXISTS (SELECT 1 FROM customers WHERE phone_number = '120056');"
}, 
{
    "step_num":2,
    "description":"Insert sale",
    "sql":"INSERT INTO sales (customer_id, sale_date, total_price) VALUES ((SELECT customer_id FROM customers WHERE phone_number = '120056'), '2010-03-27', (SELECT selling_price FROM fruits WHERE fruit_name = 'apple') * 10 + (SELECT selling_price FROM fruits WHERE fruit_name = 'pear') * 5);"
}, 
{
    "step_num":3,
    "description":"Insert sale item",
    "sql":"INSERT INTO sale_items (sale_id, fruit_id, quantity_sold, price_per_item, item_total_price) VALUES ((SELECT MAX(sale_id) FROM sales), (SELECT fruit_id FROM fruits WHERE fruit_name = 'apple'), 10, (SELECT selling_price FROM fruits WHERE fruit_name = 'apple'), (SELECT selling_price FROM fruits WHERE fruit_name = 'apple') * 10), ((SELECT MAX(sale_id) FROM sales), (SELECT fruit_id FROM fruits WHERE fruit_name = 'pear'), 5, (SELECT selling_price FROM fruits WHERE fruit_name = 'pear'), (SELECT selling_price FROM fruits WHERE fruit_name = 'pear') * 5);"
}, 
{
    "step_num":4,
    "description":"Update the stock quantity of apple and pear",
    "sql":"UPDATE fruits SET stock_quantity = CASE WHEN fruit_name = 'apple' THEN stock_quantity - 10 WHEN fruit_name = 'pear' THEN stock_quantity - 5 ELSE stock_quantity END WHERE fruit_name IN ('apple', 'pear');"
}]
"""
eg_delete_pro = """
USER INPUT: Because the customer returned the goods, roll back a sales record which is made by the customer with customer id as 8 on 2023-01-29.
ANSWER:
[{
    "step_num":1,
    "description":"Find the sale_id for this customer on this date",
    "sql":"SELECT sale_id FROM sales WHERE customer_id = 8 AND sale_date = '2023-01-29';"
}, 
{
    "step_num":2,
    "description":"Get all the fruit_id and quantity_sold for this sale, replace <sale_id> with the results from the previous queries",
    "sql":"SELECT fruit_id, quantity_sold FROM sale_items WHERE sale_id = <sale_id>;"
}, 
{
    "step_num":3,
    "description":"Increase the stock_quantity for each fruit sold in this sale, replace <quantity_sold> <fruit_id> with the results from the previous queries",
    "sql":"UPDATE fruits SET stock_quantity = stock_quantity + <quantity_sold> WHERE fruit_id = <fruit_id>;"
}, 
{
    "step_num":4,
    "description":"Delete the sale items for this sale, replace <sale_id> with the results from the previous queries",
    "sql":"DELETE FROM sale_items WHERE sale_id = <sale_id>;"
}, 
{
    "step_num":5,
    "description":"Delete the sale record, replace <sale_id> with the results from the previous queries",
    "sql":"DELETE FROM sales WHERE sale_id = <sale_id>;"
}]
"""


doctor_egs = """
原始问句：Alice Shaw的publication
SQLQuery:SELECT info FROM publications WHERE doctor_id = 'tom_123' AND type = 'publications'
SQLResult: [('Zou W, Yaung SJ, Fuhlbrück F, Ballinger M, Peters E, Palma JF, Shames DS, Gandara D, Jiang Y, Patil NS. ctDNA Predicts Overall Survival in Patients With NSCLC Treated With PD-L1 Blockade or With Chemotherapy. JCO Precis Oncol. 2021 Nov;5:827-838. doi:10.1200/PO.21.00057. PMID:34994614.',), ('Woo XY, Giordano J, Srivastava A, Zhao ZM, Lloyd MW, de Bruijn R, Suh YS, Patidar R, Chen L, Scherer S, Bailey MH, Yang CH, Cortes-Sanchez E, Xi Y, Wang J, Wickramasinghe J, Kossenkov AV, Rebecca VW, Sun H, Mashl RJ, Davies SR, Jeon R, Frech C, Randjelovic J, Rosains J, Galimi F, Bertotti A,...',), ('Radiation oncology,Thomas JS, El-Khoueiry AB, Maurer BJ, Groshen S, Pinski JK, Cobos E, Gandara DR, Lenz HJ, Kang MH, Reynolds CP, Newman EM. A phase I study of intravenous fenretinide (4-HPR) for patients with malignant solid tumors. Cancer Chemother Pharmacol. 2021 Apr;87(4):525-532....',), ('Stem cell (bone marrow) transplant,Sun H, Cao S, Mashl RJ, Mo CK, Zaccaria S, Wendl MC, Davies SR, Bailey MH, Primeau TM, Hoog J, Mudd JL, Dean DA 2nd, Patidar R, Chen L, Wyczalkowski MA, Jayasinghe RG, Rodrigues FM, Terekhanova NV, Li Y, Lim KH, Wang-Gillam A, Van Tine BA, Ma CX, Aft R, Fuh KC,...',), ('Riess JW, Reckamp KL, Frankel P, Longmate J, Kelly KA, Gandara DR, Weipert CM, Raymond VM, Keer HN, Mack PC, Newman EM, Lara PN Jr. Erlotinib and Onalespib Lactate Focused on EGFR Exon 20 Insertion Non-Small Cell Lung Cancer (NSCLC): A California Cancer Consortium Phase I/II Trial (NCI 9878)....',), ('Hematology and medical oncology,Gynecologic oncology,Hereditary cancer program,Pediatric oncology,Robotic surgery,Hirsch FR, Redman MW, Moon J, Agustoni F, Herbst RS, Semrad TJ, Varella-Garcia M, Rivard CJ, Kelly K, Gandara DR, Mack PC. EGFR High Copy Number Together With High EGFR Protein...',), ('Argiris A, Miao J, Cristea MC, Chen AM, Sands JM, Decker RH, Gettinger SN, Daly ME, Faller BA, Albain KS, Yanagihara RH, Garland LL, Byers LA, Wang D, Koczywas M, Redman MW, Kelly K, Gandara DR. A Dose-finding Study Followed by a Phase II Randomized, Placebo-controlled Trial of Chemoradiotherapy...',), ('Surgical oncology,Gadgeel S, Hirsch FR, Kerr K, Barlesi F, Park K, Rittmeyer A, Zou W, Bhatia N, Koeppen H, Paul SM, Shames D, Yi J, Matheny C, Ballinger M, McCleland M, Gandara DR. Comparison of SP142 and 22C3 Immunohistochemistry PD-L1 Assays for Clinical Efficacy of Atezolizumab in Non-Small...',), ('Ranganath H, Jain AL, Smith JR, Ryder J, Chaudry A, Miller E, Hare F, Valasareddy P, Seitz RS, Hout DR, Varga MG, Schweitzer BL, Nielsen TJ, Mullins J, Ross DT, Gandara DR, Vidal GA. Association of a novel 27-gene immuno-oncology assay with efficacy of immune checkpoint inhibitors in advanced...',), ('Gandara D, Reck M, Moro-Sibilot D, Mazieres J, Gadgeel S, Morris S, Cardona A, Mendus D, Ballinger M, Rittmeyer A, Peters S. Fast progression in non-small cell lung cancer: results from the randomized phase III OAK study evaluating second-line atezolizumab versus docetaxel. J Immunother Cancer....',)]
Answer:Alice Shaw的publication包括：Zou W, Yaung SJ, Fuhlbrück F, Ballinger M, Peters E, Palma JF, Shames DS, Gandara D, Jiang Y, Patil NS. ctDNA Predicts Overall Survival in Patients With NSCLC Treated With PD-L1 Blockade or With Chemotherapy. JCO Precis Oncol. 2021 Nov;5:827-838. doi:10.1200/PO.21.00057. PMID:34994614.；Woo XY, Giordano J, Srivastava A, Zhao ZM, Lloyd MW, de Bruijn R, Suh YS, Patidar R, Chen L, Scherer S, Bailey MH, Yang CH, Cortes-Sanchez E, Xi Y, Wang J, Wickramasinghe J, Kossenkov AV, Rebecca VW, Sun H, Mashl RJ, Davies SR, Jeon R, Frech C, Randjelovic J, Rosains J, Galimi F, Bertotti A,...；Radiation oncology,Thomas JS, El-Khou


原始问句：Alice Shaw的clinical trial
SQLQuery:SELECT brief_title FROM clinical_trials_detail WHERE doctor_id = 'tom_123';
SQLResult: [('Efficacy of Pegamotecan (PEG-Camptothecin) in Localized or Metastatic Cancer of the Stomach or Gastroesophageal Junction',)]
Answer:Alice Shaw的clinical trial是Efficacy of Pegamotecan (PEG-Camptothecin) in Localized or Metastatic Cancer of the Stomach or Gastroesophageal Junction.



原始问句：Alice Shaw的clinical trial和ID
SQLQuery:SELECT nct_no FROM clinical_trials_detail WHERE doctor_id = 'tom_123';
SQLResult: [('NCT00080002',)]
Answer:Alice Shaw的clinical trial ID是NCT00080002
127.0.0.1 - - [14/Jul/2023 10:08:47] "POST /sqa HTTP/1.1" 200 -



原始问句：Alice Shaw的NCT00080002的介绍
SQLQuery:SELECT brief_title FROM clinical_trials_detail WHERE doctor_id = 'tom_123' AND nct_no = 'NCT00080002';
SQLResult: [('Efficacy of Pegamotecan (PEG-Camptothecin) in Localized or Metastatic Cancer of the Stomach or Gastroesophageal Junction',)]
Answer:Alice Shaw的NCT00080002的介绍是Efficacy of Pegamotecan (PEG-Camptothecin) in Localized or Metastatic Cancer of the Stomach or Gastroesophageal Junction.


原始问句：Alice Shaw的NCT00080002的受试标准
SQLQuery:SELECT inclusion_criteria, exclusion_criteria FROM clinical_trials_detail WHERE doctor_id = 'tom_123' AND nct_no = 'NCT00080002'
SQLResult: [('\n                                            - Woman older than 18 years\n                                            Low-risk gestational trophoblastic neoplasia according to FIGO score (FIGO score ≤ 6) with indication of methotrexate as first line treatment\n                                     ...', '\n                                            Prior therapy with an anti-PD-1, anti-PD-L1, anti-PD-L2, anti-CD137, or anti- CTLA 4 antibody (including ipilimumab, tremelimumab or any other antibody or drug specifically targeting T-cell costimulation or immune checkpoint pathways).\n               ...')]
Answer:女性年龄超过18岁；低危妊娠滋养细胞肿瘤根据FIGO评分（FIGO评分≤6），其中指示甲基叶酸作为第一线治疗；先前接受过抗PD-1，抗PD-L1，抗PD-L2，抗CD137或抗CTLA 4抗体（包括ipilimumab，tremelimumab或任何其他特异性靶向T细胞共刺激或免疫检查点通路的抗体或药
"""


egs = [eg_ask_sale, eg_purchase, eg_if_new_customer_sale, eg_delete_pro]
# egs = [eg_if_new_customer_sale, doctor_egs]
