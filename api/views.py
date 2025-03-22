from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.utils.translation import get_language_from_request, gettext as _
from django.conf import settings
from products.models import Product, Category
from products.serializers import ProductListSerializer, CategorySerializer


class APIRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        API root endpoint showcasing available endpoints
        """
        return Response({
            "message": _("Welcome to the Apple-inspired API"),
            "version": "1.0.0",
            "endpoints": {
                "products": request.build_absolute_uri('/api/v1/products/'),
                "categories": request.build_absolute_uri('/api/v1/categories/'),
                "users": request.build_absolute_uri('/api/v1/users/'),
                "cart": request.build_absolute_uri('/api/v1/cart/'),
                "orders": request.build_absolute_uri('/api/v1/orders/'),
                "languages": request.build_absolute_uri('/api/v1/languages/'),
            }
        })


class LanguagesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get list of available languages
        """
        languages = [
            {
                'code': code,
                'name': str(name),
                'current': code == get_language_from_request(request)
            }
            for code, name in settings.LANGUAGES
        ]

        return Response(languages)


class CurrentLanguageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get the current language
        """
        current_language = get_language_from_request(request)
        return Response({
            'code': current_language,
            'name': str(dict(settings.LANGUAGES).get(current_language, ''))
        })


class SetLanguageView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Set the language for the current session",
        operation_summary="Set Language",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['language'],
            properties={
                'language': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description="Language set successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'code': openapi.Schema(type=openapi.TYPE_STRING),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid language code",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }


    )
    def post(self, request):
        """
        Set the language for the current session
        """
        lang_code = request.data.get('language', None)

        # Validate language code
        valid_languages = [code for code, name in settings.LANGUAGES]
        if not lang_code or lang_code not in valid_languages:
            return Response(
                {'error': _('Invalid language code')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set language in the session
        response = Response({
            'code': lang_code,
            'name': str(dict(settings.LANGUAGES).get(lang_code, ''))
        })

        # Set language cookie
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )

        # If user is authenticated, update their profile
        if request.user.is_authenticated:
            print(request.user.profile)
            try:
                profile = request.user.profile
                profile.language = lang_code
                print(profile.__dict__)
                profile.save(update_fields=['language'])
            except:
                pass

        return response


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_products(request):
    """
    Get featured products across all categories
    """
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def new_products(request):
    """
    Get new products across all categories
    """
    products = Product.objects.filter(is_active=True, is_new=True).order_by('-created_at')[:8]
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    """
    Search products, categories, and content
    """
    query = request.query_params.get('q', '')

    if not query or len(query) < 2:
        return Response(
            {'error': _('Search query must be at least 2 characters')},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Search products
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(sku__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct()[:20]

    # Search categories
    categories = Category.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    ).distinct()[:10]

    results = {
        'products': ProductListSerializer(products, many=True).data,
        'categories': CategorySerializer(categories, many=True).data,
        'query': query,
        'count': {
            'products': products.count(),
            'categories': categories.count(),
            'total': products.count() + categories.count()
        }
    }

    return Response(results)


# Add autocomplete search for product names
@api_view(['GET'])
@permission_classes([AllowAny])
def search_autocomplete(request):
    """
    Get autocomplete suggestions for product search
    """
    query = request.query_params.get('q', '')

    if not query or len(query) < 2:
        return Response([])

    # Get product suggestions
    suggestions = Product.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).distinct()[:10]

    # Get category suggestions
    category_suggestions = Category.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).distinct()[:5]

    # Combine results
    all_suggestions = list(suggestions) + [f"Category: {cat}" for cat in category_suggestions]

    return Response(all_suggestions)