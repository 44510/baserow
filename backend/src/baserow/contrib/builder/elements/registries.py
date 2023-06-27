from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, TypeVar

from baserow.core.registry import (
    CustomFieldsInstanceMixin,
    CustomFieldsRegistryMixin,
    ImportExportMixin,
    Instance,
    ModelInstanceMixin,
    ModelRegistryMixin,
    Registry,
)

if TYPE_CHECKING:
    from baserow.contrib.builder.pages.models import Page

from .models import Element
from .types import ElementDictSubClass, ElementSubClass


class ElementType(
    Instance,
    ModelInstanceMixin[ElementSubClass],
    ImportExportMixin[ElementSubClass],
    CustomFieldsInstanceMixin,
    ABC,
):
    """Element type"""

    SerializedDict: Type[ElementDictSubClass]

    def prepare_value_for_db(self, values: Dict, instance: Optional[Element] = None):
        """
        This function allows you to hook into the moment an element is created or
        updated. If the element is updated `instance` will be defined, and you can use
        `instance` to extract any context data that might be required for the
        implementation of this hook.

        :param values: The values that are being updated
        :param instance: (optional) The existing instance that is being updated
        :return:
        """

        return values

    def export_serialized(
        self,
        element: Element,
    ) -> ElementDictSubClass:
        """
        Exports the element to a serialized dict that can be imported by the
        `import_serialized` method. This dict is also JSON serializable.

        :param element: The element instance that must be serialized.
        :return: The exported element as serialized dict.
        """

        other_properties = {key: getattr(element, key) for key in self.allowed_fields}

        serialized = self.SerializedDict(
            id=element.id,
            type=self.type,
            order=element.order,
            style_padding_top=element.style_padding_top,
            style_padding_bottom=element.style_padding_bottom,
            **other_properties
        )

        return serialized

    def import_serialized(
        self,
        page: "Page",
        serialized_values: Dict[str, Any],
        id_mapping: Dict[str, Any],
    ) -> Element:
        """
        Imports the previously exported dict generated by the `export_serialized`
        method.

        :param page: The page we want to import the element for.
        :serialized_values: The dict containing the serialized version of the element.
        :id_mapping: Used to mapped object ids from export to newly created instances.
        :return: The created element.
        """

        if "builder_elements" not in id_mapping:
            id_mapping["builder_elements"] = {}

        serialized_copy = serialized_values.copy()

        # Remove extra keys
        element_id = serialized_copy.pop("id")
        serialized_copy.pop("type")

        element = self.model_class(page=page, **serialized_copy)
        element.save()

        id_mapping["builder_elements"][element_id] = element.id

        return element

    @abstractmethod
    def get_sample_params(self) -> Dict[str, Any]:
        """
        Returns a sample of params for this type. This can be used to tests the element
        for instance.
        """


ElementTypeSubClass = TypeVar("ElementTypeSubClass", bound=ElementType)


class ElementTypeRegistry(
    Registry[ElementTypeSubClass],
    ModelRegistryMixin[ElementSubClass, ElementTypeSubClass],
    CustomFieldsRegistryMixin,
):
    """
    Contains all registered element types.
    """

    name = "element_type"


element_type_registry = ElementTypeRegistry()
