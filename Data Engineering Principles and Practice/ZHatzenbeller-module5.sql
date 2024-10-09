-- Part A: Select

-- 1A
SELECT * FROM humanresources.employee

-- 2A
SELECT businessentityid, persontype, firstname, lastname 
FROM person.person

-- 3A
SELECT DISTINCT *
FROM humanresources.employee
WHERE jobtitle LIKE '%Manager%'
   OR jobtitle LIKE '%Supervisor%'
   OR jobtitle LIKE '%Chief%'
   OR jobtitle LIKE '%Vice President%'

-- 4A
SELECT *
FROM production.product
WHERE sellstartdate >= '2013-01-01 00:00:00' 
  AND sellstartdate <= '2013-06-30 00:00:00'
ORDER BY name



-- Part B: Joins

-- 1B
SELECT p.firstname, p.lastname, e.jobtitle
FROM person.person AS p
JOIN humanresources.employee AS e
ON p.businessentityid = e.businessentityid

-- 2B
SELECT p.firstname, p.lastname, e.jobtitle, em.emailaddress
FROM person.person AS p
JOIN humanresources.employee AS e
ON p.businessentityid = e.businessentityid
JOIN person.emailaddress AS em
ON p.businessentityid = em.businessentityid



-- Part C: Group by Aggregation

-- 1C
SELECT color, COUNT(*) AS color_count
FROM production.product
WHERE color IS NOT NULL
GROUP BY color
ORDER BY color_count DESC

-- 2C
SELECT color,  finishedgoodsflag, COUNT(*) AS color_count
FROM production.product
WHERE color IS NOT NULL
GROUP BY color, finishedgoodsflag
ORDER BY color_count DESC

-- 3C
SELECT color, finishedgoodsflag, COUNT(*) AS color_count
FROM production.product
WHERE color IS NOT NULL
GROUP BY color, finishedgoodsflag
HAVING COUNT(*) > 25
ORDER BY color_count DESC;

-- 4C
SELECT 
    pc.name AS category_name, 
    ROUND(SUM(soh.freight), 2) AS freight_sum
FROM 
    sales.salesorderheader AS soh
JOIN 
    sales.salesorderdetail AS sod
    ON soh.salesorderid = sod.salesorderid
JOIN 
    production.product AS pp
    ON sod.productid = pp.productid
JOIN 
    production.productsubcategory AS psc
    ON pp.productsubcategoryid = psc.productsubcategoryid
JOIN 
    production.productcategory AS pc
    ON psc.productcategoryid = pc.productcategoryid
GROUP BY 
    pc.name
ORDER BY 
    freight_sum DESC



-- Part D: CASE Statements and Date

-- 1D
SELECT firstname, lastname, (CURRENT_DATE - hiredate)/365 AS years_of_service,
CASE
	WHEN (CURRENT_DATE - hiredate)/365 >= 15 THEN 'Fully Vested'
	WHEN (CURRENT_DATE - hiredate)/365 >= 10 THEN 'Partially Vested'
	ELSE 'Unvested'
END AS vesting_type
FROM person.person AS p
JOIN humanresources.employee AS e
ON p.businessentityid = e.businessentityid
