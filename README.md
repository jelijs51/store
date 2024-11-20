# Store API
A Django-based API for managing products and categories in a store. This API utilizes Redis for caching frequently accessed data to optimize database queries.

## Objective
Implement a Django-based API for managing products and categories in a store. The API should use Redis for caching frequently accessed data to optimize database queries.

## Features
- **Category Management**: Add, update, delete, and retrieve categories.
- **Product Management**: Add, update, delete, and retrieve products.
- **Caching with Redis**: Frequently accessed data is cached to improve performance.
- **Filters**: The API allows filtering of products based on price range and category name.

## Requirements
1. **Django Rest Framework** for API development.
2. **SQLite** as the database for simplicity.
3. **Redis** as a caching layer, to store frequently accessed data temporarily.
4. **django-redis** for connecting Django with Redis.