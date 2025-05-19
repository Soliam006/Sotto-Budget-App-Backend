# Dependencies:
# pip install pytest-mock
import pytest
from datetime import datetime

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.api.routes.expenses import create_expense
from app.models.expense import ExpenseCreate, ExpenseStatus


class TestCreateExpense:

    # Successfully creates an expense when valid data is provided
    def test_create_expense_success(self, mocker):
        # Arrange
        mock_session = mocker.MagicMock()
        mock_expense_data = ExpenseCreate(
            expense_date=datetime.now(),
            category="Office Supplies",
            description="Printer paper",
            amount=50.0,
            status=ExpenseStatus.PENDING
        )
        mock_project_id = 1
    
        mock_new_expense = mocker.MagicMock()
        mock_create_project_expense = mocker.patch(
            "app.crud.expense.create_project_expense",
            return_value=mock_new_expense
        )
    
        # Act
        result = create_expense(
            project_id=mock_project_id,
            expense=mock_expense_data,
            session=mock_session
        )
    
        # Assert
        mock_create_project_expense.assert_called_once_with(
            session=mock_session,
            project_id=mock_project_id,
            expense_data=mock_expense_data
        )
        assert result.statusCode == 200
        assert result.data == mock_new_expense
        assert result.message == "Expense created successfully"

    # Handles case when project_id doesn't exist
    def test_create_expense_project_not_found(self, mocker):
        # Arrange
        mock_session = mocker.MagicMock()
        mock_expense_data = ExpenseCreate(
            expense_date=datetime.now(),
            category="Office Supplies",
            description="Printer paper",
            amount=50.0,
            status=ExpenseStatus.PENDING
        )
        mock_project_id = 999  # Non-existent project ID
    
        # Mock the create_project_expense to raise HTTPException for project not found
        mock_create_project_expense = mocker.patch(
            "app.crud.expense.create_project_expense",
            side_effect=HTTPException(status_code=404, detail="Project not found")
        )
    
        # Act
        result = create_expense(
            project_id=mock_project_id,
            expense=mock_expense_data,
            session=mock_session
        )
    
        # Assert
        mock_create_project_expense.assert_called_once_with(
            session=mock_session,
            project_id=mock_project_id,
            expense_data=mock_expense_data
        )
        assert isinstance(result, JSONResponse)
        assert result.status_code == 404
        assert result.body.decode('utf-8').find('"statusCode":404') > 0
        assert result.body.decode('utf-8').find('"message":"Project not found"') > 0
        assert result.body.decode('utf-8').find('"data":null') > 0

    # Handles case when expense creation fails
    def test_create_expense_creation_failed(self, mocker):
        # Arrange
        mock_session = mocker.MagicMock()
        mock_expense_data = ExpenseCreate(
            expense_date=datetime.now(),
            category="Office Supplies",
            description="Printer paper",
            amount=50.0,
            status=ExpenseStatus.PENDING
        )
        mock_project_id = 1

        # Mock the create_project_expense to raise HTTPException for creation failure
        mock_create_project_expense = mocker.patch(
            "app.crud.expense.create_project_expense",
            side_effect=HTTPException(status_code=500, detail="Failed to create expense")
        )

        # Act
        result = create_expense(
            project_id=mock_project_id,
            expense=mock_expense_data,
            session=mock_session
        )

        # Assert
        mock_create_project_expense.assert_called_once_with(
            session=mock_session,
            project_id=mock_project_id,
            expense_data=mock_expense_data
        )
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        assert result.body.decode('utf-8').find('"statusCode":500') > 0
        assert result.body.decode('utf-8').find('"message":"Failed to create expense"') > 0
        assert result.body.decode('utf-8').find('"data":null') > 0

    # Handles case when an unexpected error occurs
    def test_create_expense_unexpected_error(self, mocker):
        # Arrange
        mock_session = mocker.MagicMock()
        mock_expense_data = ExpenseCreate(
            expense_date=datetime.now(),
            category="Office Supplies",
            description="Printer paper",
            amount=50.0,
            status=ExpenseStatus.PENDING
        )
        mock_project_id = 1

        # Mock the create_project_expense to raise an unexpected error
        mock_create_project_expense = mocker.patch(
            "app.crud.expense.create_project_expense",
            side_effect=Exception("Unexpected error")
        )

        # Act
        result = create_expense(
            project_id=mock_project_id,
            expense=mock_expense_data,
            session=mock_session
        )

        # Assert
        mock_create_project_expense.assert_called_once_with(
            session=mock_session,
            project_id=mock_project_id,
            expense_data=mock_expense_data
        )
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        assert result.body.decode('utf-8').find('"statusCode":500') > 0
        assert result.body.decode('utf-8').find('"message":"Unexpected error"') > 0
        assert result.body.decode('utf-8').find('"data":null') > 0