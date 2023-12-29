# BIG-MAP Archive

## Requirements

BIG-MAP Archive offers "community" features. 
This version is expected to fulfill community-related requirements 
and record-related requirements, including:
- Users are not allowed to create communities.
- Sharing a record outside one of the user’s communities is not permitted.

More details can be found below.

## Community-related requirements

Users are not allowed to manage communities and community membership.
More precisely, any users who try to perform the following actions should get permission denied (status code: 403): 
- creating a community (POST, /api/communities)
- updating a community (PUT, /api/communities/<community_slug>)
- deleting a community (DELETE, /api/communities/<community_slug>)
- renaming a community (POST, /api/communities/<community_id>/rename)
- updating a community logo (PUT, /api/communities/<community_id>/logo)
- deleting a community logo (DELETE, /api/communities/<community_id>/logo)
- creating a featured community entry (POST, /api/communities/<community_id>/featured).

In addition, 
- Users who do not belong to the specified community should get permission denied (status code: 403) 
when attempting to do the following:
  - retrieving a community's metadata (GET, /api/communities/<community_id>)
  - retrieving a community's logo (GET, /api/communities/<community_id>/logo).

- Users should only see the communities that they belong to, when searching communities (GET, /api/communities), 
since all communities are expected to have hidden visibility.

- Unauthenticated users should get permission denied (status code: 403) when trying to do the following:
  - searching communities (GET, /api/communities)
  - searching the featured communities (GET, /api/communities/featured)
  - retrieving the featured community entries (GET, /api/communities/<community_id>/featured).