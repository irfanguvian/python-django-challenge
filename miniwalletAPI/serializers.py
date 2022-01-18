from rest_framework import serializers
from .models import Customer, Transaction, Wallet


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "type",
            "withdrawn_by",
            "deposited_by",
            "status",
            "withdrawn_at",
            "deposited_at",
            "amount",
            "reference_id",
        ]


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "owned_by", "status", "enabled_at", "disabled_at", "balance"]
