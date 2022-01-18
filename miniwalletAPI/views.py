from rest_framework import permissions
from .models import Wallet, Customer, Transaction
from .serializers import WalletSerializer, CustomerSerializer, TransactionSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import datetime
from rest_framework.authtoken.models import Token
import uuid


# Create your views here.


class CustomerInit(APIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def post(self, request):
        body = request.data
        if body["customer_xid"] is not None:
            insertArgs = {"id": body["customer_xid"]}
            serializer = self.serializer_class(data=insertArgs)
            if serializer.is_valid():
                customersave = serializer.save()
                token = Token.objects.get(user=customersave).key
                response = {"status": "success", "data": {"token": token}}
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = {
                    "status": "fail",
                    "data": {
                        "error": {"customer_xid": ["Missing data for required field."]}
                    },
                }
                return Response(response, status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                "status": "fail",
                "data": {
                    "error": {"customer_xid": ["Missing data for required field."]}
                },
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)


class WalletAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    def get(self, request):
        token = request.META["HTTP_AUTHORIZATION"]
        queryToken = Token.objects.get(key=token[6:])
        queryWallet = Wallet.objects.get(owned_by=queryToken.user_id)

        if queryWallet is not None:
            if queryWallet.status != "disabled":
                response = {
                    "status": "success",
                    "data": {
                        "wallet": {
                            "id": queryWallet.id,
                            "owned_by": queryWallet.owned_by,
                            "status": queryWallet.status,
                            "enabled_at": queryWallet.enabled_at,
                            "balance": queryWallet.balance,
                        },
                    },
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {"status": "fail", "data": {"error": "Disabled"}}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {"status": "fail", "data": {"error": "Disabled"}}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        querywallet = Wallet.objects.all()
        token = request.META["HTTP_AUTHORIZATION"]
        queryToken = Token.objects.get(key=token[6:])
        queryFilter = querywallet.filter(owned_by__contains=queryToken.user_id)
        if len(queryFilter) == 0:
            data = {
                "id": str(uuid.uuid4()),
                "owned_by": queryToken.user_id,
                "status": "enable",
                "enabled_at": datetime.datetime.now()
                .astimezone()
                .replace(microsecond=0)
                .isoformat(),
                "disabled_at": None,
                "balance": 0,
            }
            serializer = self.serializer_class(data=data)
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                response = {
                    "status": "success",
                    "data": {
                        "wallet": {
                            "id": serializer.data["id"],
                            "owned_by": serializer.data["owned_by"],
                            "status": serializer.data["status"],
                            "enabled_at": serializer.data["enabled_at"],
                            "balance": 0,
                        }
                    },
                }
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = {"status": "fails", "data": {"error": "not valid"}}
                return Response(response, status.HTTP_400_BAD_REQUEST)
        else:
            if queryFilter[0].status == "enable":
                response = {"status": "fail", "data": {"error": "Already enabled"}}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                queryWallet = Wallet.objects.get(owned_by=queryToken.user_id)
                updateArgs = {
                    "id": queryWallet.id,
                    "owned_by": queryWallet.owned_by,
                    "status": "enable",
                    "enabled_at": datetime.datetime.now()
                    .astimezone()
                    .replace(microsecond=0)
                    .isoformat(),
                    "disabled_at": None,
                    "balance": int(queryWallet.balance),
                }
                serializer = self.serializer_class(
                    instance=queryWallet, data=updateArgs
                )
                if serializer.is_valid():
                    serializer.save()
                    response = {
                        "status": "success",
                        "data": {
                            "wallet": {
                                "id": serializer.data["id"],
                                "owned_by": serializer.data["owned_by"],
                                "status": serializer.data["status"],
                                "enabled_at": serializer.data["enabled_at"],
                                "balance": serializer.data["balance"],
                            }
                        },
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {
                        "status": "fails",
                        "data": {
                            "error": "server Error",
                        },
                    }
                    return Response(
                        response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

    def patch(self, request):
        token = request.META["HTTP_AUTHORIZATION"]
        queryToken = Token.objects.get(key=token[6:])
        queryWallet = Wallet.objects.get(owned_by=queryToken.user_id)
        body = request.data
        print(body)
        if len(body) == 0:
            response = {
                "status": "fail",
                "data": {"error": "input is_disabled is None"},
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        updateArg = {
            "id": queryWallet.id,
            "owned_by": queryWallet.owned_by,
            "status": "disabled",
            "disabled_at": datetime.datetime.now()
            .astimezone()
            .replace(microsecond=0)
            .isoformat(),
            "enabled_at": None,
            "balance": int(queryWallet.balance),
        }
        serializer = self.serializer_class(instance=queryWallet, data=updateArg)

        if serializer.is_valid():
            serializer.save()
            response = {
                "status": "success",
                "data": {
                    "wallet": {
                        "id": serializer.data["id"],
                        "owned_by": serializer.data["owned_by"],
                        "status": serializer.data["status"],
                        "disabled_at": serializer.data["disabled_at"],
                        "balance": serializer.data["balance"],
                    }
                },
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                "status": "fails",
                "data": {
                    "error": "server Error",
                },
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionDeposits(APIView):
    queryset = Transaction.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def post(self, request):
        token = request.META["HTTP_AUTHORIZATION"]
        queryToken = Token.objects.get(key=token[6:])
        queryWallet = Wallet.objects.get(owned_by=queryToken.user_id)
        body = request.data
        if len(body) != 0:
            insertArgs = {
                "id": str(uuid.uuid4()),
                "type": "deposit",
                "withdrawn_by": None,
                "withdrawn_at": None,
                "deposited_at": datetime.datetime.now()
                .astimezone()
                .replace(microsecond=0)
                .isoformat(),
                "status": "success",
                "deposited_by": queryToken.user_id,
                "amount": body["amount"],
                "reference_id": body["reference_id"],
            }
            balanceNow = int(queryWallet.balance)
            balanceDeposits = int(body["amount"])
            balanceUpdated = balanceDeposits + balanceNow
            updateArgs = {
                "id": queryWallet.id,
                "owned_by": queryWallet.owned_by,
                "status": queryWallet.status,
                "enabled_at": queryWallet.enabled_at,
                "disabled_at": queryWallet.disabled_at,
                "balance": balanceUpdated,
            }
            serializerWallet = WalletSerializer(queryWallet, data=updateArgs)
            serializer = self.serializer_class(data=insertArgs)
            if serializer.is_valid():
                serializer.save()
                response = {
                    "status": "success",
                    "data": {
                        "deposit": {
                            "id": serializer.data["id"],
                            "deposited_by": serializer.data["deposited_by"],
                            "status": serializer.data["status"],
                            "deposited_at": serializer.data["deposited_at"],
                            "amount": serializer.data["amount"],
                            "reference_id": serializer.data["reference_id"],
                        }
                    },
                }
                if serializerWallet.is_valid():
                    serializerWallet.save()
                    return Response(response, status=status.HTTP_201_CREATED)
                else:
                    response = {
                        "status": "fails",
                        "data": {
                            "error": "updated fails",
                        },
                    }
                    return Response(
                        response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            else:
                response = {
                    "status": "fails",
                    "data": {
                        "error": "server Error",
                    },
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionWithdrawn(APIView):
    queryset = Transaction.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def post(self, request):
        token = request.META["HTTP_AUTHORIZATION"]
        queryToken = Token.objects.get(key=token[6:])
        queryWallet = Wallet.objects.get(owned_by=queryToken.user_id)
        body = request.data
        if len(body) != 0:
            insertArgs = {
                "id": str(uuid.uuid4()),
                "type": "withdrawn",
                "deposited_at": None,
                "deposited_by": None,
                "withdrawn_at": datetime.datetime.now()
                .astimezone()
                .replace(microsecond=0)
                .isoformat(),
                "status": "success",
                "withdrawn_by": queryToken.user_id,
                "amount": body["amount"],
                "reference_id": body["reference_id"],
            }
            balanceNow = int(queryWallet.balance)
            balanceWithdrawn = int(body["amount"])
            balanceUpdated = balanceNow - balanceWithdrawn
            updateArgs = {
                "id": queryWallet.id,
                "owned_by": queryWallet.owned_by,
                "status": queryWallet.status,
                "enabled_at": queryWallet.enabled_at,
                "disabled_at": queryWallet.disabled_at,
                "balance": balanceUpdated,
            }
            serializerWallet = WalletSerializer(queryWallet, data=updateArgs)
            serializer = self.serializer_class(data=insertArgs)
            if serializer.is_valid():
                serializer.save()
                response = {
                    "status": "success",
                    "data": {
                        "deposit": {
                            "id": serializer.data["id"],
                            "withdrawn_by": serializer.data["withdrawn_by"],
                            "status": serializer.data["status"],
                            "withdrawn_at": serializer.data["withdrawn_at"],
                            "amount": serializer.data["amount"],
                            "reference_id": serializer.data["reference_id"],
                        }
                    },
                }
                if serializerWallet.is_valid():
                    serializerWallet.save()
                    return Response(response, status=status.HTTP_201_CREATED)
                else:
                    response = {
                        "status": "fails",
                        "data": {
                            "error": "updated fails",
                        },
                    }
                    return Response(
                        response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                response = {
                    "status": "fails",
                    "data": {
                        "error": "server Error",
                    },
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            response = {
                "status": "fails",
                "data": {
                    "error": "invalid form request",
                },
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
