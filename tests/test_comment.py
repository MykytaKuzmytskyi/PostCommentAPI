comment_fields = [
    "id",
    "created_at",
    "user_id",
    "content",
    "children",
    "lft",
    "rgt",
    "post_id",
    "is_blocked",
]


class TestCommentAPI:
    async def test_create_good_comment(self, auth_client, created_post):
        data = {"content": "This is a great post! Keep it up!"}
        post_id = 1
        response = await auth_client.post(f"/posts/{post_id}/comment", json=data)
        response_data = response.json()

        assert response.status_code == 201, "Failed to create good comment"
        assert "id" in response_data, "ID not found in response"
        assert response_data["content"] == data["content"], "Content mismatch"
        assert response_data["user_id"] == 1, "User ID mismatch"

        assert response_data.get("is_blocked") is False, "Good comment should not be blocked"

    async def test_create_bad_comment(self, auth_client):
        data = {"content": "You are such an idiot!"}
        post_id = 1
        response = await auth_client.post(f"/posts/{post_id}/comment", json=data)
        response_data = response.json()

        assert response.status_code == 201, "Failed to create bad comment"
        assert "id" in response_data, "ID not found in response"
        assert response_data["content"] == data["content"], "Content mismatch"
        assert response_data["user_id"] == 1, "User ID mismatch"

        assert response_data.get("is_blocked") is True, "Bad comment should be blocked"

    async def test_create_offensive_comment(self, auth_client):
        data = {"content": "This is absolutely terrible and I hate it!"}
        post_id = 1
        response = await auth_client.post(f"/posts/{post_id}/comment", json=data)
        response_data = response.json()

        assert response.status_code == 201, "Failed to create offensive comment"
        assert "id" in response_data, "ID not found in response"
        assert response_data["content"] == data["content"], "Content mismatch"
        assert response_data["user_id"] == 1, "User ID mismatch"

        assert response_data.get("is_blocked") is False, "Offensive comment should not be blocked"

    async def test_create_another_good_comment(self, auth_client):
        data = {"content": "I found this really informative!"}
        post_id = 1
        response = await auth_client.post(f"/posts/{post_id}/comment", json=data)
        response_data = response.json()

        assert response.status_code == 201, "Failed to create another good comment"
        assert "id" in response_data, "ID not found in response"
        assert response_data["content"] == data["content"], "Content mismatch"
        assert response_data["user_id"] == 1, "User ID mismatch"

        assert response_data.get("is_blocked") is False, "Another good comment should not be blocked"

    async def test_create_another_bad_comment(self, auth_client):
        data = {"content": "You are so stupid!"}
        post_id = 1
        response = await auth_client.post(f"/posts/{post_id}/comment", json=data)
        response_data = response.json()

        assert response.status_code == 201, "Failed to create another bad comment"
        assert "id" in response_data, "ID not found in response"
        assert response_data["content"] == data["content"], "Content mismatch"
        assert response_data["user_id"] == 1, "User ID mismatch"

        assert response_data.get("is_blocked") is True, "Another bad comment should be blocked"

    async def test_create_another_offensive_comment(self, auth_client):
        data = {"content": "This is the worst thing I've ever read!"}
        post_id = 1
        response = await auth_client.post(f"/posts/{post_id}/comment", json=data)
        response_data = response.json()

        assert response.status_code == 201, "Failed to create another offensive comment"
        assert "id" in response_data, "ID not found in response"
        assert response_data["content"] == data["content"], "Content mismatch"
        assert response_data["user_id"] == 1, "User ID mismatch"

        assert response_data.get("is_blocked") is False, "Another offensive comment should be not blocked"

    async def test_create_children_comment(self, auth_client):
        data = {"content": "Children comment", "parent_id": 1}
        response = await auth_client.post(f"/posts/1/comment", json=data)
        response_data = response.json()

        assert response.status_code == 201, "Failed to create comment"
        assert "id" in response_data, "ID not found in response"
        assert response_data["content"] == data["content"], "Content mismatch"
        assert response_data["user_id"] == 1, "User ID mismatch"

    async def test_get_comments_by_post_id(self, auth_client):
        post_id = 1
        response = await auth_client.get(f"/post/{post_id}/comments")
        assert response.status_code == 200, "Failed to get comments for post"

        response_data = response.json()
        assert isinstance(response_data, list), "Response should be a list"
        assert len(response_data) >= 1, "No comments found for post"

        for comment in response_data:
            for key in comment:
                assert key in comment_fields, f"Key '{key}' not found in comment"

    async def test_get_comment_children(self, auth_client):
        parent_id = 1
        response = await auth_client.get(f"/comments/{parent_id}/children")
        assert response.status_code == 200, "Failed to get child comments"
        response_data = response.json()
        assert isinstance(response_data, list), "Response should be a list"

        for comment in response_data:
            for key in comment:
                assert key in comment_fields, f"Key '{key}' not found in comment"

    async def test_delete_comment(self, auth_client):
        comment_id = 1
        response = await auth_client.delete(f"/comments/{comment_id}")
        assert response.status_code == 204, "Failed to delete comment"

        response = await auth_client.get(f"/comments/{comment_id}")
        assert response.status_code == 404, "Comment should not exist after deletion"
        assert response.json()["detail"] == f"Comment with id {comment_id} not found."

    async def test_create_comment_with_children(self, auth_client):
        data = {"content": "Parent comment"}
        post_id = 1
        response = await auth_client.post(f"/posts/{post_id}/comment", json=data)
        assert response.status_code == 201, "Failed to create parent comment"
        parent_id = response.json()["id"]

        child_data = {"content": "Child comment", "parent_id": parent_id}
        response = await auth_client.post(f"/posts/{post_id}/comment", json=child_data)
        assert response.status_code == 201, "Failed to create child comment"
        child_id = response.json()["id"]

        response = await auth_client.get(f"/comments/{parent_id}/children")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1, "Child comment not found"

        assert response_data[0]["id"] == child_id, "Child comment ID mismatch"
