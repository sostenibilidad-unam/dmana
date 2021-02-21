# Agency Network Serializer

## Introduction

Agency Network Analylses (ANA) map the social action arena of people by
situating them relative to their collaborators and within their
problem space. This helps actors identify where they have agency in
the system, i.e. over what elements and through what relationships.

This mapping is done via a multi-part interview process during which
data is gathered about actors (their context, worplaces, type of
organization, etc.), their activities (practices, capacities), and
their relationships to other actors.

AgNeS is a database administration interface specially designed to
easily and sistematically gather data for agency network analyses.
Once data is loaded into database, agency networks can be visualized
in several ways, metrics from their structure can be easily computed,
or they can be exported to common standard formats for further
processing with other software.


## Database Architecture

In our ANA database, information is grouped into tables made up of rows
and columns, so that each row holds data for related items. For
example a "People" table has a row for each person with columns such
as "name", and "e-mail".

Links can be created that join different tables together. For example
the "People" table might be related to an "Organization" table, which
may have columns such as "organization name" and "street address".

![table scheme](../tables.png)

Constraints can be set on each column, so that only valid data can be
entered. This guarantees data consistency.

The resulting structure can be interrogated with great
flexibility. Using a specialized query language, any combination of
columns may be fetched by complex combinations of criteria.

We have developed a web application which allows users to easily
access these tables.

The following subsections describe the structure of each of the tables
we have designed, as well as the corresponding web forms for
filtering, vizualising, exporting and data input.

Of special interest are the "Edge" tables, which hold relationships
among nodes in the networks that make up the Agency Network Analysis.


### Data about people

In our data model people:
 - Can be distinguished as egos, which means they have been interviewed directly as part of the ANA method.
 - Are afiliated to an organization, through a link to an organizations table.
 - Represent an economy sector, which can be Academia, Government, Private enterprise, and Non-Governmental Organization.
 - Have an avatar name and avatar picture, which embodies their main powers and qualities.
 - Relate to "powers" by links to an "Avatar Powers" table.
 
A "description" field is included, where free text can be entered if additional information is necessary.

### Data about actions

People are involved in their problem space by taking actions. These
actions belong to different categories, by links to an Action
Categories table.

Actions are linked to people in the Agency Edgelist described below.

### Data about the perception-understanding of a system 

Variables which affect the problem space under study are kept in the
Cognitive map Variables table.

They are meant to be connected to form cognitive maps in the Cognitive
map Edgelist described below.


### Grouping data by project

A Project makes it possible to use the same nodes to create different
networks. This feature might be useful, e.g. in cases where a
researcher wishes to analyze the same agency network in two different
moments, or simply to use the same tool for different research
projects.

Edges in all networks always belong to a project, but nodes may be
shared. This makes it easy to create a new network based on previous
work: Edgelist tables allow the user to copy edges into new projects.


## Networks in an ANA

Complex networks are made up of nodes and edges. Nodes are things
being connected, edges are the links which connect them.

The main object of interest is the structure that results of
considering all nodes and edges together. However more nuance is
possible by storing arbitrary data in nodes and edges.

For example, in social networks described bellow nodes represent
people, and links represent collaboration relationships among
them. Each node holds all data related to a person, such as picture
and avatar name. And each edge holds data related to the
collaboration, such as influence and distance.

A common representation of a network is a list of edges. This is
easily achieved by tables that join other tables in our
database. These special tables are called Edgelists and there is one
for every type of network that makes up an Agency Network Analysis.


### Agency networks
	
### Social network
(person, person)

### Power network 
(avatar, power)
 
### Cognitive maps (variable, variable)

They are abstractions or internal representations of how a system works.

Examples: 

a) Cognitive Map of an academic

Here a picture of a cognitive map of the perception of
management and state of a natural protected area of the university
(with socio-political & biophysical variables)

b) Agency Network of a Laboratory that studies the Natural Protected Area-NPA (5 egos, each with 3-4 alters)

Show a picture of how they look after a SSI - what data they show

Egos: 

 1. Dr. Nigel (anthropologist)
 2. MSc. Mischa (Lab Tech)
 3. Dr. Sandra (biologist)
 4. Ms. Mirna, (sustainability student)
 5. Mr. Jared (CEO of an environmental NGO)

Alters:

 EGO1: MSc. Mischa, Mr. Jared, Dr. Repsa (head of the NPA)
 EGO2: Dr. Nigel, Dr. Sandra, Ms. Mirna
 EGO3: Ms. Mirna, Mr. Admin (permits for NPA), Dr. X (ecologist), Mr. Bugs (student)
 EGO4: Ms. Tutsi (user), Dr. Sandra
 EGO5: Dr. Nigel, Dr. Repsa, Mr. Green (International NGO), Mr. Admin, .... ??



## Outputs

### Exporting to common file formats

Any selected edgelist may be exported to the following formats:

 - GrahpML. This format is a variant of XML specialized in representing complex networks. Many programs are able to read it, specially Cytoscape.
 - Pajek's .net format. Pajek is a common tool for social network analyses.
 - GraphViz DOT format. There are many ways of visualizing a complex network, GraphViz is a specialized tool which includes many different strategies for network visualization.
 
### Network analysis report
 
Common metrics can be obtained in a spreadsheet for a selected network. 
 - Number of nodes
 - Number of edges
 - Network density
 - Netwok Clustering index
 - Average node connectivity
 
 
## Visualization


### Spring-embedded PDF

### Interactive spring-embedded

### Relationship Diagram PDF

### Hiveplot

### Adjacency Matrices Contrast Heatmap

