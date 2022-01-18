from django.urls import path
from . import views


# URLConf
urlpatterns = [
    path("init", views.CustomerInit.as_view()),
    path("wallet", views.WalletAPI.as_view()),
    path("wallet/deposits", views.TransactionDeposits.as_view()),
    path("wallet/withdrawals", views.TransactionWithdrawn.as_view()),
]
