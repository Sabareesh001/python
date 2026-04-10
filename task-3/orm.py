import sqlite3
from typing import Any, List, Dict, Optional, Type

# Database connection
_db_connection = None
_db_cursor = None

def init_db(db_name="database.db"):
    """Initialize the database connection"""
    global _db_connection, _db_cursor
    _db_connection = sqlite3.connect(db_name)
    _db_cursor = _db_connection.cursor()
    _db_connection.row_factory = sqlite3.Row
    print(f"Connected to database: {db_name}\n")
    return _db_connection, _db_cursor

def get_connection():
    """Get the database connection"""
    global _db_connection, _db_cursor
    if _db_connection is None:
        init_db()
    return _db_connection, _db_cursor

# ============= Field Descriptors =============

class Field:
    """Base field descriptor"""
    def __init__(self, nullable=False, unique=False, primary_key=False):
        self.nullable = nullable
        self.unique = unique
        self.primary_key = primary_key
        self.name = None
        self.value = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, None)
    
    def __set__(self, obj, value):
        obj.__dict__[self.name] = value
    
    def get_sql_type(self):
        """Return SQL type definition"""
        raise NotImplementedError
    
    def get_sql_definition(self):
        """Return full SQL column definition"""
        sql = self.get_sql_type()
        if self.unique:
            sql += " UNIQUE"
        if not self.nullable and not self.primary_key:
            sql += " NOT NULL"
        return sql

class CharField(Field):
    """String field"""
    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
    
    def get_sql_type(self):
        return f"VARCHAR({self.max_length})"

class IntegerField(Field):
    """Integer field"""
    def get_sql_type(self):
        if self.primary_key:
            return "INTEGER PRIMARY KEY AUTOINCREMENT"
        return "INTEGER"

class FloatField(Field):
    """Float field"""
    def get_sql_type(self):
        return "FLOAT"

class BooleanField(Field):
    """Boolean field"""
    def get_sql_type(self):
        return "BOOLEAN"

class DateField(Field):
    """Date field"""
    def get_sql_type(self):
        return "DATE"

class DateTimeField(Field):
    """DateTime field"""
    def get_sql_type(self):
        return "DATETIME"

class TextField(Field):
    """Text field"""
    def get_sql_type(self):
        return "TEXT"

class DecimalField(Field):
    """Decimal field"""
    def __init__(self, precision=10, scale=2, **kwargs):
        super().__init__(**kwargs)
        self.precision = precision
        self.scale = scale
    
    def get_sql_type(self):
        return f"DECIMAL({self.precision},{self.scale})"

class ForeignKey(Field):
    """Foreign key field for relationships"""
    def __init__(self, to_model, related_name=None, **kwargs):
        super().__init__(**kwargs)
        self.to_model = to_model
        self.related_name = related_name
    
    def get_sql_type(self):
        return "INTEGER"

# ============= QuerySet for Chaining =============

class QuerySet:
    """Query builder with method chaining"""
    def __init__(self, model_class):
        self.model_class = model_class
        self.filters = {}
        self.order_by_field = None
        self.order_asc = True
    
    def filter(self, **kwargs):
        """Add filter conditions (supports __ operators)"""
        new_qs = QuerySet(self.model_class)
        new_qs.filters = self.filters.copy()
        
        for key, value in kwargs.items():
            new_qs.filters[key] = value
        
        new_qs.order_by_field = self.order_by_field
        new_qs.order_asc = self.order_asc
        return new_qs
    
    def order_by(self, field):
        """Order results by field"""
        new_qs = QuerySet(self.model_class)
        new_qs.filters = self.filters.copy()
        
        if field.startswith("-"):
            new_qs.order_by_field = field[1:]
            new_qs.order_asc = False
        else:
            new_qs.order_by_field = field
            new_qs.order_asc = True
        
        return new_qs
    
    def all(self):
        """Execute query and return all results"""
        conn, cursor = get_connection()
        
        table_name = self.model_class.__name__.lower()
        query = f"SELECT * FROM {table_name}"
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        for key, value in self.filters.items():
            if "__" in key:
                field_name, operator = key.rsplit("__", 1)
                if operator == "gte":
                    where_conditions.append(f"{field_name} >= ?")
                elif operator == "lte":
                    where_conditions.append(f"{field_name} <= ?")
                elif operator == "gt":
                    where_conditions.append(f"{field_name} > ?")
                elif operator == "lt":
                    where_conditions.append(f"{field_name} < ?")
                elif operator == "eq":
                    where_conditions.append(f"{field_name} = ?")
                else:
                    where_conditions.append(f"{field_name} = ?")
            else:
                where_conditions.append(f"{key} = ?")
            
            params.append(value)
        
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        
        # Add ORDER BY
        if self.order_by_field:
            order = "ASC" if self.order_asc else "DESC"
            query += f" ORDER BY {self.order_by_field} {order}"
        
        query += ";"
        
        print(f"SQL: {query}")
        cursor.execute(query, params)
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            instance = self.model_class()
            for idx, field_name in enumerate(column_names):
                setattr(instance, field_name, row[idx])
            results.append(instance)
        
        return results

