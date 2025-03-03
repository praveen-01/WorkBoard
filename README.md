# WorkBoard

WorkBoard is a job posting platform built using FastAPI, allowing users to register, log in, and manage job postings securely. The platform provides authentication using JWT tokens and ensures that only authorized users can create, update, or delete their job postings.

## Features

- **User Authentication**: Sign up and log in with secure password hashing.
- **JWT-Based Authorization**: Secure API endpoints using JWT tokens.
- **Post Jobs**: Authenticated users can create job postings.
- **Update Jobs**: Users can edit only their own job postings.
- **Delete Jobs**: Users can remove job postings they have created.
- **Fetch Job Listings**: Retrieve all job postings with optional filters (title, location, type).
- **Fetch Job by ID**: Retrieve details of a specific job.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/workboard.git
   cd workboard
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   - Ensure you have a PostgreSQL or SQLite database running.
   - Modify `database.py` to connect to your database.

5. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication

- `POST /signup` – Register a new user.
  
  **Request:**
    ```
        curl http://127.0.0.1:8000/signup --header "Content-Type: application/json" \
            --data '{
            "username": "sampletestuser",
            "password": "sampletestpassword"
        }'
    ```
  **Response:**
  ```
    {
        "message":"User registered successfully"
    }
  ```

- `POST /login` – Log in and receive an access token.
  
  **Request:**
  ```
    curl --location 'http://127.0.0.1:8000/login' \
    --header 'Content-Type: application/json' \
    --data '{
        "username": "sampletestuser",
        "password": "sampletestpassword"
    }'
  ```
  
  **Response:**
  ```
    {
        "access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDA5ODIzNzEsInN1YiI6InNhbXBsZXRlc3R1c2VyIn0.1VOcC_UsU5qtraDoSGwsB1OeRmnt5c4PXGLbv62Ovys",
        "token_type":"bearer"
    }
  ```

### Jobs Management

- `GET /jobs` – Get all jobs with filtering options.
  
  **Request:**
  ```
    $ curl --location 'http://127.0.0.1:8000/jobs'
  ```
  
  **Response:**
  ```
    [
      {
          "id":1,
          "title":"engineer",
          "company":"amazon",
          "location":"hyderabad",
          "type":"full-time",
          "link":"www.bcci.com",
          "description":"it is a full tim software engineer role",
          "user_id":1,
          "created_at":"2025-03-03 09:43:34",
          "updated_at":"2025-03-03 09:43:34"
        }
    ]
  ```

- `GET /jobs/{id}` – Get job details by ID.
  **Request:**
  ```
    $ curl --location 'http://127.0.0.1:8000/jobs/1'

  ```

  **Response:**
  ```
    [
      {
          "id":1,
          "title":"engineer",
          "company":"amazon",
          "location":"hyderabad",
          "type":"full-time",
          "link":"www.bcci.com",
          "description":"it is a full tim software engineer role",
          "user_id":1,
          "created_at":"2025-03-03 09:43:34",
          "updated_at":"2025-03-03 09:43:34"
        }
    ]
  ```
- `POST /jobs/{id}` – Add a job (Only by the authenticated user).

  **Request:**
  ```
    $ curl --location 'http://127.0.0.1:8000/post-job' --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDA5ODM4NzgsInN1YiI6InNhbXBsZXRlc3R1c2VyIn0.RzT00LB4f3ZXx9RigSFTFTdQpwk8M-C-fvDnU7hVDSY' --header 'Content-Type: application/json' --data 
    '{
        "title": "engineer",
        "company": "uptycs",
        "location": "hyderabad",
        "type": "full-time",
        "link": "www.bcci.com",
        "description": "it is a full tim software engineer role"
    }'
  ```
  **Response:**
  ```
    {
        "message":"job added successfully"
    }
  ```

- `DELETE /jobs/{id}` – Delete a job (Only by the owner).
  **Request**
  ```
    $ curl --location --request DELETE 'http://127.0.0.1:8000/jobs/2' --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDA5ODQyNDcsInN1YiI6InNhbXBsZXRlc3R1c2VyIn0.z_VWqXV3wZxbe4Ncx50TCUmXE7Hv6xg92Vz3lpTWdEA'

  ```
  **Response**
  ```
    {
        "message":"job deleted successfully"
    }
  ```


## Environment Variables

Set the following environment variables:

```
SECRET_KEY=your_secret_key_here
DATABASE_URL=your_database_connection_url
```

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue.

