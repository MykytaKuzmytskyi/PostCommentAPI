
# PostCommentAPI

A FastAPI-based API for managing posts and comments with authentication, moderation support, and an asynchronous task queue powered by Celery. This API includes functionality for checking text toxicity when creating posts and comments, as well as an endpoint for retrieving statistics based on comment dates.

## Table of Contents
- [Project Setup](#project-setup)
- [Starting the Application](#starting-the-application)
- [API Endpoints](#api-endpoints)
- [Registration Conditions](#registration-conditions)
- [Monitoring with Flower](#monitoring-with-flower)
- [Obtaining Perspective API Key](#obtaining-perspective-api-key)

---

## Project Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/MykytaKuzmytskyi/PostCommentAPI.git
   cd PostCommentAPI
   ```
2. **Install modules and dependencies**:

    ```bash
    python -m venv venv
    venv\Scripts\activate (on Windows)
    source venv/bin/activate (on macOS)
    pip install -r requirements.txt
   ```

3. **Environment Variables**:
   - Create a `.env` file at the project root and fill in the following values:
   ```plaintext
   SQLALCHEMY_DATABASE_URL=<Your Database URL>
   USER_SECRET_KEY=<Your User Secret Key>
   PERSPECTIVE_API_KEY=<Your Perspective API Key>
   
   POSTGRES_USER=<Your POSTGRES_USER>
   POSTGRES_PASSWORD=<Your POSTGRES_PASSWORD>
   POSTGRES_DB=<Your POSTGRES_DB>
   POSTGRES_HOST=<Your POSTGRES_HOST>
   
   CELERY_BROKER_URL=<Your CELERY_BROKER_URL>
   CELERY_BACKEND_URL=<Your CELERY_BACKEND_URL>
   ```
   - Set up the `.env` file using the sample configuration below:
     ```plaintext
     USER_SECRET_KEY=J3Tmi6WCcs4KEOt7wHkMBmggPHMRCwgk
     PERSPECTIVE_API_KEY="your_perspective_api_key"
     
     POSTGRES_USER=user
     POSTGRES_PASSWORD=password
     POSTGRES_DB=postgres_db
     POSTGRES_HOST=postgres
     
     CELERY_BROKER_URL=redis://redis:6379/0
     CELERY_BACKEND_URL=redis://redis:6379/1
     ```

## Starting the Application

This project requires Docker to manage dependencies and services easily.

1. **Run the Application**:
   - Use `docker-compose` to start the application and its dependencies.
     ```bash
     docker-compose up --build
     ```
   - This starts the FastAPI server on `http://localhost:8000`, Redis, Celery, and Flower for monitoring.

2. **API Documentation**:
   - Access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Endpoints

The following main API endpoints are available:

### Post
- **GET** `/posts` - Get a list of all posts.
- **GET** `/post/{post_id}` - Get details of a specific post.
- **POST** `/posts` - Create a new post (requires authentication).
- **PATCH** `/post/{post_id}` - Update an existing post (requires authentication).
- **DELETE** `/post/{post_id}` - Delete a post (requires authentication).

### Comment
- **GET** `/post/{post_id}/comments` - Retrieve comments for a post, in a threaded format.
- **GET** `/comments/{comment_id}` - Get details of a specific comment.
- **POST** `/posts/{post_id}/comment` - Add a comment to a post (requires authentication).
- **DELETE** `/comments/{comment_id}` - Delete a comment (requires authentication).

### auth
- **POST** `/auth/register` - Register a new user.
- **POST** `/auth/login` - Authenticate an existing user.
- **POST** `/auth/logout` - Log out the authenticated user.

### Statistic
- **GET** `/comments-daily-breakdown` - Retrieve daily statistics on comments, including total and blocked comments 
within a specified date range. Parameters: date_from (string, format: YYYY-MM-DD) and date_to (string, format: YYYY-MM-DD).

Refer to the [API Documentation](http://localhost:8000/docs) for details on request/response schemas and additional query parameters.

## Registration Conditions

To successfully register a new user in the API, you must adhere to the following conditions and provide the required fields:

### Conditions for Registration
- Email must be a valid email format.
- The password must meet security requirements (minimum length, complexity, etc.).

### Required Fields
When making a registration request to the `/auth/register` endpoint, the following fields must be included in the request body:

```json
{
  "email": "userd@example.com",
  "password": "string",
  "auto_reply_enabled": false,  // Defaults to false, meaning the auto-reply feature is disabled.
  "auto_reply_delay": "00:00:10" // (format HH:MM:SS) Defaults to None if not specified, which disables the auto-reply delay.
}
```

#### Field Descriptions:
- `email` (string): The user's email address.
- `password` (string): The password for the user's account.
- `auto_reply_enabled` (boolean, optional): Indicates if auto-reply is enabled for the user (default is `false`).
- `auto_reply_delay` (string, optional): The delay for auto-reply in HH:MM:SS format (default is `00:00:10`).

## Monitoring with Flower

Flower is a real-time web-based monitoring tool for Celery. Access Flower to monitor tasks by visiting:

- **Flower**: [http://localhost:5555](http://localhost:5555)

## Obtaining Perspective API Key

The Perspective API key is required to enable content moderation features. To get an API key:

1. Visit the [Perspective API documentation](https://support.perspectiveapi.com/s/docs-get-started?language=en_US).
2. Follow the instructions to create a Google Cloud project and enable the Perspective API.
3. Once enabled, generate an API key and add it to your `.env` file:
   ```plaintext
   PERSPECTIVE_API_KEY=<Your API Key>
   ```

## Docker Services

This project includes the following services in `docker-compose.yml`:

- **FastAPI Service**: Serves the API on `http://localhost:8000`.
- **Redis**: Acts as a message broker for Celery.
- **Celery Worker**: Executes background tasks.
- **Flower**: Monitors Celery tasks on `http://localhost:5555`.

---

**Note**: Modify environment variables as needed to suit your local setup.
