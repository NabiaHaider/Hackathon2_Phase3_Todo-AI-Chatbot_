**Instructions for Configuring Deployment Platforms (T047)**

This task requires manual configuration on the respective deployment platforms. As an AI, I cannot directly perform these steps, but I can provide detailed guidance.

---

### 1. Hugging Face Space (Backend Deployment)

The backend application is designed to be deployed as a Docker image on Hugging Face Spaces. You have already created the `Dockerfile` in `backend/Dockerfile`.

**Steps to Configure on Hugging Face Spaces:**

1.  **Create a New Space:**
    *   Go to [Hugging Face Spaces](https://huggingface.co/spaces).
    *   Click on "Create new Space".
    *   Choose a Space name (e.g., `your-username/todo-ai-chatbot-backend`).
    *   Select "Docker" as the Space SDK.
    *   Choose "Public" or "Private" as desired.
    *   Click "Create Space".

2.  **Push Your Code:**
    *   Hugging Face Spaces typically connect to a Git repository. You will need to push your backend code (including the `backend/Dockerfile`, `backend/requirements.txt`, and all Python files in the `backend` directory) to a Git repository (e.g., GitHub).
    *   Connect your Hugging Face Space to this repository. Hugging Face will automatically detect the `Dockerfile` and build your application. Make sure the `backend/` directory content is at the root of the repository you link to the Space, or adjust the Dockerfile path in Space settings if it's in a subdirectory.

3.  **Configure Environment Variables (Secrets):**
    *   In your Hugging Face Space, navigate to the "Settings" tab.
    *   Scroll down to the "Repository secrets" section.
    *   Add the following environment variables as secrets. These are crucial for your backend to function correctly:
        *   `Neon_db_url`: Your Neon.tech PostgreSQL database connection string.
        *   `COHERE_API_KEY`: Your API key for Cohere.
        *   `BETTER_AUTH_SECRET`: The secret key used for JWT authentication.
        *   `BETTER_AUTH_URL`: The URL for your authentication service (if applicable, otherwise a placeholder or `null`).

4.  **Monitor Deployment:**
    *   Once configured, Hugging Face will start building and deploying your Docker image. Monitor the logs in the "Logs" tab of your Space to ensure it deploys successfully without errors.
    *   The backend will be accessible via the Space's URL (e.g., `https://your-username-todo-ai-chatbot-backend.hf.space`). You'll use this URL in your frontend configuration.

---

### 2. Vercel Project (Frontend Deployment)

The frontend application is a Next.js project and is designed to be deployed on Vercel.

**Steps to Configure on Vercel:**

1.  **Connect Your GitHub Repository:**
    *   Go to [Vercel](https://vercel.com/) and log in.
    *   Click "Add New..." -> "Project".
    *   Select your Git repository that contains the `frontend` Next.js project. If your `frontend` directory is a subdirectory, Vercel will usually detect it automatically. If not, you might need to specify the "Root Directory" in the project settings (e.g., set it to `frontend/`).

2.  **Configure Build & Development Settings (if needed):**
    *   Vercel usually auto-detects Next.js projects and sets up the build command (`next build`) and output directory correctly. You typically don't need to change these.

3.  **Configure Environment Variables:**
    *   In your Vercel project settings, navigate to "Environment Variables".
    *   Add the following environment variable:
        *   `NEXT_PUBLIC_API_BASE_URL`: This should be set to the URL of your deployed backend application on Hugging Face Spaces (e.g., `https://your-username-todo-ai-chatbot-backend.hf.space/api`). **Ensure you include `/api` at the end if that's your backend's base path for API routes.**

4.  **Deploy:**
    *   Once the repository is connected and environment variables are set, Vercel will automatically deploy your frontend. Any subsequent pushes to the configured branch will trigger new deployments.
    *   Monitor the deployment logs for any build or runtime errors.

---

**Important Notes:**

*   **Security:** Always keep your API keys and sensitive information secure. Do not hardcode them in your repository. Use the secret management features of Hugging Face and Vercel.
*   **Testing:** After deployment, thoroughly test both your backend and frontend to ensure they are communicating correctly and all features work as expected in the deployed environment.
*   **API Base URL:** Double-check that `NEXT_PUBLIC_API_BASE_URL` on Vercel correctly points to the public URL of your Hugging Face Space backend, including any `/api` path prefix if your backend uses one.
