from rest_framework import serializers

from app.products.models import Product

from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
        ]
        read_only_fields = [
            "id",
            "unit_price",
            "product_name",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )

        return value

    def validate(self, attrs):
        product = attrs.get("product")
        quantity = attrs.get("quantity")

        if product and not product.is_active:
            raise serializers.ValidationError(
                {
                    "product": "This product is currently inactive."
                }
            )

        if product and quantity and quantity > product.stock_quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        f"Only {product.stock_quantity} units "
                        "are currently available."
                    )
                }
            )

        return attrs

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "status",
            "shipping_address",
            "order_date",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "order_date",
            "created_at",
            "updated_at",
            "customer_name",
            "items",
        ]

    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"

    def validate_shipping_address(self, value):
        value = value.strip()

        if len(value) < 10:
            raise serializers.ValidationError(
                "Shipping address must contain at least 10 characters."
            )

        return value

class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
    )

    quantity = serializers.IntegerField(
        min_value=1,
    )

    def validate(self, attrs):
        product = attrs["product"]
        quantity = attrs["quantity"]

        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        f"Requested quantity exceeds available stock. "
                        f"Available: {product.stock_quantity}."
                    )
                }
            )

        return attrs

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(
        many=True,
        write_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "customer",
            "shipping_address",
            "items",
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "An order must contain at least one item."
            )

        product_ids = [
            item["product"].id
            for item in value
        ]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                "The same product cannot appear more than once in an order."
            )

        return value