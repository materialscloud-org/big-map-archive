# BIG-MAP Archive

## Requirements

BIG-MAP Archive offers a "community" feature, 
where community members can privately share records (datasets) with entire communities. 

This version of BIG-MAP Archive should fulfill numerous requirements, including:
- Users are not allowed to join or leave a community by themselves. Administrators of BIG-MAP Archive are in charge of community membership.
- Users are allowed to privately share a record with one of their communities.
- A shared record is accessible to all members of the community and only to those users.

More details can be found below.

## Community-related requirements (ALL TESTS PASSED ON DEC. 29, 2023)

Users are not allowed to manage communities. More precisely, any users who try to perform the following actions should get permission denied (status code: 403): 
- creating a community (POST, /api/communities)
- updating a community (PUT, /api/communities/<community_slug>)
- deleting a community (DELETE, /api/communities/<community_slug>)
- renaming a community (POST, /api/communities/<community_id>/rename)
- updating a community logo (PUT, /api/communities/<community_id>/logo)
- deleting a community logo (DELETE, /api/communities/<community_id>/logo)
- creating a featured community entry (POST, /api/communities/<community_id>/featured)
- retrieving the featured community entries (GET, /api/communities/<community_id>/featured).

In addition, users who do not belong to the specified community should get permission denied when attempting to do the following:
- retrieving a community's metadata (GET, /api/communities/<community_id>)
- retrieving a community's logo (GET, /api/communities/<community_id>/logo).

Users should only see the communities that they belong to, when searching communities (GET, /api/communities), 
since all communities are expected to have hidden visibility.

Anonymous users should get permission denied when:
- searching communities (GET, /api/communities)
- searching a user's communities (GET, /api/user/communities)
- searching the featured communities (GET, /api/communities/featured).
  
## Community-membership-related requirements (ALL TESTS PASSED ON DEC. 29, 2023)

Users are not allowed to manage community membership. 

Any users who attempt the following should get permission denied:
- adding a group as a community member (POST, /api/communities/<community_id>/members)
- inviting users to join a community (POST, /api/communities/<community_id>/invitations)
- removing members from a community (DELETE, /api/communities/<community_id>/members)
- updating membership of community members (PUT, /api/communities/<community_id>/members)
- searching members of a community (GET, /api/communities/<community_id>/members)
- searching public members of a community (GET, /api/communities/<community_id>/members/public)
- searching invitations to join a community (GET, /api/communities/<community_id>/invitations).

## Shared-records-related requirements (ALL TESTS PASSED ON DEC. 30, 2023)

Anonymous users should get permission denied when trying to search records (GET, /api/records).

For any record that is shared with a given community, 
if users do not belong to that community, they should get permission denied when attempting to do the following:
- getting the metadata of the record (GET, /api/records/<record_id>) 
- getting the list of record files (GET, /api/records/<record_id>/files)
- retrieving the metadata of a record file (GET, /api/records/<record_id>/files/<filename>)
- downloading a record file (GET, /api/records/<record_id>/files/<filename>/content).