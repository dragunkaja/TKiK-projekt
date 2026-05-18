from dataclasses import dataclass
from typing import Optional, Union, Dict, Any, Tuple


# =========================================================
#                     NODES BAZOWE
# =========================================================

class ASTNode:
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


# =========================================================
#                    PROGRAM / STATEMENT
# =========================================================

@dataclass
class StatementNode(ASTNode):
    dryrun: bool
    query: "QueryNode"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dryrun": self.dryrun,
            "query": self.query.to_dict(),
        }


@dataclass
class ProgramNode(ASTNode):
    statement: StatementNode

    def to_dict(self) -> Dict[str, Any]:
        # engine.py oczekuje top-level dict z kluczami dryrun i query
        return self.statement.to_dict()


# =========================================================
#                         QUERY
# =========================================================

@dataclass
class QueryNode(ASTNode):
    action: str

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


@dataclass
class SelectQueryNode(QueryNode):
    columns: Union[str, list]
    path: str
    where: Optional["ConditionNode"] = None
    order: Optional["OrderClauseNode"] = None
    limit: Optional[int] = None

    def __init__(
        self,
        columns: Union[str, list],
        path: str,
        where: Optional["ConditionNode"] = None,
        order: Optional["OrderClauseNode"] = None,
        limit: Optional[int] = None,
    ):
        super().__init__("SELECT")
        self.columns = columns
        self.path = path
        self.where = where
        self.order = order
        self.limit = limit

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "columns": self.columns,
            "path": self.path,
            "where": self.where.to_dict() if self.where else None,
            "order": self.order.to_dict() if self.order else None,
            "limit": self.limit,
        }


@dataclass
class DeleteQueryNode(QueryNode):
    path: str
    where: Optional["ConditionNode"] = None
    limit: Optional[int] = None

    def __init__(
        self,
        path: str,
        where: Optional["ConditionNode"] = None,
        limit: Optional[int] = None,
    ):
        super().__init__("DELETE")
        self.path = path
        self.where = where
        self.limit = limit

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "path": self.path,
            "where": self.where.to_dict() if self.where else None,
            "limit": self.limit,
        }


@dataclass
class MoveQueryNode(QueryNode):
    source: str
    destination: str
    where: Optional["ConditionNode"] = None
    limit: Optional[int] = None

    def __init__(
        self,
        source: str,
        destination: str,
        where: Optional["ConditionNode"] = None,
        limit: Optional[int] = None,
    ):
        super().__init__("MOVE")
        self.source = source
        self.destination = destination
        self.where = where
        self.limit = limit

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "source": self.source,
            "destination": self.destination,
            "where": self.where.to_dict() if self.where else None,
            "limit": self.limit,
        }


@dataclass
class CopyQueryNode(QueryNode):
    source: str
    destination: str
    where: Optional["ConditionNode"] = None
    limit: Optional[int] = None

    def __init__(
        self,
        source: str,
        destination: str,
        where: Optional["ConditionNode"] = None,
        limit: Optional[int] = None,
    ):
        super().__init__("COPY")
        self.source = source
        self.destination = destination
        self.where = where
        self.limit = limit

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "source": self.source,
            "destination": self.destination,
            "where": self.where.to_dict() if self.where else None,
            "limit": self.limit,
        }


# =========================================================
#                      CONDITIONS
# =========================================================

@dataclass
class ConditionNode(ASTNode):
    pass


@dataclass
class LogicConditionNode(ConditionNode):
    logic_op: str
    left: ConditionNode
    right: Optional[ConditionNode] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "logic_op": self.logic_op,
            "left": self.left.to_dict(),
        }
        if self.right is not None:
            result["right"] = self.right.to_dict()
        return result


@dataclass
class NotConditionNode(ConditionNode):
    val: ConditionNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "logic_op": "NOT",
            "val": self.val.to_dict(),
        }


@dataclass
class RelationConditionNode(ConditionNode):
    rel_op: str
    column: str
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rel_op": self.rel_op,
            "column": self.column,
            "value": self.value.to_dict() if isinstance(self.value, ValueNode) else self.value,
        }


@dataclass
class LikeConditionNode(ConditionNode):
    column: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rel_op": "LIKE",
            "column": self.column,
            "value": self.value,
        }


# =========================================================
#                         VALUES
# =========================================================

@dataclass
class ValueNode(ASTNode):
    def to_dict(self) -> Any:
        raise NotImplementedError


@dataclass
class StringValueNode(ValueNode):
    value: str

    def to_dict(self) -> str:
        return self.value


@dataclass
class NumberValueNode(ValueNode):
    value: Union[int, float]

    def to_dict(self) -> Union[int, float]:
        return self.value


@dataclass
class SizeValueNode(ValueNode):
    value: Union[int, float]
    unit: str

    def to_python(self) -> Tuple[Union[int, float], str]:
        return (self.value, self.unit.upper())

    def to_dict(self) -> Tuple[Union[int, float], str]:
        return self.to_python()


# =========================================================
#                    ORDER / LIMIT
# =========================================================

@dataclass
class OrderClauseNode(ASTNode):
    column: str
    direction: str = "ASC"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "column": self.column,
            "dir": self.direction.upper(),
        }


@dataclass
class LimitClauseNode(ASTNode):
    value: int

    def to_dict(self) -> int:
        return self.value