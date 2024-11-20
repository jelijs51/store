from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.core.cache import cache


def response_wrapper(data=None, message=None, status_code=status.HTTP_200_OK):
    return Response({"data": data, "message": message}, status=status_code)


@api_view(["GET"])
def ApiOverview(request):
    api_urls = {
        "List all categories": "/api/categories/",
        "Create a new category": "/api/categories/",
        "Retrieve a category by id": "/api/categories/{id}",
        "Update a category by id": "/api/categories/{id}",
        "Delete a category by id": "/api/categories/{id}",
        "List all products": "/api/products/",
        "Create a new product": "/api/products/",
        "Retrieve a product by id": "/api/products/{id}?category_name=&price_min=&price_max&",
        "Update a product by id": "/api/products/{id}",
        "Delete a product by id": "/api/products/{id}",
    }
    return response_wrapper(data=api_urls, message="List of API URL")


@api_view(["GET", "POST"])
def categories_view(request):

    # Get all category data
    if request.method == "GET":
        data = cache.get("store:categories")
        if not data:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            data = serializer.data
            cache.set(key="store:categories", value=data, timeout=5 * 60)
        return response_wrapper(data=data, message="Success")

    # Post a new category
    elif request.method == "POST":
        serializer = CategorySerializer(data=request.data)
        category_name = request.data.get("name")
        if Category.objects.filter(name=category_name).exists():
            return response_wrapper(
                message=f"data with name {category_name} already exist",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if serializer.is_valid():
            serializer.save()
            cache.delete(key="store:categories")
            return response_wrapper(
                data=serializer.data,
                message="Success",
                status_code=status.HTTP_201_CREATED,
            )
        return response_wrapper(
            data=serializer.errors,
            message="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET", "PUT", "DELETE"])
def category_view(request, *args, **kwargs):
    id = kwargs.get("id")

    # Get category by ID
    if request.method == "GET":
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return response_wrapper(
                message=f"Category with id {id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = CategorySerializer(category)
        return response_wrapper(data=serializer.data, message="Success")

    # Update category by ID
    elif request.method == "PUT":
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return response_wrapper(
                message=f"Category with id {id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = CategorySerializer(instance=category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(key="store:categories")
            return response_wrapper(data=serializer.data, message="Success")
        else:
            return response_wrapper(
                data=serializer.errors,
                message="Validation Error",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    # Delete category by ID
    elif request.method == "DELETE":
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return response_wrapper(
                message=f"Category with id {id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        category.delete()
        cache.delete(key="store:categories")
        return response_wrapper(
            message=f"Category with id {id} has been deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET", "POST"])
def products_view(request, *args, **kwargs):
    # Get all product
    if request.method == "GET":
        data = cache.get(key="store:products")
        if not data:
            filters = {}
            category_name = request.query_params.get("category_name", None)
            price_min = request.query_params.get("price_min", None)
            price_max = request.query_params.get("price_max", None)

            try:
                if price_min:
                    filters["price__gte"] = float(price_min)
                if price_max:
                    filters["price__lte"] = float(price_max)
            except ValueError:
                return response_wrapper(
                    message="Invalid price filter values",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if category_name:
                filters["category__name__icontains"] = category_name
            products = Product.objects.filter(**filters)
            serializer = ProductSerializer(products, many=True)
            data = serializer.data
            cache.set(key="store:products", value=data, timeout=5 * 60)
        return response_wrapper(data=data, message="Success")

    # Post a new product
    elif request.method == "POST":
        try:
            if (
                "category" in request.data
                and not Category.objects.filter(id=request.data["category"]).exists()
            ):
                return response_wrapper(
                    message=f"Category with id {request.data['category']} does not exist",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return response_wrapper(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(key="store:products")
            return response_wrapper(
                data=serializer.data,
                message="Success",
                status_code=status.HTTP_201_CREATED,
            )
        return response_wrapper(
            data=serializer.errors,
            message="Validation Error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET", "PUT", "DELETE"])
def product_view(request, *args, **kwargs):
    id = kwargs.get("id")

    # Get category by ID
    if request.method == "GET":
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return response_wrapper(
                message=f"Product with id {id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = ProductSerializer(product)
        return response_wrapper(data=serializer.data, message="Success")

    # Update category by ID
    elif request.method == "PUT":
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return response_wrapper(
                message=f"Product with id {id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        try:
            if (
                "category" in request.data
                and not Category.objects.filter(id=request.data["category"]).exists()
            ):
                return response_wrapper(
                    message=f"Category with id {request.data['category']} does not exist",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return response_wrapper(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer = ProductSerializer(instance=product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(key="store:products")
            return response_wrapper(data=serializer.data, message="Success")
        else:
            return response_wrapper(
                data=serializer.errors,
                message="Validation Error",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    # Delete Category by ID
    elif request.method == "DELETE":
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return response_wrapper(
                message=f"Product with id {id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        product.delete()
        cache.delete(key="store:products")
        return response_wrapper(
            message=f"Product with id {id} has been deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )
