from typing import List

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from baserow.contrib.builder.api.pages.serializers import PathParamSerializer
from baserow.contrib.builder.domains.models import Domain
from baserow.contrib.builder.elements.models import Element
from baserow.contrib.builder.elements.registries import element_type_registry
from baserow.contrib.builder.models import Builder
from baserow.contrib.builder.pages.models import Page


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ("id", "domain_name", "order", "builder_id", "last_published")
        extra_kwargs = {
            "id": {"read_only": True},
            "builder_id": {"read_only": True},
            "order": {"help_text": "Lowest first."},
        }


class CreateDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ("domain_name",)


class OrderDomainsSerializer(serializers.Serializer):
    domain_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="The ids of the domains in the order they are supposed to be set in",
    )


class PublicElementSerializer(serializers.ModelSerializer):
    """
    Basic element serializer mostly for returned values.
    """

    type = serializers.SerializerMethodField(help_text="The type of the element.")

    @extend_schema_field(OpenApiTypes.STR)
    def get_type(self, instance):
        return element_type_registry.get_by_model(instance.specific_class).type

    class Meta:
        model = Element
        fields = ("id", "type", "style_padding_top", "style_padding_bottom")
        extra_kwargs = {
            "id": {"read_only": True},
            "type": {"read_only": True},
        }


class PublicPageSerializer(serializers.ModelSerializer):
    """
    A public version of the page serializer with less data to prevent data leaks.
    """

    path_params = PathParamSerializer(many=True, required=False)

    class Meta:
        model = Page
        fields = ("id", "name", "path", "path_params")
        extra_kwargs = {
            "id": {"read_only": True},
            "builder_id": {"read_only": True},
            "order": {"help_text": "Lowest first."},
        }


class PublicBuilderSerializer(serializers.ModelSerializer):
    """
    A public version of the builder serializer with less data to prevent data leaks.
    """

    pages = serializers.SerializerMethodField(
        help_text="This field is specific to the `builder` application and contains "
        "an array of pages that are in the builder."
    )

    class Meta:
        model = Builder
        fields = ("id", "name", "pages")

    @extend_schema_field(PublicPageSerializer(many=True))
    def get_pages(self, instance: Builder) -> List:
        """
        Returns the pages related to this public builder.

        :param instance: The builder application instance.
        :return: A list of serialized pages that belong to this instance.
        """

        pages = instance.page_set.all()

        return PublicPageSerializer(pages, many=True).data
