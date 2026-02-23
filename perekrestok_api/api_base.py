from __future__ import annotations

from dataclasses import field, fields, is_dataclass
from inspect import signature
from typing import Any, Callable, Generic, TypeVar, cast

try:
    from human_requests import (  # type: ignore[attr-defined]
        ApiChild,
        ApiParent,
        api_child_field,
    )
except ImportError:
    ParentT = TypeVar("ParentT")
    FactoryParentT = TypeVar("FactoryParentT")
    FactoryChildT = TypeVar("FactoryChildT")

    _API_CHILD_FACTORY_META = "perekrestok_api_child_factory"
    _UNSET = object()

    class ApiChild(Generic[ParentT]):
        _parent: ParentT

        def __init__(self, parent: ParentT) -> None:
            self._parent = parent

        @property
        def parent(self) -> ParentT:
            return self._parent

    class ApiParent:
        def __post_init__(self) -> None:
            if not is_dataclass(self):
                raise TypeError("ApiParent can only be used with dataclasses")

            for dataclass_field in fields(self):
                child_factory = cast(
                    Callable[[Any], Any] | None,
                    dataclass_field.metadata.get(_API_CHILD_FACTORY_META),
                )
                if child_factory is None:
                    continue
                if getattr(self, dataclass_field.name, _UNSET) is not _UNSET:
                    continue
                setattr(self, dataclass_field.name, _create_child(child_factory, self))

    def api_child_field(
        child_factory: Callable[[FactoryParentT], FactoryChildT],
        *,
        repr: bool = False,
        compare: bool = False,
    ) -> FactoryChildT:
        return cast(
            FactoryChildT,
            field(
                init=False,
                repr=repr,
                compare=compare,
                metadata={_API_CHILD_FACTORY_META: child_factory},
            ),
        )

    def _create_child(child_factory: Callable[[Any], Any], parent: Any) -> Any:
        try:
            call_signature = signature(child_factory)
            accepts_parent = _can_bind_single_positional(call_signature, parent)
        except (TypeError, ValueError):
            accepts_parent = True

        child = child_factory(parent) if accepts_parent else child_factory()
        if not accepts_parent and isinstance(child, ApiChild):
            child._parent = parent
        return child

    def _can_bind_single_positional(call_signature: Any, value: Any) -> bool:
        try:
            call_signature.bind(value)
            return True
        except TypeError:
            return False


__all__ = ["ApiChild", "ApiParent", "api_child_field"]
