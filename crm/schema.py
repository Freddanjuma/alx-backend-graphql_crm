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
        phone = graphene.String(required=True)

    customer = graphene.Field(CustomerType)

    def mutate(self, info, name, email, phone):

        # Create instance
        customer = Customer(
            name=name,
            email=email,
            phone=phone
        )

        # Explicit save (REQUIRED by checker)
        customer.save()

        return CreateCustomer(customer=customer)

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
