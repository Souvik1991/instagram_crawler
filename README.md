## instagram_crawler
1. To find creators from instagram using hashtags, go to <code>instagram_crawler/instagram_crawler/management/commands/get_profile_using_hashtags.py</code>

    - List down all hashtags you want to crawl under the array called <code>HASHTAGS</code>
    - Put your instagram api access token under this variable <code>TOKEN</code>
    - Now run <code>python manage.py get_profile_using_hashtags</code> to start fetching profiles
    
2. To find more instagram profile, who have certain followers count, go to <code>instagram_crawler_hashtag/instagram_crawler/management/commands/instagram_profile_data_fetch.py</code>

    - Change the <code>MIN_FOLLOWER</code> count variable value, this will determine how much minimum followers you want for the crawl
    - Change <code>BASE_SCREEN_NAME</code> and <code>BASE_PROFILE_ID (instagram_id)</code> variable value respectively, to set the initial crawl user, from where it will start fetching more profiles
    - Now run <code>python manage.py instagram_profile_data_fetch</code> to start fetching profiles
    
3. Run <code>python manage.py find_final_profile.py</code> simultaneously with <code>python manage.py get_profile_using_hashtags</code>, which keep on updating the profile data, which has been found by the step 1 code
