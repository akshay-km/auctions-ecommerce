# auctions-ecommerce
An e-commerce auction site that will allow users to post auction listings, place bids on listings, comment on those listings, and add listings to a watchlist. This is a personal project build using Django framework making use of Django html templates.

## Specifications
### Listing Creation
- Users can visit a page to create a new listing.
- Users can specify a title, a text-based description, and a starting bid for the listing.
- Users can optionally provide a URL for an image for the listing and/or select a category (e.g., Fashion, Toys, Electronics, Home, etc.).

### Active Listings Page
- The default route displays all currently active auction listings.
- For each active listing, the page shows the title, description, current price, and photo (if available).

### Listing Page
- Clicking on a listing takes users to a page specific to that listing.
The listing page displays all details about the listing, including the current price.
- If a user is signed in, they can add the item to their "Watchlist" or remove it if it's already on the watchlist.
- Signed-in users can place bids on the item, which must be at least as large as the starting bid and greater than any other bids placed.
If the bid does not meet the criteria, an error is displayed.
- If the user who created the listing is signed in, they can "close" the auction, making the highest bidder the winner and marking the listing as inactive.
- If a signed-in user has won an auction, the closed listing page indicates so.
- Signed-in users can add comments to the listing page, and all comments are displayed.

### Watchlist
- Signed-in users can visit a Watchlist page that displays all the listings they have added to their watchlist.
- Clicking on any of the listings takes the user to the specific listing's page.

### Categories
- Users can visit a page that displays a list of all listing categories.
- Clicking on a category name takes the user to a page showing all the active listings in that category.

### Django Admin Interface
- The Django admin interface allows the site administrator to view, add, edit, and delete listings, comments, and bids on the site.
