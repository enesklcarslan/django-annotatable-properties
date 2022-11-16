# Annotatable Properties

Annotatable properties is a django library that allows you to 
annotate any model property or calculated value using property name,
lambdas or any other callable.

It is approximately 15x slower than regular Django ORM, but it is
still fast enough for most use cases.

Quick start
-----------

1. Install using pip
   ```
   pip install django-annotatable-properties
   ```

2. Set the desired model's manager to AnnotatableQuerySet.as_manager() or AnnotatableManager():
    ```python
    from annotatable_properties import AnnotatableManager


    class SomeModel(models.Model):
        ...
        @property
        def some_field_plus_one(self):
            return self.some_field + 1
        ...
        objects = AnnotatableManager(),
    ```

3. Now you can annotate any model property or calculated value using property name, lambdas or any other callable:

    ```python
    from some_app.models import SomeModel
    SomeModel.objects.annotate_property('some_field_plus_one').filter(some_field_plus_one_property__gt=10)
    ```

    is roughly equivalent to:
    ```python
    from some_app.models import SomeModel
    from django.db.models import F
    SomeModel.objects.annotate(some_field_plus_one_property=F('some_field') + 1).filter(some_field_plus_one_property__gt=10)
    ```

How It Works
------------

Annotatable properties make annotating anything possible and much easier compared to the standard Django ORM.
It basically converts the QuerySet annotated into a Python sequence, calculates the values to be annotated and
annotates using raw SQL, then converts the result back to a QuerySet, keeping the order of the original QuerySet.


Some More Usage Examples
========================

Sort method
-----------

1. 
    Assume we have a model, Book, that has a title field, which is a CharField
    and all titles end with a number (from 0-9 to keep the example simple). We are required to order the Book QuerySet
    that we have by the number at the end of the title. If the Book is using
    the AnnotatableManager as the manager or the AnnotatableQuerySet as the
    QuerySet, we can do the following:

    ```python
    from book_app.models import Book
        
    Book.objects.sort(key=lambda book: book.title[-1])
    ```
    
2.
    Assume we have another model, Author, that has a name field, which is a CharField
    We want to sort all the authors by the length of their name and then by their name.
    If the Author is using the AnnotatableManager as the manager or the AnnotatableQuerySet as the
    QuerySet, we can do the following:

    ```python
    from author_app.models import Author
        
    Author.objects.sort(key=lambda author: (len(author.name), author.name))
    ```

3.
    Assume we have the same Author model from example 2. But this time, the model has a
    property called name_length, which is the length of the name field. Something like:
    ```python
    from django.db import models
        
    class Author(models.Model):
        name = models.CharField(max_length=100)
        ...
        @property
        def name_length(self):
            return len(self.name)
    ```
    We want to sort all the authors by the length of their name. This can be done by:
    ```python
    from author_app.models import Author
        
    Author.objects.sort(key='name_length')
    ```
    or if we want to sort by name_length and then name, we can use:
    ```python
    from author_app.models import Author
        
    Author.objects.sort(key=('name_length', 'name'))
    ```

annotate_property method
------------------------

1.
    Assume we have a model, Book, that has a title field, which is a CharField
    and all titles end with a number (from 0-9 to keep the example simple). We are required to annotate the Book QuerySet
    that we have with the number at the end of the title. If the Book is using
    the AnnotatableManager as the manager or the AnnotatableQuerySet as the
    QuerySet, we can do the following:

    ```python
    from book_app.models import Book
        
    books = Book.objects.annotate_property(lambda x: x.title[-1], property_name='title_number')
    ```
    Then if we wanted to exclude all the books that have a title number of 0, we can do:
    ```python
    books.exclude(title_number=0)
    ```

2.
    Assume we have an Author model. The model has a
    property called name_length, which is the length of the name field. Something like:
    ```python
    from django.db import models
        
    class Author(models.Model):
        name = models.CharField(max_length=100)
        ...
        @property
        def name_length(self):
            return len(self.name)
    ```
    To annotate this, we can simply do:
    ```python
    from author_app.models import Author
        
    authors = Author.objects.annotate_property('name_length')
    ```
    Then if we wanted to exclude all the authors that have a name shorter than 5 characters, we can do:
    ```python
    authors.exclude(name_length_property__lt=5)
    ```
    * Note that when the property name parameter is omitted, the property name is automatically appended with _property to avoid conflicts with the actual property.
    * Property annotations can be chained, just like ORM queries.
