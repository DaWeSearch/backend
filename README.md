# DaWeSearch
## Deploy the Serverless API to AWS

1. Install Serverless

    ```
    npm install -g serverless
    ```

2. Install `serverless-python-requirements`

    ```
    npm i --save serverless-python-requirements
    ```

3. Define necessary environment variables

    Export the following environment variables:

    ```
    export MONGO_DB_USER=
    export MONGO_DB_PASS=
    export MONGO_DB_URL=
    export SPRINGER_API_KEY=
    export ELSEVIER_API_KEY=
    export JWT_SECRET_KEY= 
    export AWS_ACCESS_KEY_ID=
    export AWS_SECRET_ACCESS_KEY=
    ```
   If you are using Windows, use "set" instead of "export".
   Note that your mongo DB option params have to be URL encoded. You can use online tools such as 
   https://www.urlencoder.org/.

4. Deploy the API

    ```
    sls deploy
    ```

    Your results should look something like this:
    ```
    Serverless: Stack update finished...
    Service Information
    service: slr-backend
    stage: dev
    region: eu-central-1
    stack: slr-backend-dev
    resources: 152
    WARNING:
        You have 152 resources in your service.
        CloudFormation has a hard limit of 200 resources in a service.
        For advice on avoiding this limit, check out this link: http://bit.ly/2IiYB38.
    api keys:
        None
    endpoints:
        GET - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/query
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/review/{review_id}/query
        GET - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/results/{review_id}
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/persist/{review_id}
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/review/{review_id}/collaborator
        GET - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/users/{username}/reviews
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/persist/{review_id}/list
        DELETE - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/persist/{review_id}
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/review
        GET - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/review/{review_id}
        DELETE - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/review/{review_id}
        PUT - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/review/{review_id}
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/users
        GET - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/users/{username}
        GET - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/users
        PATCH - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/user
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/userdb
        DELETE - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/users/{username}
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/login
        DELETE - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/logout
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/logincheck
        POST - https://abcdefghi123.execute-api.eu-central-1.amazonaws.com/dev/score/{review_id}
    functions:
        dry_query: slr-backend-dev-dry_query
        new_query: slr-backend-dev-new_query
        get_persisted_results: slr-backend-dev-get_persisted_results
        persist_page_of_query: slr-backend-dev-persist_page_of_query
        add_collaborator_to_review: slr-backend-dev-add_collaborator_to_review
        get_reviews_for_user: slr-backend-dev-get_reviews_for_user
        persist_list_of_results: slr-backend-dev-persist_list_of_results
        delete_results_by_dois: slr-backend-dev-delete_results_by_dois
        add_review: slr-backend-dev-add_review
        get_review_by_id: slr-backend-dev-get_review_by_id
        delete_review: slr-backend-dev-delete_review
        update_review: slr-backend-dev-update_review
        add_user: slr-backend-dev-add_user
        get_user_by_username: slr-backend-dev-get_user_by_username
        get_users: slr-backend-dev-get_users
        update_user: slr-backend-dev-update_user
        add_api_keys: slr-backend-dev-add_api_keys
        delete_user: slr-backend-dev-delete_user
        login: slr-backend-dev-login
        logout: slr-backend-dev-logout
        check_auth: slr-backend-dev-check_auth
        update_score: slr-backend-dev-update_score
    layers:
        None

        Serverless: Removing old service artifacts from S3...
        Serverless: Run the "serverless" command to setup monitoring, troubleshooting and testing.
    ```
    
5. Enable CORS in AWS Console / API Gateway
	
	This seems to be problematic atm.
