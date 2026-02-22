import re
import graphene
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Customer


# ---------------------------
# Customer GraphQL Type
# ---------------------------

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


# ---------------------------
# CreateCustomer Mutation
# ---------------------------

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, email, phone=None):
        errors = []

        # ---------------------------
        # Validate email uniqueness
        # ---------------------------
        if Customer.objects.filter(email=email).exists():
            errors.append("Email already exists.")

        # ---------------------------
        # Validate phone format (optional)
        # ---------------------------
        if phone:
            phone_pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
            if not re.match(phone_pattern, phone):
                errors.append(
                    "Invalid phone format. Use +1234567890 or 123-456-7890."
                )

        # If validation errors exist
        if errors:
            return CreateCustomer(
                success=False,
                message="Customer creation failed.",
                errors=errors,
                customer=None,
            )

        try:
            customer = Customer.objects.create(
                name=name,
                email=email,
                phone=phone
            )

            return CreateCustomer(
                success=True,
                message="Customer created successfully.",
                errors=None,
                customer=customer,
            )

        except IntegrityError:
            return CreateCustomer(
                success=False,
                message="Database integrity error.",
                errors=["Email must be unique."],
                customer=None,
            )

        except Exception as e:
            return CreateCustomer(
                success=False,
                message="Unexpected error occurred.",
                errors=[str(e)],
                customer=None,
            )


# ---------------------------
# Root Mutation Class
# ---------------------------

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