# ============= ModelMetaclass =============

class ModelMetaclass(type):
    """Metaclass for Model to track fields"""
    def __new__(mcs, name, bases, namespace):
        # Don't process the base Model class itself
        if name == "Model" and not any(isinstance(b, ModelMetaclass) for b in bases):
            return super().__new__(mcs, name, bases, namespace)
        
        # Collect fields
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value
        
        # Store fields in class
        namespace["_fields"] = fields
        
        return super().__new__(mcs, name, bases, namespace)

# ============= Base Model =============

class Model(metaclass=ModelMetaclass):
    """Base Model class"""
    _fields = {}
    
    def __init__(self, **kwargs):
        """Initialize model instance"""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def create_table(cls):
        """Create table in database"""
        conn, cursor = get_connection()
        
        table_name = cls.__name__.lower()
        columns = []
        
        # Add id primary key
        columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        
        # Add fields
        for field_name, field_obj in cls._fields.items():
            if not field_name.startswith("_"):
                col_def = f"{field_name} {field_obj.get_sql_definition()}"
                columns.append(col_def)
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        query += ",\n   ".join(columns)
        query += "\n);"
        
        print(f"SQL: {query}")
        cursor.execute(query)
        conn.commit()
        print(f"Table '{table_name}' created.\n")
    
    def save(self):
        """Insert record into database"""
        conn, cursor = get_connection()
        
        table_name = self.__class__.__name__.lower()
        
        # Get fields with values
        fields = []
        values = []
        placeholders = []
        
        for field_name, field_obj in self.__class__._fields.items():
            if not field_name.startswith("_") and hasattr(self, field_name):
                value = getattr(self, field_name)
                if value is not None:
                    fields.append(field_name)
                    values.append(value)
                    placeholders.append("?")
        
        if not fields:
            print("No fields to save")
            return
        
        query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(placeholders)});"
        
        print(f"SQL: {query}")
        cursor.execute(query, values)
        conn.commit()
        
        # Get inserted id
        self.id = cursor.lastrowid
        print(f"Record saved: {self.__class__.__name__}(id={self.id})\n")
    
    def delete(self):
        """Delete record from database"""
        conn, cursor = get_connection()
        
        table_name = self.__class__.__name__.lower()
        
        if not hasattr(self, 'id') or self.id is None:
            print("Cannot delete: no id set")
            return
        
        query = f"DELETE FROM {table_name} WHERE id = ?;"
        
        print(f"SQL: {query}")
        cursor.execute(query, (self.id,))
        conn.commit()
        print(f"Record deleted: {self.__class__.__name__}(id={self.id})\n")
    
    @classmethod
    def filter(cls, **kwargs):
        """Create a QuerySet with filters"""
        return QuerySet(cls).filter(**kwargs)
    
    @classmethod
    def all(cls):
        """Get all records"""
        return QuerySet(cls).all()
    
    def __repr__(self):
        """String representation"""
        fields_str = ", ".join(
            f"{k}='{getattr(self, k, None)}'" 
            for k in self._fields.keys() 
            if hasattr(self, k)
        )
        return f"{self.__class__.__name__}({fields_str})"

# ============= Backwards Compatibility Functions =============

def IntegerValue(nullable=False):
    return "INTEGER " + ("NULL" if nullable else "NOT NULL")

def StringValue(max_length=255, nullable=False):
    return f"VARCHAR({max_length}) " + ("NULL" if nullable else "NOT NULL")

def BooleanValue(nullable=False):
    return "BOOLEAN " + ("NULL" if nullable else "NOT NULL")

def FloatValue(nullable=False):
    return "FLOAT " + ("NULL" if nullable else "NOT NULL")

def DateValue(nullable=False):
    return "DATE " + ("NULL" if nullable else "NOT NULL")

def DateTimeValue(nullable=False):
    return "DATETIME " + ("NULL" if nullable else "NOT NULL")

def TextValue(nullable=False):
    return "TEXT " + ("NULL" if nullable else "NOT NULL")

def DecimalValue(precision=10, scale=2, nullable=False):
    return f"DECIMAL({precision},{scale}) " + ("NULL" if nullable else "NOT NULL")

def BigIntegerValue(nullable=False):
    return "BIGINT " + ("NULL" if nullable else "NOT NULL")

def SmallIntegerValue(nullable=False):
    return "SMALLINT " + ("NULL" if nullable else "NOT NULL")