---
title: "The Five Normal Forms"
date: 2018-01-28
autoThumbnailImage: true
thumbnailImagePosition: left
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1517087773/5NormalForms_ls5glx.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1517089330/5NF_bg_ltoau5.png
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Database
- Normalization
- Normal Forms
- design
- database 101
- normal form
- the five normal forms


categories:
- Database

tags:
- Database
- Normalization
- Normal forms
- Design
---
*Simple rules for improving the integrity of your data tables through Normalization.*

<!--more-->

---

If you're like me when you get a new dataset on your hands, the first thing you want to do is throw it into one giant table and start analyzing it. Historically table design (table structure) hasn't always been at the top of my priority list. As long as I could find what I needed I was happy.

Inevitably at some point in a project however I would need to perform updates. This is where poor design always came back to haunt me. Simple updates could require all kinds of complex filtering and sorting to ensure I accurately updated each field.

Do to the nature of putting all of my data into one table, I had unintentionally introduced rampant redundancy. Even simple updates or deletes became annoying timesinks and always left me questioning - did I really update everything I was supposed to?

![A witty gif](https://media.giphy.com/media/P9RRyBd6ABYJi/giphy.gif)

By adhering to the Five Normal Forms it's possible to weed out most redundancy issues.

{{< alert success no-icon >}}
**Normalization -** a process of systematically reducing redundancy in data tables.
{{< /alert >}}

## 1st Normal Form ##

A data table is in first normal form (1NF) when:

##### A table consists of cells where each cell contains 1 and only 1 value #####

   This means you cannot have multiple values stored in a single cell like in the example table below.

<!--Table1-->
{{< image classes="fancybox center fig-100" src="https://res.cloudinary.com/wessport/image/upload/v1517091714/Table1_blhf5c.png" thumbnail="https://res.cloudinary.com/wessport/image/upload/v1517091714/Table1_blhf5c.png" title="Table 1">}}

##### The order doesn't matter #####

   The position of the rows and also the columns shouldn't carry any significance. If they do, you have implicit information in the table order that should be made explicit by creating a new attribute. For instance if the priority of the data is indicated by the order it appears in the table, then a new attribute should be created to indicate priority. This makes future maintenance easier.


##### No two rows are exactly alike #####

   This constraint makes sense given that we’re trying to reduce redundancy as much as possible.

##### The column/attribute names are unique #####

   Say for instance you need to update the name of a coffee in your coffee database. If there are two columns named ‘Coffee_Name’ which one should you update – both? This leads to data integrity issues and makes it more difficult to reference columns reliably.

##### The datatype of each column is consistent #####

  A column shouldn't contain cells with text **and** numerical values. Columns with multiple datatypes can produce unexpected results when attempting to calculate numerical values or search text leading to integrity issues and future headaches.

---

## 2nd Normal Form ##

##### Functional Dependencies #####

Before we talk about the second normal form, we need to know what functional dependencies are.

A functional dependency exists when you can take a value from one attribute (or set of attributes) and use it to find the value of another.

The determinant attribute determines the value of the dependent attribute. In other words, it is the attribute you need first before you can link to the second attribute.

There are two common types of dependencies which give rise to the second and third normal forms.

##### 2nd Normal Form #####

Second normal form (2NF) is realized when there are no partial dependencies.

{{< alert success no-icon >}}
**Partial dependencies** exist when a part of the primary key can be used to determine the value of a non-key attribute.
{{< /alert >}}

For instance in the example table below a partial dependency exists between `Coffee_ID` and `Coffee_Name`.

<!--Table2-->
{{< image classes="fancybox center fig-100" src="https://res.cloudinary.com/wessport/image/upload/v1517091921/Table2_ldxmwq.png" thumbnail="https://res.cloudinary.com/wessport/image/upload/v1517091921/Table2_ldxmwq.png" title="Table 2">}}

Partial dependencies can introduce integrity issues into your data tables.

For instance every time we store data concerning the `Coffee_ID`, we also repeatedly include the `Coffee_Name`. If we decide to rebrand a particular coffee and introduce a new name later on, every old name of the rebranded coffee has to be replaced. Furthermore, if we currently don’t have a particular coffee on hand, when we lose that `Coffee_ID` value we also lose the name of the coffee.

Partial dependencies can be addressed by creating a new table. Take the determinant in the troublesome partial dependency and copy it to a new table (think cmd-c). Then take the dependent attribute and cut it (cmd-x) to the new table you just created.

{{< alert warning no-icon >}}
It's important that you leave a copy of the determinant behind as a foreign key - otherwise you lose the relationship between the two tables.
{{< /alert >}}

<br>

<!--Table3-->
{{< image classes="fancybox center fig-100" src="https://res.cloudinary.com/wessport/image/upload/v1517092035/Table3_jkysab.png" thumbnail="https://res.cloudinary.com/wessport/image/upload/v1517092035/Table3_jkysab.png" title="Table 3">}}

<!--Table4-->
{{< image classes="fancybox center fig-100" src="https://res.cloudinary.com/wessport/image/upload/v1517092035/Table4_sr10pg.png" thumbnail="https://res.cloudinary.com/wessport/image/upload/v1517092035/Table4_sr10pg.png" title="Table 4">}}


{{< pullquote left >}}
If your table doesn't have a composite key, then technically it's already in 2NF by default as long as it's already in 1NF. You can't have a partial dependency if the primary key doesn't have multiple parts.
{{< /pullquote >}}

<p>
</p>

---


## 3rd Normal Form ##

For a table to be in third normal form (3NF), transitive dependencies must not exist.

Transitive dependencies occur when a single non-key attribute determines another non-key attribute. Sets of attributes that can determine another single attribute do not count. Just like before, transitive dependencies create redundancy issues.

For example in the table below a transitive dependency exists between `Roaster_ID` and `Roaster_Name`.

<!--Table5-->
{{< image classes="fancybox center fig-100" src="https://res.cloudinary.com/wessport/image/upload/v1517092390/Table5_q5weug.png" thumbnail="https://res.cloudinary.com/wessport/image/upload/v1517092390/Table5_q5weug.png" title="Table 5">}}

To fix any existing transitive dependencies, we can use the same strategy we employed to put our tables into 2NF. Copy the determinants into a new table. Then cut the dependents into the new table you just created.

{{< image classes="fancybox center fig-100" src="https://res.cloudinary.com/wessport/image/upload/v1517092390/Table6_v6hnxm.png" thumbnail="https://res.cloudinary.com/wessport/image/upload/v1517092390/Table6_v6hnxm.png" title="Table 6">}}

{{< image classes="fancybox center fig-100" src="https://res.cloudinary.com/wessport/image/upload/v1517092390/Table7_qptxlg.png" thumbnail="https://res.cloudinary.com/wessport/image/upload/v1517092390/Table7_qptxlg.png" title="Table 7">}}

##### Boyce Codd Normal Form (3.5 NF) #####

Boyce Codd Normal Form (BCNF) is at first glance a reverse of the Second Normal Form. You're essentially removing dependencies in the opposite direction now.

A table is in BCNF when there are no non-key attributes that determine part of a composite-key attribute. In a composite key, every partial-key attribute can only depend on a superkey.

For a more technical breakdown of the difference between 3NF and BCNF, check out this discussion: [Data depends on the key [1NF], the whole key [2NF] and nothing but the key [3NF]](https://stackoverflow.com/questions/8437957/difference-between-3nf-and-bcnf-in-simple-terms-must-be-able-to-explain-to-an-8).

---

## 4th Normal Form ##

Fourth normal form is achieved when a table meets the requirements of the 1-3NF as well as BCNF, and all existing multivalued facts have been separated into their own tables.

Multivalued dependency occurs when an attribute can determine multiple facts about more than one independent attributes.

This leads to formatting and update problems where multiple changes might have to be made across the table when updating records.

To circumvent these issues, each multivalued fact/dependency should be put into its own table consisting of the determinant and dependent - pairwise decomposition.

---

## 5th Normal Form ##

A table is in fifth normal form when it cannot be further subdivided into smaller tables.

If you can reconstruct your original table from several smaller tables, then you haven't reached 5th normal form.

Firth normal form alleviates redundancies that we could not address up to this point with pairwise decomposition which is essentially just breaking a table up into two smaller tables.

Three or more smaller tables maybe necessary to achieve 5NF. The greater amount of attributes you have, the greater number of possible table decompositions.

This is what makes 5NF challenging to put into practice.

Interestingly removing even a single row in your original table could change whether your smaller tables successfully reconstruct.

---
{{< image classes="fancybox center fig-100" src="https://res.cloudinary.com/wessport/image/upload/c_scale,w_350/v1517156729/5NormalForms_color_sb5c2i.png" thumbnail="https://res.cloudinary.com/wessport/image/upload/c_scale,w_350/v1517156729/5NormalForms_color_sb5c2i.png">}}


If you've made it to this point, you might have noticed that the solution to every problem thus far has been to create a new table. That's the nature of Normalization. Reduce redundancy but increase the number of tables you have to keep up with. This can make your database feel cumbersome.

Normalizing all of your tables may be the *perfect* solution but [is it the right solution for your operational requirements](http://sqlblog.com/blogs/louis_davidson/archive/2010/04/29/can-you-over-normalize.aspx)?

If the data your working with is mission critical - lives are on the line - then normalizing all your tables to 5th NF is probably the way you want to go. Maybe your requirements are not as dire however and you're comfortable sitting at 3rd NF.

Normalizing to 3rd NF is what I typically shoot for. After 3rd NF, the effort invested is a lot greater than the return. The power of the Normal Forms is that they are applicable even if your data lives outside a database - say in a Shapefile attribute table or Excel spreadsheet.

Eliminating redundancy may not always be possible, but controlling it is key to protecting the integrity of your data.
