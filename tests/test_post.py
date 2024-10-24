import pytest

post_fields = ["title", "content", "id", "created_at", "user_id"]


@pytest.mark.asyncio
class TestAsyncClient:
    async def test_user_me(self, auth_client):
        response = await auth_client.get("/users/me")
        assert response.status_code == 200, "Failed to fetch user data"

        user_data = response.json()
        assert "email" in user_data, "User data should contain email"
        assert (
            user_data["email"] == "string@string.com"
        ), "Email should match the logged-in user"

        response = await auth_client.get("/users")
        assert response.status_code == 200

    async def test_get_posts(self, auth_client):
        response = await auth_client.get("posts")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        for key in response_data[0]:
            assert key in post_fields

    async def test_get_post_by_id(self, auth_client):
        response = await auth_client.get("/post/1")
        assert response.status_code == 200
        for key in response.json():
            assert key in post_fields

    async def test_get_post_by_non_existent_id(self, auth_client):
        non_existent_id = 234
        response = await auth_client.get(f"/post/{non_existent_id}")
        assert response.status_code == 404
        assert (
            response.json()["detail"]
            == f"The post with id {non_existent_id} does not exist"
        )

    async def test_update_post(self, auth_client):
        data = {"title": "Updated Post", "content": "Updated content"}
        response = await auth_client.patch("/post/1", json=data)
        assert response.status_code == 200
        for key in response.json():
            assert key in post_fields
        for key in data:
            assert response.json()[key] == data[key]

    async def test_delete_post(self, auth_client):
        response = await auth_client.delete("/post/1")
        assert response.status_code == 204
        response = await auth_client.get(f"/post/1")
        assert response.status_code == 404
        assert response.json()["detail"] == f"The post with id 1 does not exist"

    async def test_create_post(self, auth_client):
        data = {"title": "New Test Post", "content": "New Test content"}
        response = await auth_client.post("/posts", json=data)
        response_data = response.json()

        assert response.status_code == 201
        assert "id" in response_data, "ID not found in response"

        for key in data:
            assert key in response_data, f"Key '{key}' not found in response"

        assert (
            response_data["title"] == data["title"]
        ), f"Expected title to be '{data['title']}', but got '{response_data['title']}'"
        assert response_data["content"] == data["content"]