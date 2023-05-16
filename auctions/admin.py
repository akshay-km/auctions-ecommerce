from django.contrib import admin
from .models import * 

class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ("title","owner","price",)

class CommentAdmin(admin.ModelAdmin):
    list_display = ("auction_listing","user","text",)

class BidAdmin(admin.ModelAdmin):
    list_display = ("bidder","auction_listing","price",)

# Register your models here.
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
