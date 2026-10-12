import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const createPost = async (postData) => {
  const response = await api.post("/posts/", postData);
  return response.data;
};

export const submitPost = async (postId) => {
  const response = await api.post(
    `/posts/${postId}/submit/`
  );
  return response.data;
};

export const getPosts = async (status = "") => {
  const params = status ? { status } : {};
  const response = await api.get("/posts/", { params });
  return response.data;
};

export const getPost = async (postId) => {
  const response = await api.get(`/posts/${postId}`);
  return response.data;
};

export const publishPost = async (postId) => {
  const response = await api.patch(
    `/posts/${postId}/publish/`
  );
  return response.data;
};

export default api;