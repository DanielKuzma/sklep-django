from django.urls import path
from .views import StartingPage, AddAuction, ClientPayInvoice, ClientMyInvoices, AllMyOffers, AuctionList, StaffConfirmPayment, AuctionDetail, MyProfile, StaffPendingPayments, UserBiddingAuctions,StaffIssueInvoice, StaffAuctionsToClose, sing_up 

urlpatterns = [
    path("", StartingPage.as_view(), name = "starting_page"),
    path("home", StartingPage.as_view(), name = "starting_page"),
    path("sing-up", sing_up, name = "create_acount"),
    path("home/all-auctions", AuctionList.as_view(), name = "auction_list"),
    path("home/my-profile", MyProfile.as_view(), name = "my_profile"),
    path("home/my-offers", AllMyOffers.as_view(), name = "my_offers"),
    path("home/my-biddings", UserBiddingAuctions.as_view(), name = "my_biddings"),
    path("home/add-auction", AddAuction.as_view(), name = "add_auction"),
    path('staff/auctions/', StaffAuctionsToClose.as_view(), name='staff_auctions'),
    path('my-invoices/', ClientMyInvoices.as_view(), name='client_invoices'),
    path('staff/payments/', StaffPendingPayments.as_view(), name='staff_payments'),

    path('my-invoices/<int:pk>/pay/', ClientPayInvoice.as_view(), name='client_pay_invoice'),
    path('staff/auctions/<int:pk>/issue-invoice/', StaffIssueInvoice.as_view(), name='staff_issue_invoice'),
    path('staff/payments/<int:pk>/confirm/', StaffConfirmPayment.as_view(), name='staff_confirm_payment'),
    path("auction-detail/<slug:slug>", AuctionDetail.as_view(), name = "action_detail")
    
]
