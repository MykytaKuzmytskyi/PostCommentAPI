
# PostCommentAPI

A FastAPI-based API for managing posts and comments with authentication, moderation support, and an asynchronous task queue powered by Celery.

## Table of Contents
- [Project Setup](#project-setup)
- [Environment Variables](#environment-variables)
- [Starting the Application](#starting-the-application)
- [API Endpoints](#api-endpoints)
- [Monitoring with Flower](#monitoring-with-flower)
- [Obtaining Perspective API Key](#obtaining-perspective-api-key)

---

## Project Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/MykytaKuzmytskyi/PostCommentAPI.git
   cd PostCommentAPI
   ```

2. **Environment Variables**:
   - Create a `.env` file at the project root and fill in the following values:
   ```plaintext
   SQLALCHEMY_DATABASE_URL=<Your Database URL>
   USER_SECRET_KEY=<Your User Secret Key>
   PERSPECTIVE_API_KEY=<Your Perspective API Key>
   ```
   - Set up the `.env` file using the sample configuration below:
     ```plaintext
     SQLALCHEMY_DATABASE_URL=sqlite+aiosqlite:///./post_comment.db
     USER_SECRET_KEY="your_secret_key"
     PERSPECTIVE_API_KEY="your_perspective_api_key"
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

### Posts
- **GET** `/posts` - Get a list of all posts.
- **GET** `/post/{post_id}` - Get details of a specific post.
- **POST** `/posts` - Create a new post (requires authentication).
- **PATCH** `/post/{post_id}` - Update an existing post (requires authentication).
- **DELETE** `/post/{post_id}` - Delete a post (requires authentication).

### Comments
- **GET** `/post/{post_id}/comments` - Retrieve comments for a post, in a threaded format.
- **GET** `/comments/{comment_id}` - Get details of a specific comment.
- **POST** `/posts/{post_id}/comment` - Add a comment to a post (requires authentication).
- **DELETE** `/comments/{comment_id}` - Delete a comment (requires authentication).

### Users
- **POST** `/auth/register` - Register a new user.
- **POST** `/auth/login` - Authenticate an existing user.
- **GET** `/users` - List all users.

Refer to the [API Documentation](http://localhost:8000/docs) for details on request/response schemas and additional query parameters.

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
