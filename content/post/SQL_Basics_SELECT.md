---
title: "SQL Basics: The SELECT Statement"
date: 2017-12-15
autoThumbnailImage: true
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1514069924/SQL_plain140_q0jiy9.svg
coverImage: https://res.cloudinary.com/wessport/image/upload/c_scale,h_1080,w_1920/v1513372413/mountain_sunset_iu7zey.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- SQL
- SQL basics
- SQL beginner
- SELECT statement
- Database

categories:
- Database

tags:
- SQL
- Database
- SQL Basics
---

Over the next few weeks I'm going to share some of the **SQL Basics** I've picked up. Hopefully, these posts will make **SQL** a little less intimidating for other beginners.

<!--more-->
## Structured Query Language ##

This past semester I was fortunate enough to find my way into a **Database Design and Development** course. Having struggled with **ArcMap SQL**  queries in the past, I decided to sharpen my data wrangling abilities by honing a few fundamental **SQL** skills.

**SQL** or **Structured Query Language** is the language we use to explore databases. It's a bit like a roadmap comprised of sequential directions. These directions outline exactly where we're going and what treasure (data) we're going to find. The directions can be simple or they can be very complex (looking at you subqueries in the FROM clause). After a little practice though, even complex statements can be mastered relatively quickly. With even a basic knowledge of **SQL**, you can do more than you might think. The hard part is defining what you actually want to retrieve from your database.

![A witty gif](https://media.giphy.com/media/3oKIPnuhcwE9tywW5y/giphy.gif)

------

## SELECT Statement ##

The **SELECT** statement is used to retrieve data from tables stored inside your database. Maybe you want to survey the contents of a customer table or perhaps you would like to pull customer data into another tool like **R** or **Python** for analysis. Either way, you're going to need a **SELECT** query.

The most basic **SELECT** statement requires two clauses.

```
SELECT BREWERY_NAME
FROM BREWERY;
```
| BREWERY_NAME                    |
| ------------------------------- |
| Yee-Haw Brewing Co.             |
| GREEN MAN BREWERY               |
| The Black Abbey Brewing Company |


The first clause is the **SELECT** clause. This is where you specify which **columns** (attributes) you want to retrieve using the '**SELECT**' keyword followed by the name(s) of the desired column.

The '**FROM**' keyword is used to specify the **table** you're selecting data from.

In this case I want to know the names of breweries in our example **BREWERY** table. I use a **SELECT** statement to request only the names of the breweries **FROM** the **BREWERY** table. Any other attributes in the **BREWERY** table are excluded because I didn't explicitly request them.

The semicolon '**;**' placed at the end of the line is used to designate the end of an **SQL** command. Every **SELECT** statement should conclude with a semicolon. We use the semicolon to distinguish multiple **SQL** commands from one another.

Formatting rules are not as strict as they are in other languages like **Python**. I could also structure my **SELECT** statement like this:

```
SELECT BREWERY_NAME FROM BREWERY;
```
| BREWERY_NAME                    |
| ------------------------------- |
| Yee-Haw Brewing Co.             |
| GREEN MAN BREWERY               |
| The Black Abbey Brewing Company |

Notice how the results are the same. More than one clause can be placed on the same line, however I like to keep clauses on separate lines for readability. Note that the order of the clauses is important. We will look at order of execution in more detail later.

If we want to look at multiple columns, it's as easy as adding a comma and the column name in our **SELECT** clause.

```
SELECT BREWERY_NAME, BREWERY_STATE
FROM BREWERY;
```
| BREWERY_NAME                    | BREWERY_STATE |
| ------------------------------- | ----- |
| Yee-Haw Brewing Co.             | TN    |
| GREEN MAN BREWERY               | NC    |
| The Black Abbey Brewing Company | TN    |

The order of the returned columns is dependent on the order you specify in your **SELECT** clause.

To view all of the columns in the **BREWERY** table, we need to use a **wildcard** '*'.

```
SELECT *
FROM BREWERY;
```
| BREWERY_ID | BREWERY_NAME                    | BREWERY_STATE | BREWERY_LICENSE |
|----------- | ------------------------------- | ----- | --------------- |
| 1000       | Yee-Haw Brewing Co.             | TN    | HK41/TFA        |
| 1001       | GREEN MAN BREWERY               | NC    | 3000-TBTL       |
| 1003       | The Black Abbey Brewing Company | TN    | DFTBA-10102017  |

Be conservative when using wildcards. Ask yourself do I really need to use a wildcard here? Requesting more columns than you need is generally inefficient and bad practice. Knowing when and when not to use a wildcard will become clearer once we add additional keyword clauses in the future.

As you might have guessed from our breweries example, **SQL** is not a cryptic language. It does its best to resemble regular English. This makes the syntax often times intuitive to the point where you can guess ahead of time the keyword you need based on the logic of your query. As a beginner, I enjoyed this aspect of the language the most. It helps tremendously when translating the logic behind your query into actual **SQL** code.

------
* **Disclaimer:** I learned SQL in an ORACLE Client environment. The syntax of my examples will follow ORACLE conventions. The core logic behind the code however should translate regardless of the database environment you're working in.
------

## To Sum It Up ##

When you need to interact with the database, you write a **SELECT** statement. Vary rarely do we want to look at entire columns of data as we did in the examples above. Typically we are interested in constraining our data. In the next post I'll get into how we can use the **WHERE** clause and special operators to make our **SELECT** queries even more useful.

------

## TL;DR ##

**SQL** is the language we use to retrieve data from a database. The **SELECT** statement is a structured query comprised of separate keyword clauses. The **SELECT** clause is used to request specified columns. The **FROM** clause designates from which table the columns originate.
