---
title: "The Five Normal Forms"
date: 2018-01-22
autoThumbnailImage: true
thumbnailImagePosition: left
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1516220273/grad_400_zviq8s.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1516211751/pexels-photo-373488_gw4wqr.jpg
metaAlignment: center
coverMeta: out
comments: true

keywords:
- Database
- Normalization
- Normal Forms
- design
- database 101
- normal form


categories:
- Database

tags:
- Database
- Normalization
- Normal forms
- Design
---
Rules for improving the integrity of your data tables through Normalization.

<!--more-->

---

## 1st Normal Form ##

A data table is in first normal form (1NF) when:

- A table consists of cells where each cell contains 1 and only 1 value
- The order doesn't matter. The position of the rows and also the columns shouldn't carry any significance
- No two rows are exactly alike
- The column/attribute names are unique
- The datatype of each column is consistent i.e. a column shouldn't contain cells with text and numerical values

## 2nd Normal Form ##

##### Functional Dependencies #####

Before we talk about the second normal form, we need to know what functional dependencies are.

A functional dependency exists when you can take a value from one attribute (or set of attributes) and use it to find the value of another.

The determinant attribute determines the value of the dependent attribute. In other words, it is the attribute you need first before you can link to the second attribute.

There are two common types of dependencies which give rise to the second and third normal forms.

##### 2nd Normal Form #####

Second normal form (2NF) is realized when there are no partial dependencies.

Partial dependencies exist when a part of the primary key can be used to determine the value of a non-key attribute.

For instance...

Partial dependencies can introduce integrity issues into your data tables.

For instance...

Partial dependencies can be addressed by creating a new table. Take the determinant in the troublesome partial dependency and copy it to a new table (think cmd-c). Then take the dependent attribute and cut it (cmd-x) to the new table you just created. It's important that you leave a copy of the determinant behind as a foreign key - otherwise you lose the relationship between the two tables.

If your table doesn't have a composite key, then technically it's already in 2NF by default as long as it's already in 1NF. You can't have a partial dependency if the primary key doesn't have multiple parts.



## 3rd Normal Form ##

For a table to be in third normal form (3NF), transitive dependencies must not exist.

Transitive dependencies occur when a non-key attribute (or set of attributes) determines another non-key attribute. Just like before, transitive dependencies create redundancy issues.

For instance...

To fix any existing transitive dependencies, we can use the same strategy we employed to put our tables into 2NF. Copy the determinants into a new table. Then cut the dependents into the new table you just created.

## Boyce Codd Normal Form ##

Boyce Codd Normal Form (BCNF) is at first glance a reverse of the Second Normal Form. You're essentially removing dependencies in the opposite direction now.

A table is in BCNF when there are no non-key attributes that determine part of a composite-key attribute. In a composite key, every partial-key attribute can only depend on a superkey.

For a more technical breakdown of the difference between 3NF and BCNF, check out this discussion: [Data depends on the key [1NF], the whole key [2NF] and nothing but the key [3NF]](https://stackoverflow.com/questions/8437957/difference-between-3nf-and-bcnf-in-simple-terms-must-be-able-to-explain-to-an-8).

## 4th Normal Form ##

Fourth normal form is achieved when a table meets the requirements of the 1-3NF as well as BCNF, and all existing multivalued facts have been separated into their own tables.

Multivalued dependency occurs when an attribute can determine multiple facts about more than one independent attributes.

For instance...

This leads to formatting and update problems where multiple changes might have to be made across the table when updating records.

To circumvent these issues, each multivalued fact/dependency should be put into its own table consisting of the determinant and dependent - pairwise decomposition.

## 5th Normal Form ##

A table is in fifth normal form when it cannot be further subdivided into smaller tables.

If you can reconstruct your original table from several smaller tables, then you haven't reached 5th normal form.

Firth normal form alleviates redundancies that we could not address up to this point with pairwise decomposition which is essentially just breaking a table up into two smaller tables. Three or more smaller tables maybe necessary to achieve 5NF. The greater amount of attributes you have, the greater number of possible table decompositions. This is what makes 5NF challenging to put into practice. Interestingly removing even a single row in your original table could change whether your smaller tables successfully reconstruct.

## In Closing ##
