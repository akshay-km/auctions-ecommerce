from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    pass

    def __str__(self):
        return f"{self.username}"

class AuctionListing(models.Model):
    CATEGORIES = [  ('ELECTRONICS','Electronics'),
                    ('FASHION','Fashion'),
                    ('TOYS','Toys'),
                    ('HOME APPLIANCES','Home Appliances'),
                    ('OTHER','Other'),
    ]
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=500)
    image_path = models.URLField(max_length=300 , blank = True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_listings")
    category = models.CharField(max_length=15,choices=CATEGORIES, default = 'OTHER')
    price = models.DecimalField(max_digits=20, decimal_places=2)
    is_active = models.BooleanField(default=True)
    time_stamp = models.DateTimeField(auto_now_add=True)
    highest_bidder = models.ForeignKey(User,models.SET_NULL,blank=True,null=True)

    def __str__(self):
        return f"{self.title} | Owner: {self.owner}"



class Bid(models.Model):
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(max_digits= 20, decimal_places = 2)
    
    def __str__(self):
        return f"{self.bidder} on  ${self.price} for {self.auction_listing.title}"

   
        

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user} on {self.auction_listing}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} with {self.auction_listing}"


