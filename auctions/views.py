from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
    })

def displayCategory(request):
    if request.method == "POST":
        categoryForm = request.POST["category"]
        if categoryForm == "select":
            return HttpResponseRedirect(reverse(index))
        category = Category.objects.get(categoryName=categoryForm)
        activeListings = Listing.objects.filter(isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": allCategories,
        })


def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)

    isUser = request.user.username == listingData.owner.username

    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isUser": isUser
    })

def endAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isUser = request.user.username == listingData.owner.username

    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "success": "Congrats!!! Your auction has been closed",
        "isUser": isUser
    })

def addBid(request, id):
    bid = request.POST["bid"]
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isUser = request.user.username == listingData.owner.username

    currentUser = request.user
    listingData.userBid.add(currentUser)

    if float(bid) > listingData.price.bid:
        updateBid = Bid(bid=float(bid), user=request.user)
        updateBid.save()
        listingData.price = updateBid
        listingData.save()

        return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "message": "Bid added successfully",
        "updated": True,
        "isUser": isUser
    })
    else:
        return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "message": "Unable to add bid",
        "updated": False,
        "isUser": isUser
        })


def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        category = request.POST["category"]
        price = request.POST["price"]

        currentUser = request.user

        if category == "select":
            allCategories = Category.objects.all()
            return render(request, "auctions/create.html", {
                "categories": allCategories,
                "message": "Please select a category"
            })
        categoryData = Category.objects.get(categoryName=category)

        newBid = Bid(bid=float(price), user=currentUser)
        newBid.save()
        
        newListing = Listing(
            title=title,
            description=description,
            category=categoryData,
            price=newBid,
            imageUrl=imageurl,
            owner=currentUser
        )

        newListing.save()
        return HttpResponseRedirect(reverse(index))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
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

def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))
    

def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def watchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })

def userBidding(request):
    currentUser = request.user
    listings = currentUser.userBiddings.all()
    activeListings = Listing.objects.filter(isActive=True)
    return render(request, "auctions/bidding.html",{
        "listings": listings,
        "inactiveListings": activeListings
    })

def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST["newComment"]

    newComment = Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    newComment.save()
    return HttpResponseRedirect(reverse("listing",args=(id, )))