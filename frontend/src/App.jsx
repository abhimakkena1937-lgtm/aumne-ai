import { useCallback, useEffect, useState } from "react";
import {
  createPost,
  getPosts,
  publishPost,
  submitPost,
} from "./services/api";
import "./App.css";

const FILTERS = [
  "all",
  "draft",
  "flagged",
  "approved",
  "published",
];

function App() {
  const [posts, setPosts] = useState([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [filter, setFilter] = useState("all");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Load posts from the backend.
  const loadPosts = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getPosts(
        filter === "all" ? "" : filter
      );

      setPosts(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load posts. Check whether the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadPosts();
  }, [loadPosts]);

  // Create a new draft.
  async function handleCreatePost(event) {
    event.preventDefault();

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const post = await createPost({
        title: title.trim(),
        content: content.trim(),
      });

      setTitle("");
      setContent("");
      setFilter("all");

      setMessage(
        `Draft created successfully. Post ID: ${post.id}`
      );

      await loadPosts();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to create the post."
      );
    } finally {
      setSaving(false);
    }
  }

  // Submit a draft for moderation.
  async function handleSubmit(postId) {
    setError("");
    setMessage("");

    try {
      const post = await submitPost(postId);

      if (post.status === "approved") {
        setMessage(
          `Post ${post.id} passed moderation and was approved.`
        );
      } else {
        setMessage(
          `Post ${post.id} was flagged by moderation.`
        );
      }

      await loadPosts();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to submit the post for moderation."
      );
    }
  }

  // Publish an approved post.
  async function handlePublish(postId) {
    setError("");
    setMessage("");

    try {
      await publishPost(postId);

      setMessage(
        `Post ${postId} was published successfully.`
      );

      await loadPosts();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to publish the post."
      );
    }
  }

  // Statistics for the currently visible posts.
  const stats = {
    total: posts.length,
    draft: posts.filter(
      (post) => post.status === "draft"
    ).length,
    flagged: posts.filter(
      (post) => post.status === "flagged"
    ).length,
    approved: posts.filter(
      (post) => post.status === "approved"
    ).length,
    published: posts.filter(
      (post) => post.status === "published"
    ).length,
  };

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">A</div>

          <div>
            <h1>Aumne AI</h1>
            <p>Content workspace</p>
          </div>
        </div>

        <div className="sidebar-section">
          <span className="sidebar-label">
            WORKSPACE
          </span>

          <div className="sidebar-item active">
            <span>▦</span>
            Content dashboard
          </div>

          <div className="sidebar-item">
            <span>✓</span>
            Moderation center
          </div>

          <div className="sidebar-item">
            <span>◷</span>
            Publishing workflow
          </div>
        </div>

        <div className="sidebar-bottom">
          <span className="status-indicator" />
          Local development
        </div>
      </aside>

      {/* Main Dashboard */}
      <main className="main-content">
        {/* Header */}
        <header className="topbar">
          <div>
            <p className="breadcrumb">
              Workspace / Content
            </p>

            <h2>Content dashboard</h2>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={loadPosts}
            disabled={loading}
          >
            ↻ Refresh
          </button>
        </header>

        {/* Welcome Banner */}
        <section className="welcome-section">
          <div className="welcome-text">
            <span className="eyebrow">
              AI-ASSISTED CONTENT MANAGEMENT
            </span>

            <h2>
              Create with confidence.
              <br />
              <span>Publish responsibly.</span>
            </h2>

            <p>
              Create content, review moderation results,
              and manage your publishing workflow in one
              place.
            </p>
          </div>

          <div className="welcome-illustration">
            <div className="illustration-orb">A</div>

            <div className="illustration-card card-one">
              ✦ AI review
            </div>

            <div className="illustration-card card-two">
              ✓ Content quality
            </div>
          </div>
        </section>

        {/* Notifications */}
        {error && (
          <div
            className="alert alert-error"
            role="alert"
          >
            <strong>Error:</strong> {error}
          </div>
        )}

        {message && (
          <div
            className="alert alert-success"
            role="status"
          >
            <strong>Success:</strong> {message}
          </div>
        )}

        {/* Statistics */}
        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-heading">
              <span>Total visible posts</span>
              <span className="stat-icon purple">
                #
              </span>
            </div>

            <strong>{stats.total}</strong>

            <p>Posts in current view</p>
          </div>

          <div className="stat-card">
            <div className="stat-heading">
              <span>Drafts</span>
              <span className="stat-icon gray">
                D
              </span>
            </div>

            <strong>{stats.draft}</strong>

            <p>Waiting for moderation</p>
          </div>

          <div className="stat-card">
            <div className="stat-heading">
              <span>Flagged</span>
              <span className="stat-icon orange">
                !
              </span>
            </div>

            <strong>{stats.flagged}</strong>

            <p>Require content review</p>
          </div>

          <div className="stat-card">
            <div className="stat-heading">
              <span>Published</span>
              <span className="stat-icon green">
                ✓
              </span>
            </div>

            <strong>{stats.published}</strong>

            <p>Successfully published</p>
          </div>
        </section>

        {/* Editor and Workflow */}
        <section className="workspace-grid">
          {/* Content Editor */}
          <div className="panel create-panel">
            <div className="panel-heading">
              <div>
                <span className="panel-eyebrow">
                  CONTENT EDITOR
                </span>

                <h3>Create a post</h3>

                <p>
                  Your new content starts as a draft.
                </p>
              </div>
            </div>

            <form
              className="post-form"
              onSubmit={handleCreatePost}
            >
              {/* Title Field */}
              <div className="form-group">
                <label htmlFor="post-title">
                  Post title
                </label>

                <input
                  id="post-title"
                  name="title"
                  type="text"
                  placeholder="Give your post a clear title"
                  value={title}
                  onChange={(event) =>
                    setTitle(event.target.value)
                  }
                  maxLength={200}
                  required
                />

                <div className="field-hint">
                  {title.length}/200 characters
                </div>
              </div>

              {/* Content Field */}
              <div className="form-group">
                <div className="content-label-row">
                  <label htmlFor="post-content">
                    Content
                  </label>

                  <span className="character-count">
                    {content.length} characters
                  </span>
                </div>

                <textarea
                  id="post-content"
                  name="content"
                  placeholder="Write your content here..."
                  value={content}
                  onChange={(event) =>
                    setContent(event.target.value)
                  }
                  maxLength={10000}
                  rows={8}
                  required
                />

                <div className="field-hint">
                  {content.length}/10000 characters
                </div>
              </div>

              {/* Moderation Information */}
              <div className="editor-tip">
                <span className="tip-icon">✦</span>

                <p>
                  Moderation checks content length, banned
                  words, aggressive phrases, and excessive
                  capitalization.
                </p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="primary-button full-width"
                disabled={
                  saving ||
                  !title.trim() ||
                  !content.trim()
                }
              >
                {saving
                  ? "Creating..."
                  : "+ Create draft"}
              </button>
            </form>
          </div>

          {/* Publishing Workflow */}
          <div className="panel workflow-panel">
            <div className="panel-heading">
              <div>
                <span className="panel-eyebrow">
                  HOW IT WORKS
                </span>

                <h3>Publishing workflow</h3>
              </div>
            </div>

            <div className="workflow-steps">
              <div className="workflow-step">
                <div className="step-number">01</div>

                <div>
                  <h4>Create a draft</h4>

                  <p>
                    Write and save your post before review.
                  </p>
                </div>
              </div>

              <div className="workflow-line" />

              <div className="workflow-step">
                <div className="step-number">02</div>

                <div>
                  <h4>Submit for moderation</h4>

                  <p>
                    Check content against moderation rules.
                  </p>
                </div>
              </div>

              <div className="workflow-line" />

              <div className="workflow-step">
                <div className="step-number">03</div>

                <div>
                  <h4>Review the result</h4>

                  <p>
                    Inspect flagged issues or proceed when
                    approved.
                  </p>
                </div>
              </div>

              <div className="workflow-line" />

              <div className="workflow-step">
                <div className="step-number">04</div>

                <div>
                  <h4>Publish your post</h4>

                  <p>
                    Publish content that has been approved.
                  </p>
                </div>
              </div>
            </div>

            <div className="workflow-note">
              <span>✦</span>

              <p>
                Only approved posts can be published.
              </p>
            </div>
          </div>
        </section>

        {/* Content Library */}
        <section className="panel posts-panel">
          <div className="posts-heading">
            <div>
              <span className="panel-eyebrow">
                CONTENT LIBRARY
              </span>

              <h3>Your posts</h3>

              <p>
                Review statuses and manage your content.
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={loadPosts}
              disabled={loading}
            >
              ↻ Refresh list
            </button>
          </div>

          {/* Filters */}
          <div className="filter-row">
            {FILTERS.map((item) => (
              <button
                type="button"
                key={item}
                className={`filter-button ${
                  filter === item ? "selected" : ""
                }`}
                onClick={() => {
                  setFilter(item);
                  setMessage("");
                  setError("");
                }}
              >
                {item.charAt(0).toUpperCase() +
                  item.slice(1)}
              </button>
            ))}
          </div>

          {/* Post List */}
          {loading ? (
            <div className="empty-state">
              <div className="loading-spinner" />

              <p>Loading posts...</p>
            </div>
          ) : posts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✦</div>

              <h4>No posts found</h4>

              <p>
                Create a draft or choose another filter.
              </p>
            </div>
          ) : (
            <div className="posts-list">
              {posts.map((post) => (
                <article
                  className="post-card"
                  key={post.id}
                >
                  <div className="post-main">
                    <div className="post-title-row">
                      <h4>{post.title}</h4>

                      <span
                        className={`status-badge ${post.status}`}
                      >
                        {post.status}
                      </span>
                    </div>

                    <p className="post-content">
                      {post.content}
                    </p>

                    <div className="post-metadata">
                      <span>Post #{post.id}</span>

                      <span>·</span>

                      <span>
                        {post.created_at
                          ? new Date(
                              post.created_at
                            ).toLocaleString()
                          : ""}
                      </span>
                    </div>

                    {/* Moderation Findings */}
                    {post.status === "flagged" &&
                      post.flagged_reasons?.length > 0 && (
                        <div className="flagged-reasons">
                          <strong>
                            Moderation findings
                          </strong>

                          <ul>
                            {post.flagged_reasons.map(
                              (reason, index) => (
                                <li key={index}>
                                  {reason}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                  </div>

                  {/* Post Actions */}
                  <div className="post-actions">
                    {post.status === "draft" && (
                      <button
                        type="button"
                        className="primary-button small"
                        onClick={() =>
                          handleSubmit(post.id)
                        }
                      >
                        Submit for review
                      </button>
                    )}

                    {post.status === "approved" && (
                      <button
                        type="button"
                        className="primary-button small"
                        onClick={() =>
                          handlePublish(post.id)
                        }
                      >
                        Publish
                      </button>
                    )}

                    {post.status === "flagged" && (
                      <span className="action-hint">
                        Review required
                      </span>
                    )}

                    {post.status === "published" && (
                      <span className="published-label">
                        ✓ Published
                      </span>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        {/* Footer */}
        <footer className="footer">
          <span>© 2026 Aumne AI</span>

          <span>
            Content moderation and publishing
          </span>
        </footer>
      </main>
    </div>
  );
}

export default App;