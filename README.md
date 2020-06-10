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
    ```

4. Deploy the API

    ```
    sls deploy
    ```

    Your results should look something like this:
    ```
    Serverless: Stack update finished...
    Service Information
    service: serverless-pymongo-item-api
    stage: dev
    region: us-east-1
    stack: serverless-pymongo-item-api-dev
    resources: 28
    api keys:
      None
    endpoints:
      POST - https://0xfyi15qci.execute-api.us-east-1.amazonaws.com/dev/item
      GET - https://0xfyi15qci.execute-api.us-east-1.amazonaws.com/dev/item
      GET - https://0xfyi15qci.execute-api.us-east-1.amazonaws.com/dev/item/{id}
      DELETE - https://0xfyi15qci.execute-api.us-east-1.amazonaws.com/dev/item/{id}
    functions:
      create: serverless-pymongo-item-api-dev-create
      list: serverless-pymongo-item-api-dev-list
      get: serverless-pymongo-item-api-dev-get
      delete: serverless-pymongo-item-api-dev-delete
    layers:
      None
    Serverless: Removing old service artifacts from S3...
    Serverless: Run the "serverless" command to setup monitoring, troubleshooting and testing.
    ```
    
5. Enable CORS in AWS Console / API Gateway
	
	This seems to be problematic atm.
