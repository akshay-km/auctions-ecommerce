from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, Textarea, URLInput, TextInput, NumberInput
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import *



def index(request):

    auction_listings = AuctionListing.objects.filter(is_active=True).order_by('-pk')
    
    return render(request, "auctions/index.html", {
        "auction_listings" : auction_listings,
        "count": get_count(request),
    })


def get_count(request):
    if request.user.is_authenticated:
        count = len(request.user.watchlist.all())
        if count: 
            return count
    return '' 
    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        # Check if authentication successful
        if user is not None:
            login(request, user)
            count = len(user.watchlist.all())
            return HttpResponseRedirect(reverse("index",))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

    
@login_required
def watchlist_view(request): 
    watchlist = Watchlist.objects.filter(user=request.user).order_by('-pk')
    listings = [item.auction_listing for item in watchlist]
    return render(request, "auctions/watchlist.html", {
        "watchlist": listings,
         "count" : get_count(request),
    })

@login_required 
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.owner = request.user
            new_listing.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "auctions/createlisting.html",{
                "form": form,
                "count": get_count(request),
            })

    return render(request, "auctions/createlisting.html",{
        "form": CreateListingForm(),
        "count": get_count(request),
    })


class CreateListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description','image_path','category','price']
        # exclude =['user','is_active','time_stamp']
        labels = {
            'title': _('Title'),
            'image_path': _('Image URL'),
            'price': _('Price $'),
            'description' : _(''),

        }
        widgets = {
            'description': Textarea( attrs ={'cols':21, 'rows': 4, 'placeholder':"Description...(maximum 500 characters)"}),
            'image_path' : URLInput( attrs = { 'placeholder': "(Optional)"}),
            'title': TextInput( attrs={ 'placeholder': "Title"})
        }

@login_required 
def categories(request):
    categories_list = ["Electronics","Fashion","Toys","Home Appliances","Other"]
    return render(request, "auctions/categories.html",{
        "categories_list": categories_list,
        "count": get_count(request),
    })

@login_required
def category(request, item):
    auction_listings = AuctionListing.objects.filter(Q(is_active=True) & Q(category=item.upper())).order_by('-pk')
    return render(request, "auctions/category.html",{
        "item": item,
        "auction_listings": auction_listings,
        "count": get_count(request)
    })

def listing(request, key ):
    auction_listing = AuctionListing.objects.get(pk = key)
    bid_count = get_bid_count(auction_listing)
    if request.user.is_authenticated:
        return render (request, "auctions/listing.html", {
            "listing" : auction_listing,
            "count" : get_count(request),
            "bid_count": bid_count,
            "bidform": BidForm(),
            "in_watchlist":in_watchlist(auction_listing,request.user),
            "commentform": CommentForm(),  
            "commentlist": get_comments(auction_listing),      
        })

    return render (request, "auctions/listing.html", {
        "listing": auction_listing,
        "count": get_count(request),
        "bid_count": bid_count,
        "commentlist": get_comments(auction_listing),
    })

def get_comments(auction_listing):
    return Comment.objects.filter(auction_listing=auction_listing).order_by('-pk')

def get_bid_count(auction_listing):
    return len(auction_listing.bids.all())

def in_watchlist(auction_listing, user):
    if user.watchlist.filter(auction_listing=auction_listing):
        return True
    return False

def validate_price(auction_listing, price):
    if auction_listing.bids.all():
        if price > auction_listing.bids.order_by('price').last().price:
            return True
        else:
            return "Bid price should be higher than the current bid."
    else:
        if price >= auction_listing.price:
            return True
        else:
            return "Bid price should be atleast equal to the initial price."

@login_required
def bid(request , key):
    if request.method == "POST":
        form = BidForm(request.POST)
        auction_listing = AuctionListing.objects.get(pk=key)
        if form.is_valid():
            new_bid = form.save(commit=False)
            new_bid.bidder = request.user
            msg = validate_price(auction_listing, new_bid.price)
            if msg == True:
                auction_listing.price = new_bid.price
                auction_listing.highest_bidder = new_bid.bidder
                auction_listing.save()
                new_bid.auction_listing = auction_listing 
                new_bid.save()
                add_to_watchlist(request, key, True)
                return render (request, "auctions/listing.html", {
                "listing" : auction_listing,
                "count" : get_count(request),
                "bid_count": get_bid_count(auction_listing),
                "bidform": BidForm(),
                "commentform": CommentForm(),
                "in_watchlist":in_watchlist(auction_listing,request.user),
                "commentlist": get_comments(auction_listing),
                "bid_success": f"Bid of ${new_bid.price} placed successfully! Item added to watchlist.",
                })
            
            else:
                return render (request, "auctions/listing.html", {
                "listing" : auction_listing,
                "count" : get_count(request),
                "bid_count": get_bid_count(auction_listing),
                "bidform": form,
                "commentform": CommentForm(),
                "commentlist": get_comments(auction_listing),
                "in_watchlist":in_watchlist(auction_listing,request.user), 
                "error_message": msg,
                })

        else :
            return render (request, "auctions/listing.html", {
            "listing" : AuctionListing.objects.get(pk=key),
            "count" : get_count(request),
            "bid_count": get_bid_count(auction_listing),
            "bidform": form,
            "commentform": CommentForm(),
            "commentlist": get_comments(auction_listing),
            "in_watchlist":in_watchlist(auction_listing,request.user), 
            })

@login_required
def close_bid(request, key):
    auction_listing = AuctionListing.objects.get(pk=key)
    auction_listing.is_active = False
    auction_listing.save()
    add_to_watchlist(request,key,True)
    return HttpResponseRedirect(reverse('watchlist'))


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price',]

        labels = {
            'price' : _(''),
        }
        widgets = {
            'price' : NumberInput( attrs = { 'placeholder': "Value must be higher than the current bid." ,}),
        }

@login_required
def add_to_watchlist(request, key, from_bid=False):
    auction_listing = AuctionListing.objects.get(pk=key)
    if not request.user.watchlist.filter(auction_listing=auction_listing):
        watchlist = Watchlist(user = request.user, auction_listing=auction_listing)
        watchlist.save()
    if not from_bid:
        return HttpResponseRedirect(reverse('watchlist'))

@login_required
def delete_from_watchlist(request, key):
    auction_listing = AuctionListing.objects.get(pk=key)
    item = Watchlist.objects.filter(Q(user=request.user) & Q(auction_listing=auction_listing))
    item.delete()
    return HttpResponseRedirect(reverse('listing', kwargs={'key':key}))


@login_required
def add_comment(request, key):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            auction_listing = AuctionListing.objects.get(pk=key)
            new_comment.auction_listing = auction_listing
            new_comment.user = request.user
            new_comment.save()
            return HttpResponseRedirect(reverse('listing', kwargs={'key':key}))
        else:
            return render (request, "auctions/listing.html", {
            "listing" : AuctionListing.objects.get(pk=key),
            "count" : get_count(request),
            "bid_count": get_bid_count(auction_listing),
            "bidform": BidForm(),
            "commentform": form,
            "commentlist": get_comments(auction_listing),
            "in_watchlist":in_watchlist(auction_listing,request.user), 
            })



class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

        labels = {
            'text' : _(''),
        }

        widgets = {
            'text' : TextInput( attrs ={ 'placeholder':"Add your comment here...(maximum 200 characters)"}),
        }