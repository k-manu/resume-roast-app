# STREAMLIT-SUPABASE-AUTH-MD

Streamlit component - https://github.com/sweatybridge/streamlit-supabase-auth.git

## How to use it in your App

### 1. Install the package
In the virtual environment you setup, install the component:
```bash
pip install streamlit-supabase-auth
```

### 2. Get your Supabase details

- Create a supabase account if you don’t already have one or login if u have one.
- Create a new project (except wherever required, use default project setup) after you login.
- Go to Authentication > SignIn/Providers > Scroll to Auth providers and check if Email is enabled.

#### Go to Project Settings > Data API
Copy:
- `SUPABASE_URL` (e.g., `https://xyzjehvhjwqws.supabase.co`)

#### Go to Project Settings > API keys
Copy:
- `SUPABASE_KEY` (anon/public key)

---

### 3. Add Secrets to `.streamlit/secrets.toml`

Create or edit this file:

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

---

## Changing Code

### 1. Add Supabase Configuration

Add this code at the top of your main application file:

```python
from streamlit_supabase_auth import login_form, logout_button
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()
```

---

### 2. Update Session State Management

Replace your existing session state initialization with:

```python
if "user_session" not in st.session_state:
    st.session_state.user_session = None
```

---

### 3. Replace Authentication UI

Replace your existing authentication UI with:

```python
def show_auth_page():
    # Supabase Authentication
    session = login_form(
        url=SUPABASE_URL,
        apiKey=SUPABASE_KEY
    )

    if session:
        st.session_state.user_session = session
        st.session_state.page = "main"  # or whatever your main page is called
        st.rerun()
```

---

### 4. Update Main Application Logic

Replace your main application logic with:

```python
def main():
    if st.session_state.page == "landing":
        show_landing_page()
    elif st.session_state.page == "auth":
        show_auth_page()
    elif st.session_state.page == "main":
        show_main_page()
    else:
        st.session_state.page = "landing"
        st.rerun()
```

---

## Step 5: Update Streamlit Secrets

1. Create a `.streamlit/secrets.toml` file with:

```toml
SUPABASE_URL = "your_project_url"
SUPABASE_KEY = "your_anon_key"
```

For an application with complex logic, give this README.md as context and generate the script for authentication