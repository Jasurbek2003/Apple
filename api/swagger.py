from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import gettext_lazy as _

# Example JWT token response
token_response = openapi.Response(
    description=_("JWT token pair"),
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING, description=_('JWT access token')),
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description=_('JWT refresh token')),
        }
    )
)

# Product response schema for docs
product_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'category': openapi.Schema(type=openapi.TYPE_OBJECT),
        'images': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
    }
)

# Category response schema
category_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'slug': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

# Cart response schema
cart_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'items': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        'total_price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'item_count': openapi.Schema(type=openapi.TYPE_INTEGER),
    }
)

# Now update some key views with better documentation
# These are examples you can apply to other views/endpoints

# 1. Example for authentication endpoint - add this to views or a wrapper

login_swagger_schema = swagger_auto_schema(
    operation_description=_("Obtain JWT token pair by providing username and password."),
    operation_summary=_("Login"),
    responses={200: token_response},
    tags=['Authentication']
)

# 2. Example for product list endpoint

product_list_swagger_schema = swagger_auto_schema(
    operation_description=_("List all products with filtering options."),
    operation_summary=_("List Products"),
    manual_parameters=[
        openapi.Parameter(
            'category__slug',
            openapi.IN_QUERY,
            description=_("Filter by category slug"),
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'is_new',
            openapi.IN_QUERY,
            description=_("Filter by new products"),
            type=openapi.TYPE_BOOLEAN
        ),
        openapi.Parameter(
            'is_featured',
            openapi.IN_QUERY,
            description=_("Filter by featured products"),
            type=openapi.TYPE_BOOLEAN
        ),
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description=_("Search in name, description and SKU"),
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: openapi.Response(
        description=_("Successful response"),
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                'results': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=product_schema
                )
            }
        )
    )},
    tags=['Products']
)

# 3. Example for cart view

cart_swagger_schema = swagger_auto_schema(
    operation_description=_("Get the current user's shopping cart."),
    operation_summary=_("Get Cart"),
    responses={200: openapi.Response(
        description=_("Successful response"),
        schema=cart_schema
    )},
    tags=['Cart']
)

# 4. Example for order creation

order_create_swagger_schema = swagger_auto_schema(
    operation_description=_("Create a new order from the items in the cart."),
    operation_summary=_("Create Order"),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['shipping_address_id', 'billing_address_id'],
        properties={
            'shipping_address_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'billing_address_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'payment_method': openapi.Schema(type=openapi.TYPE_STRING),
            'notes': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        201: openapi.Response(
            description=_("Order created successfully"),
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        400: openapi.Response(
            description=_("Bad request - Cart is empty or invalid data"),
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    },
    tags=['Orders']
)