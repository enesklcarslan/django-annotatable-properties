from operator import attrgetter
from django.db.models import (
    QuerySet,
)
from django.db.models.manager import Manager
from typing import Callable, Union


class AnnotatableQuerySet(QuerySet):
    def sort(self, key: Union[Callable, str, tuple[str, ...]], reverse: bool = False) -> QuerySet:
        """Sort a queryset pythonically by a key. Works just like `list.sort()` method.

        Args:
            key (Union[Callable, str, tuple[str, ...]]): A callable or a string or a tuple of strings. 
            reverse (bool, optional): Defaults to False.

        Returns:
            AnnotatableQuerySet: A queryset sorted by the key. Can be chained with other queryset methods.
        
        Examples:
            >>> from annotatable_querysets.models import TestModel
            >>> sorted_qs = TestModel.objects.filter(will_be_sorted=True).sort(key=lambda x: (x.cost/x.price, x.name))
            >>> sorted_qs = TestModel.objects.sort(key="name")
            >>> sorted_qs = TestModel.objects.sort(key=("name", "cost")).filter(cost__gt=100)
        """
        if isinstance(key, str):
            key = attrgetter(key)

        elif isinstance(key, tuple):
            key = attrgetter(*key)

        sorted_objects = sorted(
            self, 
            key=key,
            reverse=reverse
        )
        
        if not sorted_objects:
            return self

        pk_mapping = {obj.pk: order for order, obj in enumerate(sorted_objects)}

        sql = f"CASE {' '.join([f'WHEN id = {pk} THEN {order}' for pk, order in pk_mapping.items()])} END"
        return self.extra(
            select={
                "sort_order": sql
            }
        ).order_by("sort_order")

    def annotate_property(self, annotation: Union[Callable, str], property_name: str = None) -> QuerySet:
        """Annotate a queryset with a property.

        Args:
            annotation (Union[Callable, str]): A callable or a string (Model property's name). 
            property_name (str): The name of the property to be annotated.

        Returns:
            AnnotatableQuerySet: A queryset annotated with the property. Can be chained with other queryset methods.
        
        Examples:
            >>> from annotatable_querysets.models import TestModel
            >>> annotated_qs = TestModel.objects.annotate_property(annotation=lambda x: x.cost/x.price, property_name="price_to_cost_ratio").filter(price_to_cost_ratio__gt=2)
            >>> annotated_qs = TestModel.objects.annotate_property(annotation="name", property_name="product_name").filter(product_name__icontains="apple")
        """
        if property_name is None:
            if isinstance(annotation, str):
                property_name = f"{annotation}_property"
            else:
                raise ValueError("property_name cannot be None if annotation is not a string.")

        if isinstance(annotation, str):
            annotation = attrgetter(annotation)

        pk_mapping = {obj.pk: annotation(obj) for obj in self}

        sql = f"CASE {' '.join([f'WHEN id = {pk} THEN {repr(annotated_property)}' for pk, annotated_property in pk_mapping.items()])} END"

        return self.extra(
            select={
                property_name: sql
            }
        )

class AnnotatableManager(Manager):
    def get_queryset(self) -> AnnotatableQuerySet:
        return AnnotatableQuerySet(self.model, using=self._db)

    def sort(self, key: Union[Callable, str, tuple[str, ...]], reverse: bool = False) -> AnnotatableQuerySet:
        """Sort a queryset pythonically by a key. Works just like `list.sort()` method.

        Args:
            key (Union[Callable, str, tuple[str, ...]]): A callable or a string or a tuple of strings. 
            reverse (bool, optional): Defaults to False.

        Returns:
            AnnotatableQuerySet: A queryset sorted by the key. Can be chained with other queryset methods.
        
        Examples:
            >>> from annotatable_querysets.models import TestModel
            >>> sorted_qs = TestModel.objects.filter(will_be_sorted=True).sort(key=lambda x: (x.cost/x.price, x.name))
            >>> sorted_qs = TestModel.objects.sort(key="name")
            >>> sorted_qs = TestModel.objects.sort(key=("name", "cost")).filter(cost__gt=100)
        """
        return self.get_queryset().sort(key=key, reverse=reverse)
    
    def annotate_property(self, annotation: Union[Callable, str], property_name: str = None) -> AnnotatableQuerySet:
        """Annotate a queryset with a property.

        Args:
            annotation (Union[Callable, str]): A callable or a string (Model property's name). 
            property_name (str): The name of the property to be annotated.

        Returns:
            AnnotatableQuerySet: A queryset annotated with the property. Can be chained with other queryset methods.
        
        Examples:
            >>> from annotatable_querysets.models import TestModel
            >>> annotated_qs = TestModel.objects.annotate_property(annotation=lambda x: x.cost/x.price, property_name="price_to_cost_ratio").filter(price_to_cost_ratio__gt=2)
            >>> annotated_qs = TestModel.objects.annotate_property(annotation="name", property_name="product_name").filter(product_name__icontains="apple")
        """
        return self.get_queryset().annotate_property(annotation=annotation, property_name=property_name)