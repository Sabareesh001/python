# Task 3: Lightweight ORM Implementation

## Overview

A lightweight Object-Relational Mapping (ORM) library that abstracts SQLite database operations using Python descriptors and field definitions. Provides a simple yet functional interface for defining models, creating tables, and performing CRUD operations without writing raw SQL.

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install sqlite3
```

*Note: sqlite3 is included in Python's standard library, so explicit installation is optional.*

### 3. Run the Demo

```bash
python main.py
```

This will:
- Initialize the SQLite database (`app.db`)
- Create tables for User, Post, and Product models
- Display schema information

## Features

- **Field Descriptors**: Custom field types with validation (CharField, IntegerField, FloatField, DateField)
- **Table Management**: Automatic table creation from model definitions
- **Field Constraints**: Support for nullable, unique, and primary key constraints
- **Type Safety**: Basic type checking for field values
- **Simple API**: Intuitive model definition syntax

## Architecture

- **main.py**: Model definitions and demo application
- **orm.py**: Core ORM implementation including:
  - `Field` base class
  - Field type implementations (CharField, IntegerField, FloatField, DateField)
  - `Model` metaclass for automatic table generation
  - Database initialization and connection management
  - (Future) CRUD operation methods

## Example Usage

```python
from orm import Model, CharField, IntegerField, init_db

init_db("app.db")

class User(Model):
    name = CharField(max_length=100)
    email = CharField(max_length=255, unique=True)
    age = IntegerField(nullable=True)

User.create_table()
```
