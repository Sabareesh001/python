from orm import Model, CharField, IntegerField, FloatField, DateField, init_db

# Initialize database
init_db("app.db")

# Define Models
class User(Model):
    name = CharField(max_length=100)
    email = CharField(max_length=255, unique=True)
    age = IntegerField(nullable=True)

class Post(Model):
    title = CharField(max_length=200)
    content = CharField(max_length=1000)
    author_id = IntegerField()

class Product(Model):
    name = CharField(max_length=200)
    price = FloatField()
    stock = IntegerField()

def main():
    # Create tables
    print("=" * 60)
    print("Creating Tables")
    print("=" * 60)
    User.create_table()
    Post.create_table()
    Product.create_table()
    
    # Insert records
    print("=" * 60)
    print("Inserting Records")
    print("=" * 60)
    
    alice = User(name="Alice", email="alice@example.com", age=30)
    alice.save()
    
    bob = User(name="Bob", email="bob@example.com", age=25)
    bob.save()
    
    charlie = User(name="Charlie", email="charlie@example.com", age=35)
    charlie.save()
    
    post1 = Post(title="Hello World", content="First post content", author_id=1)
    post1.save()
    
    post2 = Post(title="Second Post", content="Another great post", author_id=1)
    post2.save()
    
    post3 = Post(title="Bob's Post", content="Bob's content here", author_id=2)
    post3.save()
    
    # Query with filters
    print("=" * 60)
    print("Filtering Records (age >= 30)")
    print("=" * 60)
    older_users = User.filter(age__gte=30).all()
    for user in older_users:
        print(f"  {user}")
    print()
    
    # Query with ordering
    print("=" * 60)
    print("Ordering Records (by name DESC)")
    print("=" * 60)
    ordered_users = User.filter(age__gte=25).order_by("-name").all()
    for user in ordered_users:
        print(f"  {user}")
    print()
    
    # Get all records
    print("=" * 60)
    print("All Posts")
    print("=" * 60)
    all_posts = Post.all()
    for post in all_posts:
        print(f"  {post}")
    print()
    
    # Exact match filter
    print("=" * 60)
    print("Filter by Email (exact match)")
    print("=" * 60)
    users = User.filter(name="Alice").all()
    for user in users:
        print(f"  {user}")
    print()

if __name__ == "__main__":
    main()