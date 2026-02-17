---
title: "Graph Database Prototype for Location Data"
author: "Wes"
date: 2021-09-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Neo4j
- Graph Database
- Location Data
- Cypher

categories:
- Data Engineering

tags:
- neo4j
- graph-database
- prototyping
---

*Exploring whether a graph database could better model complex geographic hierarchies.*

<!--more-->

---

# The Problem with Hierarchies #

Location data is inherently hierarchical. Countries contain admin1 regions, which contain admin2 regions, which contain cities, which contain postal codes. Simple enough.

Except it isn't. Real-world geographic hierarchies are messy:

- Some countries have 4 levels of administrative divisions, some have 2
- Cities can span multiple admin2 regions
- Postal codes can cross city boundaries
- Metropolitan areas don't align with administrative boundaries

Our relational database handled the common cases well. The edge cases required workarounds — duplicate records, special-case logic, manual overrides. International markets with more nuanced hierarchies were particularly problematic.

---

# Why Graph Databases #

Graph databases model relationships as first-class citizens. Instead of foreign keys and join tables, you have nodes and edges with properties.

For location data, this means:

```
(Country)-[:CONTAINS]->(Admin1)-[:CONTAINS]->(Admin2)-[:CONTAINS]->(City)
```

But also:

```
(City)-[:OVERLAPS]->(Admin2_A)
(City)-[:OVERLAPS]->(Admin2_B)
```

The relational model struggles with "a city can belong to multiple admin2 regions." The graph model handles it naturally with multiple relationship edges.

---

# Building the Prototype #

I built the prototype independently using Friday afternoon personal development time, using Neo4j and Cypher query language. The initial dataset was a subset of our location database — Japan, a country with complex administrative divisions:

```cypher
// Create country node
CREATE (jp:Country {name: 'Japan', code: 'JP'})

// Create prefecture (admin1) nodes
CREATE (tokyo:Admin1 {name: 'Tokyo', code: '13'})
CREATE (osaka:Admin1 {name: 'Osaka', code: '27'})

// Create relationships
CREATE (jp)-[:CONTAINS]->(tokyo)
CREATE (jp)-[:CONTAINS]->(osaka)

// City that spans multiple wards
CREATE (shibuya:City {name: 'Shibuya'})
CREATE (tokyo)-[:CONTAINS]->(shibuya)
```

---

# Querying Hierarchies #

The graph model made hierarchy queries more intuitive:

```cypher
// Find all locations within Tokyo, any depth
MATCH (tokyo:Admin1 {name: 'Tokyo'})-[:CONTAINS*]->(location)
RETURN location.name, labels(location)

// Find the full path from a postal code to country
MATCH path = (postal:Postal {code: '150-0001'})<-[:CONTAINS*]-(country:Country)
RETURN [node IN nodes(path) | node.name] AS hierarchy
```

In the relational model, variable-depth hierarchy queries required recursive CTEs or multiple queries. In Neo4j, it's a single pattern match.

---

# Handling Edge Cases #

The prototype explored several edge cases that were problematic in our relational model:

| Edge Case | Relational Approach | Graph Approach |
|-----------|---------------------|----------------|
| City spans multiple admin2s | Duplicate city records | Multiple OVERLAPS edges |
| Postal code crosses boundaries | Pick one parent arbitrarily | Multiple CONTAINS edges |
| Metropolitan areas | Separate lookup table | PART_OF relationship type |

---

# Demo at Research Meeting #

I presented the prototype at our July research meeting. The demo showed:

1. How the graph model represented complex hierarchies
2. Query examples that were simpler than SQL equivalents
3. Visualization of location relationships in the Neo4j browser

The response was interested but cautious. Key questions came up:

- Migration path from existing relational data
- Performance characteristics at production scale
- Team familiarity with Cypher query language
- Integration with existing services

All valid concerns. This was a prototype, not a production proposal.

---

# The Opportunity Document #

Following the demo, I drafted an opportunity document outlining potential benefits:

**Internal Benefits:**
- Simpler handling of complex hierarchies
- Natural support for international markets with different administrative structures
- Reduced special-case logic in application code

**Product Benefits:**
- More accurate location resolution for edge cases
- Better support for "near" queries and geographic relationships
- Foundation for future features like neighborhood boundaries

**Risks and Unknowns:**
- Significant migration effort
- Team training requirements
- Performance at scale untested
- Operational complexity of running Neo4j

---

# What Came of It #

The prototype didn't lead to a production migration. The risk-reward calculation didn't favor it given other priorities.

But the work wasn't wasted:

1. The team had a shared reference point for discussing graph database concepts
2. The opportunity document became useful when similar questions came up later
3. I gained hands-on experience with Neo4j that proved useful in other contexts

Sometimes prototypes lead to production systems. Sometimes they inform decisions to stay the course. Both are valuable outcomes.

---

# Technical Notes #

For anyone interested in trying something similar, the key Neo4j concepts:

```cypher
// Node creation with labels and properties
CREATE (n:Label {property: 'value'})

// Relationship creation
CREATE (a)-[:RELATIONSHIP_TYPE {property: 'value'}]->(b)

// Variable-length path matching
MATCH (start)-[:CONTAINS*1..5]->(end)

// Path functions
MATCH path = shortestPath((a)-[*]-(b))
RETURN length(path), nodes(path)
```

The Cypher query language has a learning curve, but it's well-documented and the Neo4j browser provides excellent interactive exploration.
