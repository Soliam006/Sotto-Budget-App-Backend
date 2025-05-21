from pydantic import model_validator

from .deps import Field, Relationship, SQLModel, Enum, Optional

class InventoryCategory(str, Enum):
    SERVICES = "services"
    MATERIALS = "materials"
    PRODUCTS = "products"
    LABOUR = "labour"

class InventoryStatus(str, Enum):
    INSTALLED = "Installed"
    PENDING = "Pending"
    IN_BUDGET = "In_Budget"

class InventoryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., max_length=100)
    category: InventoryCategory
    total: float = Field(..., gt=0)
    used: float = Field(default=0, ge=0)
    remaining: float = Field(default=0, ge=0)
    unit: str = Field(..., max_length=20)
    unit_cost: float = Field(..., gt=0, alias="unitCost")
    supplier: str = Field(..., max_length=100)
    status: InventoryStatus
    project_id: int = Field(foreign_key="project.id")

    # Relación con Project
    project: Optional["Project"] = Relationship(back_populates="inventory_items")

    class Config:
        validate_by_name = True  # Para usar alias (unitCost)

    @model_validator(mode="after")
    def calculate_remaining(self):
        self.remaining = self.total - self.used
        return self


class InventoryItemCreate(SQLModel):
    name: str = Field(..., max_length=100)
    category: InventoryCategory
    total: float = Field(..., gt=0)
    unit: str = Field(..., max_length=20)
    unit_cost: float = Field(..., gt=0, alias="unitCost")
    supplier: str = Field(..., max_length=100)
    status: InventoryStatus = InventoryStatus.IN_BUDGET
    project_id: int

    class Config:
        validate_by_name = True


class InventoryItemUpdate(SQLModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[InventoryCategory] = None
    total: Optional[float] = Field(None, gt=0)
    used: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=20)
    unit_cost: Optional[float] = Field(None, gt=0, alias="unitCost")
    supplier: Optional[str] = Field(None, max_length=100)
    status: Optional[InventoryStatus] = None
    project_id: Optional[int] = None

    class Config:
        validate_by_name = True
