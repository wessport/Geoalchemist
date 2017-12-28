---
title: "SQL Basics: The WHERE clause"
date: 2017-12-28
autoThumbnailImage: true
thumbnailImagePosition: left
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1514073271/SQL_bw_400_dz3urm.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1514486830/macbook_qwzedr.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- SQL
- SQL basics
- SQL beginner
- SQL Operators
- WHERE clause
- Database

categories:
- Database

tags:
- SQL
- Database
- SQL Basics
---

Working with the **WHERE** clause and **SQL operators** to refine data requests.

<!--more-->

In my last post I covered the basics of the `SELECT` statement and what exactly Structured Query Language (**SQL**) is. In today's post, we're adding a new clause to the `SELECT` statement that will allow us to refine our data requests. If this is your first introduction to **SQL**, I recommend you check out my previous post which you can find [here](/2017/12/sql-basics-the-select-statement/).


## The WHERE Clause ##
*Oh WHERE, oh WHERE can my data be?* - Eddie Vedder, Pearl Jam lead singer and SQL enthusiast.

![Portlandia Eddie Vedder](https://media.giphy.com/media/lXo6htNUAqMgM/giphy.gif)

Okay so [Eddie Vedder](https://www.youtube.com/watch?v=LJsEpNIY5IA) probably isn't an SQL enthusiast, but if he were, I'd bet he would be a big fan of the `WHERE` clause.

Put simply, the `WHERE` clause is used to filter rows in a table. When we want to limit the number of rows returned based on a condition or set of conditions, we use the `WHERE` clause.

Remember our `BREWERY` table from last time?

```
SELECT *
FROM BREWERY;
```
| BREWERY_ID | BREWERY_NAME                    | BREWERY_STATE | BREWERY_LICENSE |
|------------|---------------------------------|---------------|-----------------|
| 1000       | Yee-Haw Brewing Co.             | TN            | HK41/TFA        |
| 1001       | GREEN MAN BREWERY               | NC            | 3000-TBTL       |
| 1003       | The Black Abbey Brewing Company | TN            | DFTBA-10102017  |
| 1004       | New Belgium Brewing Company     | NC            | FT/21CRAV       |
| 1005       | Wicked Weed Brewing             | NC            | WWB-28801       |
| 1006       | BURIAL BEER CO.                 | NC            | 40-COLAV        |
| 1007       | Bearded Iris Brewing            | TN            | NASH/615        |
| 1008       | TWIN LEAF BREWERY               | NC            | 144/COX         |
| 1009       | CRAFTY BASTARD BREWING          | TN            | 865-37917       |
| 1010       | Highland Brewing Company        | NC            | 28803- HBC      |

Let's say we're planning a trip to Asheville, NC, a town known for its eccentric style and thriving beer scene. Before we drive up into the mountains to sample some brews, we would like to know what breweries we can potentially visit in NC. Now we could use `SELECT * FROM BREWERY` and scroll through our table searching for breweries where the value for the `BREWERY_STATE` attribute is `TN` or we could use the `WHERE` clause.

```
SELECT *
FROM BREWERY
WHERE BREWERY_STATE = 'TN';
```

| BREWERY_ID | BREWERY_NAME                    | BREWERY_STATE | BREWERY_LICENSE |
|------------|---------------------------------|---------------|-----------------|
| 1001       | GREEN MAN BREWERY               | NC            | 3000-TBTL       |
| 1004       | New Belgium Brewing Company     | NC            | FT/21CRAV       |
| 1005       | Wicked Weed Brewing             | NC            | WWB-28801       |
| 1006       | BURIAL BEER CO.                 | NC            | 40-COLAV        |
| 1008       | TWIN LEAF BREWERY               | NC            | 144/COX         |
| 1010       | Highland Brewing Company        | NC            | 28803- HBC      |

Maybe instead of looking at a list of all of the breweries in NC, we want to look up a specific brewery we heard about to check and see if it's located in NC.

{{< alert warning >}}
Note that the state abbreviation is in single quotation marks signifying that 'TN' is of the `string` data type.
{{< /alert >}}

```
SELECT *
FROM BREWERY
WHERE BREWERY_NAME = 'GREEN MAN BREWERY';
```
| BREWERY_ID | BREWERY_NAME                    | BREWERY_STATE | BREWERY_LICENSE |
|------------|---------------------------------|---------------|-----------------|
| 1001       | GREEN MAN BREWERY               | NC            | 3000-TBTL       |


Be sure to pay special attention to the case of your string conditions inside your `WHERE` clause. Had we tried to use `WHERE BREWERY_NAME = 'Green Man Brewery';`  our return would have been empty because in the `BREWERY` table, "GREEN MAN BREWERY" is in all caps. If we are unsure of the case of the string value we are searching for inside a particular table, most DBMS have text manipulation functions such as `UPPER` and `LOWER` that we can use to temporarily convert text to one case or another.

{{< alert [classes] >}}
Database Management System (DBMS) is the software used to manage a database and the engine for executing your SQL queries. For example Oracle, PostgreSQL, MySQL, etc.
{{< /alert >}}

```
SELECT BREWERY_ID, BREWERY_NAME, BREWERY_STATE, BREWERY_LICENSE
FROM BREWERY
WHERE LOWER(BREWERY_NAME) = 'green man brewery';
```
| BREWERY_ID | BREWERY_NAME                    | BREWERY_STATE | BREWERY_LICENSE |
|------------|---------------------------------|---------------|-----------------|
| 1001       | GREEN MAN BREWERY               | NC            | 3000-TBTL       |

Because we only included the text manipulation function `LOWER` in the where clause and not in the `SELECT ` clause, the "GREEN MAN BREWERY" was returned in its default case instead of lower case.

Sometimes we don't have an exact value we're looking for. In those search cases we need to use conditional operators.

{{< alert info >}}
The `WHERE` clause can also be used with `UPDATE`, `INSERT`, and `DELETE` commands, but more on this later.
{{< /alert >}}

------

## Conditional Operators ##

Conditional operators allow us to expand our search criteria beyond exact values.

Here are some of the most common conditional operators you'll encounter.

| Operator | Description              |
|----------|--------------------------|
| =        | Equality                 |
| >        | Greater than             |
| <        | Less than                |
| >=       | Greater than or equal to |
| <=       | Less than or equal to    |
| <>       | Not equal                |
| !<>      | Not equal                |
| BETWEEN  | Between two values       |
| IS NULL  | Contains a NULL value    |

{{< alert info >}}
`NULL` stands for *no value*. They are **empty** fields. Empty here means no spaces, no placeholder values like -9999 - nothing. `NULL` values typically occur in our data when we don't know the actual value of a field (cell) within our data table so we leave it blank.
{{< /alert >}}

If we wanted to find brewery IDs where the BREWERY_ID is between 1002 and 1005, we would write our query like this:

```
SELECT BREWERY_ID
FROM BREWERY
WHERE BREWERY_ID BETWEEN 1002 AND 1005;
```

| BREWERY_ID | BREWERY_NAME                    | BREWERY_STATE | BREWERY_LICENSE |
|------------|---------------------------------|---------------|-----------------|
| 1003       | The Black Abbey Brewing Company | TN            | DFTBA-10102017  |
| 1004       | New Belgium Brewing Company     | NC            | FT/21CRAV       |
| 1005       | Wicked Weed Brewing             | NC            | WWB-28801       |

The `WHERE` clause in this example actually uses two operators. The `AND` in this statement is actually an operator itself.

------

## Logical Operators ##

| Logic Operator | Description                                               |
|----------------|-----------------------------------------------------------|
| AND            | Return only rows that meet all conditions                 |
| OR             | Return rows that meet either condition                    |
| NOT            | Return only rows that do not meet the specified condition |

Logic operators allow you to combine more than one search condition at a time. For instance if we want to limit our results for breweries where the BREWERY_ID is 1005 and the state is NC our query would use the `AND` logic operator. If we wanted to return a list of breweries located in NC or TN we would use the `OR` operator. The nice thing about logic operators in **SQL** is that they're pretty intuitive.

For practice let's write a query with multiple conditions. Let's say we want to look at breweries in either `NC` or `TN` where the `BREWERY_ID` is greater than `1005`.

```
SELECT *
FROM BREWERY
WHERE BREWERY_STATE = 'NC' OR BREWERY_STATE = 'TN' AND BREWERY_ID > 1005;
```
| BREWERY_ID | BREWERY_NAME                    | BREWERY_STATE | BREWERY_LICENSE |
|------------|---------------------------------|---------------|-----------------|
| 1001       | GREEN MAN BREWERY               | NC            | 3000-TBTL       |
| 1004       | New Belgium Brewing Company     | NC            | FT/21CRAV       |
| 1005       | Wicked Weed Brewing             | NC            | WWB-28801       |
| 1006       | BURIAL BEER CO.                 | NC            | 40-COLAV        |
| 1007       | Bearded Iris Brewing            | TN            | NASH/615        |
| 1008       | TWIN LEAF BREWERY               | NC            | 144/COX         |
| 1009       | CRAFTY BASTARD BREWING          | TN            | 865-37917       |
| 1010       | Highland Brewing Company        | NC            | 28803- HBC      |

Hmm. Was this the table you were expecting? Looks like we've got NC breweries where the IDs is below 1005 even though we requested only IDs above 1005. Let's look closely at what's actually going on here.

The order in which the operators are evaluated is causing us trouble. In most DBMS environments, the `AND` operator is executed first. This means that in our example above, *any breweries located in TN and with a BREWERY_ID > 1005 are returned, and any breweries located in NC regardless of their ID*. To fix this problem we just need to be more specific. By adding parentheses around our conditions, we can control the order in which they're evaluated. Think of your old TI-83 calculator days.

```
SELECT *
FROM BREWERY
WHERE (BREWERY_STATE = 'NC' OR BREWERY_STATE = 'TN') AND BREWERY_ID > 1005;
```

| BREWERY_ID | BREWERY_NAME                    | BREWERY_STATE | BREWERY_LICENSE |
|------------|---------------------------------|---------------|-----------------|
| 1005       | Wicked Weed Brewing             | NC            | WWB-28801       |
| 1006       | BURIAL BEER CO.                 | NC            | 40-COLAV        |
| 1007       | Bearded Iris Brewing            | TN            | NASH/615        |
| 1008       | TWIN LEAF BREWERY               | NC            | 144/COX         |
| 1009       | CRAFTY BASTARD BREWING          | TN            | 865-37917       |
| 1010       | Highland Brewing Company        | NC            | 28803- HBC      |


------

## To Sum It Up ##

The `WHERE` clause should be used whenever you need to constrain your data. Conditional operators can help you further refine your queries beyond exact matches, and if you find you need multiple conditions, include logic operators such as `AND` and `OR`. In the next post of the **SQL BASICS** series, we'll continue expanding our SQL toolkit. I'll go into how grouping rows in or data tables using the `GROUP BY` clause can be handy and how to sort our returned rows using the `ORDER BY` clause.
