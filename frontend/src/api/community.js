import client from './client'

export const communityApi = {
  posts(stockCode) {
    const params = stockCode ? { stock: stockCode } : {}
    return client.get('community/posts/', { params })
  },
  post(id) {
    return client.get(`community/posts/${id}/`)
  },
  createPost(payload) {
    return client.post('community/posts/', payload)
  },
  updatePost(id, payload) {
    return client.patch(`community/posts/${id}/`, payload)
  },
  deletePost(id) {
    return client.delete(`community/posts/${id}/`)
  },
  toggleLike(id) {
    return client.post(`community/posts/${id}/like/`)
  },
  comments(postId) {
    return client.get('community/comments/', { params: { post: postId } })
  },
  createComment(postId, content) {
    return client.post('community/comments/', { post: postId, content })
  },
  updateComment(id, content) {
    return client.patch(`community/comments/${id}/`, { content })
  },
  deleteComment(id) {
    return client.delete(`community/comments/${id}/`)
  },
  toggleCommentLike(id) {
    return client.post(`community/comments/${id}/like/`)
  },
}
